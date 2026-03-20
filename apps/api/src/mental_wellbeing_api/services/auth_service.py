from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mental_wellbeing_api.core.config import get_settings
from mental_wellbeing_api.models.auth_session import AuthSession
from mental_wellbeing_api.models.organization import Organization, OrganizationMembership, Role
from mental_wellbeing_api.models.user import User, UserProfile
from mental_wellbeing_api.schemas.auth import RequestContextResponse
from mental_wellbeing_api.services.rbac_service import RBACService


@dataclass
class RequestContext:
    is_authenticated: bool
    auth_mode: str
    auth_subject: str
    permissions: list[str]
    deployment_name: str | None = None
    user: User | None = None
    organization: Organization | None = None
    membership: OrganizationMembership | None = None
    role: Role | None = None
    session: AuthSession | None = None

    @property
    def user_id(self) -> str | None:
        return self.user.id if self.user else None

    @property
    def organization_id(self) -> str | None:
        return self.organization.id if self.organization else None

    @property
    def membership_id(self) -> str | None:
        return self.membership.id if self.membership else None

    @property
    def role_name(self) -> str | None:
        return self.role.name if self.role else None

    def to_response(self) -> RequestContextResponse:
        return RequestContextResponse(
            is_authenticated=self.is_authenticated,
            auth_mode=self.auth_mode,
            auth_subject=self.auth_subject,
            user_id=self.user_id,
            organization_id=self.organization_id,
            membership_id=self.membership_id,
            role_name=self.role_name,
            permissions=self.permissions,
            deployment_name=self.deployment_name,
            user=self.user,
            organization=self.organization,
            membership=self.membership,
        )


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.settings = get_settings()
        self.rbac = RBACService(session)

    @staticmethod
    def _slugify(value: str) -> str:
        normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
        normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
        return normalized or "default-enterprise"

    def _token_hash(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _sign(self, payload_bytes: bytes) -> str:
        signature = hmac.new(
            self.settings.auth_session_secret.encode("utf-8"),
            payload_bytes,
            hashlib.sha256,
        ).digest()
        return base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")

    def _encode_token(self, payload: dict[str, Any]) -> str:
        payload_bytes = json.dumps(
            payload,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode("utf-8").rstrip("=")
        signature = self._sign(payload_bytes)
        return f"{payload_b64}.{signature}"

    def _decode_token(self, token: str) -> dict[str, Any]:
        try:
            payload_b64, signature = token.split(".", 1)
            padded = payload_b64 + "=" * (-len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(padded.encode("utf-8"))
            expected_signature = self._sign(payload_bytes)
            if not hmac.compare_digest(signature, expected_signature):
                raise ValueError("Invalid token signature")
            payload = json.loads(payload_bytes.decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token",
            ) from exc

        exp = payload.get("exp")
        if exp is None or datetime.fromtimestamp(exp, tz=UTC) <= datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token expired",
            )
        return payload

    async def _ensure_user(self, *, email: str, display_name: str | None = None) -> User:
        existing = await self.session.scalar(
            select(User)
            .options(selectinload(User.profile))
            .where(User.email == email)
        )
        if existing is not None:
            if existing.profile is None:
                self.session.add(
                    UserProfile(
                        user_id=existing.id,
                        display_name=display_name,
                    )
                )
                await self.session.commit()
                await self.session.refresh(existing)
            elif display_name and not existing.profile.display_name:
                existing.profile.display_name = display_name
                await self.session.commit()
                await self.session.refresh(existing)
            return existing

        user = User(email=email)
        profile = UserProfile(
            user=user,
            display_name=display_name,
        )
        self.session.add_all([user, profile])
        await self.session.commit()

        created = await self.session.scalar(
            select(User)
            .options(selectinload(User.profile))
            .where(User.id == user.id)
        )
        assert created is not None
        return created

    async def _ensure_organization(self, *, name: str, slug: str) -> Organization:
        existing = await self.session.scalar(
            select(Organization).where(Organization.slug == slug)
        )
        if existing is not None:
            return existing

        org = Organization(
            name=name,
            slug=slug,
            status="active",
            is_active=True,
            settings_json={"deployment": self.settings.deployment_name},
        )
        self.session.add(org)
        await self.session.commit()
        await self.session.refresh(org)
        return org

    async def _ensure_membership(
        self,
        *,
        user: User,
        organization: Organization,
        role_name: str,
    ) -> OrganizationMembership:
        await self.rbac.ensure_system_roles()

        role = await self.rbac.get_role_by_name(role_name)
        if role is None:
            raise HTTPException(status_code=400, detail=f"Unknown role: {role_name}")

        membership = await self.session.scalar(
            select(OrganizationMembership)
            .options(
                selectinload(OrganizationMembership.organization),
                selectinload(OrganizationMembership.role).selectinload(Role.permissions),
            )
            .where(
                OrganizationMembership.organization_id == organization.id,
                OrganizationMembership.user_id == user.id,
            )
        )
        if membership is not None:
            if membership.role_id != role.id:
                membership.role_id = role.id
                await self.session.commit()
                await self.session.refresh(membership)
            return membership

        existing_default = await self.session.scalar(
            select(OrganizationMembership).where(
                OrganizationMembership.user_id == user.id,
                OrganizationMembership.is_default.is_(True),
            )
        )

        membership = OrganizationMembership(
            organization_id=organization.id,
            user_id=user.id,
            role_id=role.id,
            status="active",
            is_default=existing_default is None,
            membership_metadata_json={"seeded_by": "auth_service"},
        )
        self.session.add(membership)
        await self.session.commit()

        created = await self.session.scalar(
            select(OrganizationMembership)
            .options(
                selectinload(OrganizationMembership.organization),
                selectinload(OrganizationMembership.role).selectinload(Role.permissions),
            )
            .where(OrganizationMembership.id == membership.id)
        )
        assert created is not None
        return created

    async def create_dev_session(
        self,
        *,
        email: str,
        display_name: str | None,
        organization_name: str | None,
        organization_slug: str | None,
        role_name: str,
        auth_provider: str,
    ) -> tuple[str, AuthSession, User, Organization, OrganizationMembership, list[str]]:
        await self.rbac.ensure_system_roles()

        user = await self._ensure_user(email=email, display_name=display_name)

        resolved_org_name = organization_name or self.settings.enterprise_default_org_name
        resolved_org_slug = self._slugify(
            organization_slug or organization_name or self.settings.enterprise_default_org_slug
        )

        organization = await self._ensure_organization(
            name=resolved_org_name,
            slug=resolved_org_slug,
        )
        membership = await self._ensure_membership(
            user=user,
            organization=organization,
            role_name=role_name,
        )
        permissions = await self.rbac.list_permissions_for_role(membership.role)

        expires_at = datetime.now(UTC) + timedelta(
            minutes=self.settings.auth_access_token_ttl_minutes
        )

        session = AuthSession(
            user_id=user.id,
            organization_id=organization.id,
            membership_id=membership.id,
            token_hash="pending",
            auth_provider=auth_provider,
            session_status="active",
            expires_at=expires_at,
            session_metadata_json={
                "deployment_name": self.settings.deployment_name,
                "role_name": membership.role.name if membership.role else role_name,
            },
        )
        self.session.add(session)
        await self.session.flush()

        token_payload = {
            "sid": session.id,
            "uid": user.id,
            "oid": organization.id,
            "mid": membership.id,
            "exp": int(expires_at.timestamp()),
            "dep": self.settings.deployment_name,
        }
        access_token = self._encode_token(token_payload)
        session.token_hash = self._token_hash(access_token)

        await self.session.commit()
        await self.session.refresh(session)

        return access_token, session, user, organization, membership, permissions

    async def revoke_session(self, *, session_id: str, reason: str | None = None) -> AuthSession | None:
        await self.rbac.ensure_enterprise_tables()
        item = await self.session.get(AuthSession, session_id)
        if item is None:
            return None
        item.revoked_at = datetime.now(UTC)
        item.session_status = "revoked"
        item.revoke_reason = reason
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def _build_dev_bypass_context(self, request: Request) -> RequestContext:
        header_email = request.headers.get("X-Dev-User-Email")
        header_display_name = request.headers.get("X-Dev-Display-Name")
        header_org_slug = request.headers.get("X-Dev-Org-Slug")
        header_org_name = request.headers.get("X-Dev-Org-Name")
        header_role_name = request.headers.get(
            "X-Dev-Role",
            self.settings.enterprise_admin_role_name,
        )

        if self.settings.auth_allow_dev_headers and header_email:
            await self.rbac.ensure_system_roles()

            _, _, _, _, _ = await self.create_dev_session(
                email=header_email,
                display_name=header_display_name,
                organization_name=header_org_name,
                organization_slug=header_org_slug,
                role_name=header_role_name,
                auth_provider="dev_header_context",
            )

            user = await self.session.scalar(
                select(User)
                .options(selectinload(User.profile))
                .where(User.email == header_email)
            )
            organization = await self.session.scalar(
                select(Organization).where(
                    Organization.slug
                    == self._slugify(
                        header_org_slug
                        or header_org_name
                        or self.settings.enterprise_default_org_slug
                    )
                )
            )
            membership = await self.session.scalar(
                select(OrganizationMembership)
                .options(
                    selectinload(OrganizationMembership.organization),
                    selectinload(OrganizationMembership.role).selectinload(Role.permissions),
                )
                .where(
                    OrganizationMembership.user_id == user.id,
                    OrganizationMembership.organization_id == organization.id,
                )
            )
            permissions = await self.rbac.list_permissions_for_role(
                membership.role if membership else None
            )

            return RequestContext(
                is_authenticated=True,
                auth_mode=self.settings.auth_mode,
                auth_subject="development_header_context",
                permissions=permissions,
                deployment_name=self.settings.deployment_name,
                user=user,
                organization=organization,
                membership=membership,
                role=membership.role if membership else None,
                session=None,
            )

        return RequestContext(
            is_authenticated=True,
            auth_mode=self.settings.auth_mode,
            auth_subject="development_bypass",
            permissions=RBACService.all_default_permissions(),
            deployment_name=self.settings.deployment_name,
            user=None,
            organization=None,
            membership=None,
            role=None,
            session=None,
        )

    async def resolve_request_context(
        self,
        *,
        request: Request,
        bearer_token: str | None,
    ) -> RequestContext:
        if bearer_token:
            await self.rbac.ensure_enterprise_tables()

            payload = self._decode_token(bearer_token)
            token_hash = self._token_hash(bearer_token)

            auth_session = await self.session.scalar(
                select(AuthSession)
                .options(
                    selectinload(AuthSession.user).selectinload(User.profile),
                    selectinload(AuthSession.organization),
                    selectinload(AuthSession.membership)
                    .selectinload(OrganizationMembership.organization),
                    selectinload(AuthSession.membership)
                    .selectinload(OrganizationMembership.role)
                    .selectinload(Role.permissions),
                )
                .where(
                    AuthSession.id == payload["sid"],
                    AuthSession.token_hash == token_hash,
                )
            )
            if auth_session is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session not found",
                )
            if auth_session.revoked_at is not None or auth_session.session_status != "active":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session is no longer active",
                )
            if auth_session.expires_at <= datetime.now(UTC):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session expired",
                )

            auth_session.last_seen_at = datetime.now(UTC)
            await self.session.commit()

            membership = auth_session.membership
            role = membership.role if membership else None
            permissions = await self.rbac.list_permissions_for_role(role)

            return RequestContext(
                is_authenticated=True,
                auth_mode=self.settings.auth_mode,
                auth_subject="access_token",
                permissions=permissions,
                deployment_name=self.settings.deployment_name,
                user=auth_session.user,
                organization=auth_session.organization,
                membership=membership,
                role=role,
                session=auth_session,
            )

        if self.settings.auth_requires_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        return await self._build_dev_bypass_context(request)