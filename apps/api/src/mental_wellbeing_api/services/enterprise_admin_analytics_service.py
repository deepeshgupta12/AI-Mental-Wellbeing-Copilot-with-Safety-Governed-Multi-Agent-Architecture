from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.models.audit_log import AuditLog
from mental_wellbeing_api.models.auth_session import AuthSession
from mental_wellbeing_api.models.enterprise_setting import EnterpriseSetting
from mental_wellbeing_api.models.organization import Organization, OrganizationMembership, Role
from mental_wellbeing_api.models.safety_event import SafetyEvent
from mental_wellbeing_api.models.stored_artifact import StoredArtifact
from mental_wellbeing_api.services.enterprise_settings_service import EnterpriseSettingsService
from mental_wellbeing_api.services.infrastructure_governance_service import (
    InfrastructureGovernanceService,
)


class EnterpriseAdminAnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.enterprise_settings = EnterpriseSettingsService(session)
        self.infrastructure = InfrastructureGovernanceService(session)

    async def _organization_setting_updated_at_map(self) -> dict[str, datetime]:
        rows = (
            await self.session.execute(
                select(EnterpriseSetting.scope_id, EnterpriseSetting.updated_at)
                .where(EnterpriseSetting.scope_type == "organization")
                .order_by(desc(EnterpriseSetting.updated_at))
            )
        ).all()

        mapping: dict[str, datetime] = {}
        for scope_id, updated_at in rows:
            if scope_id and updated_at and scope_id not in mapping:
                mapping[str(scope_id)] = updated_at
        return mapping

    async def _organization_session_snapshot_map(
        self,
    ) -> dict[str, dict[str, Any]]:
        rows = (
            await self.session.execute(
                select(
                    AuthSession.organization_id,
                    func.count(AuthSession.id).label("session_count"),
                    func.max(AuthSession.last_seen_at).label("latest_seen_at"),
                )
                .where(AuthSession.organization_id.is_not(None))
                .group_by(AuthSession.organization_id)
            )
        ).all()

        payload: dict[str, dict[str, Any]] = {}
        for row in rows:
            if row.organization_id:
                payload[str(row.organization_id)] = {
                    "active_session_count": int(row.session_count or 0),
                    "latest_session_at": row.latest_seen_at,
                }
        return payload

    async def list_organizations(self, *, limit: int = 100) -> list[dict[str, Any]]:
        setting_updated_map = await self._organization_setting_updated_at_map()
        session_snapshot_map = await self._organization_session_snapshot_map()

        rows = (
            await self.session.execute(
                select(
                    Organization.id,
                    Organization.name,
                    Organization.slug,
                    Organization.status,
                    Organization.is_active,
                    Organization.created_at,
                    Organization.updated_at,
                    func.count(OrganizationMembership.id).label("membership_count"),
                )
                .outerjoin(
                    OrganizationMembership,
                    OrganizationMembership.organization_id == Organization.id,
                )
                .group_by(
                    Organization.id,
                    Organization.name,
                    Organization.slug,
                    Organization.status,
                    Organization.is_active,
                    Organization.created_at,
                    Organization.updated_at,
                )
                .order_by(desc("membership_count"), Organization.created_at.desc())
                .limit(limit)
            )
        ).all()

        payload: list[dict[str, Any]] = []
        for row in rows:
            session_snapshot = session_snapshot_map.get(str(row.id), {})
            payload.append(
                {
                    "id": str(row.id),
                    "name": row.name,
                    "slug": row.slug,
                    "status": row.status,
                    "is_active": bool(row.is_active),
                    "membership_count": int(row.membership_count or 0),
                    "active_session_count": int(
                        session_snapshot.get("active_session_count", 0)
                    ),
                    "latest_session_at": session_snapshot.get("latest_session_at"),
                    "latest_setting_updated_at": setting_updated_map.get(str(row.id)),
                    "created_at": row.created_at,
                    "updated_at": row.updated_at,
                }
            )

        return payload

    async def build_overview(self) -> dict[str, Any]:
        now = datetime.now(UTC)

        total_organizations = int(
            (await self.session.scalar(select(func.count(Organization.id)))) or 0
        )
        active_organizations = int(
            (
                await self.session.scalar(
                    select(func.count(Organization.id)).where(
                        Organization.is_active.is_(True)
                    )
                )
            )
            or 0
        )

        total_memberships = int(
            (await self.session.scalar(select(func.count(OrganizationMembership.id)))) or 0
        )

        membership_rows = (
            await self.session.execute(
                select(Role.name, func.count(OrganizationMembership.id).label("count"))
                .join(OrganizationMembership, OrganizationMembership.role_id == Role.id)
                .group_by(Role.name)
                .order_by(desc("count"))
            )
        ).all()
        membership_breakdown_by_role = {
            str(row.name): int(row.count or 0)
            for row in membership_rows
            if row.name
        }

        total_auth_sessions = int(
            (await self.session.scalar(select(func.count(AuthSession.id)))) or 0
        )
        active_auth_sessions = int(
            (
                await self.session.scalar(
                    select(func.count(AuthSession.id)).where(
                        AuthSession.session_status == "active",
                        AuthSession.revoked_at.is_(None),
                        AuthSession.expires_at > now,
                    )
                )
            )
            or 0
        )
        expired_auth_sessions = int(
            (
                await self.session.scalar(
                    select(func.count(AuthSession.id)).where(
                        AuthSession.expires_at <= now,
                    )
                )
            )
            or 0
        )
        revoked_auth_sessions = int(
            (
                await self.session.scalar(
                    select(func.count(AuthSession.id)).where(
                        (AuthSession.revoked_at.is_not(None))
                        | (AuthSession.session_status == "revoked")
                    )
                )
            )
            or 0
        )

        organization_settings_count = int(
            (
                await self.session.scalar(
                    select(func.count(EnterpriseSetting.id)).where(
                        EnterpriseSetting.scope_type == "organization",
                        EnterpriseSetting.is_active.is_(True),
                    )
                )
            )
            or 0
        )
        deployment_settings_count = int(
            (
                await self.session.scalar(
                    select(func.count(EnterpriseSetting.id)).where(
                        EnterpriseSetting.scope_type == "deployment",
                        EnterpriseSetting.is_active.is_(True),
                    )
                )
            )
            or 0
        )

        stored_artifact_count = int(
            (await self.session.scalar(select(func.count(StoredArtifact.id)))) or 0
        )
        artifact_rows = (
            await self.session.execute(
                select(
                    StoredArtifact.storage_provider,
                    func.count(StoredArtifact.id).label("count"),
                )
                .group_by(StoredArtifact.storage_provider)
                .order_by(desc("count"))
            )
        ).all()
        artifact_breakdown_by_provider = {
            str(row.storage_provider): int(row.count or 0)
            for row in artifact_rows
            if row.storage_provider
        }

        immutable_audit_log_count = int(
            (
                await self.session.scalar(
                    select(func.count(AuditLog.id)).where(
                        AuditLog.is_immutable.is_(True)
                    )
                )
            )
            or 0
        )

        total_safety_events = int(
            (await self.session.scalar(select(func.count(SafetyEvent.id)))) or 0
        )
        high_risk_safety_events = int(
            (
                await self.session.scalar(
                    select(func.count(SafetyEvent.id)).where(
                        SafetyEvent.risk_level == "high"
                    )
                )
            )
            or 0
        )

        organizations = await self.list_organizations(limit=10)

        return {
            "total_organizations": total_organizations,
            "active_organizations": active_organizations,
            "total_memberships": total_memberships,
            "membership_breakdown_by_role": membership_breakdown_by_role,
            "total_auth_sessions": total_auth_sessions,
            "active_auth_sessions": active_auth_sessions,
            "expired_auth_sessions": expired_auth_sessions,
            "revoked_auth_sessions": revoked_auth_sessions,
            "organization_settings_count": organization_settings_count,
            "deployment_settings_count": deployment_settings_count,
            "stored_artifact_count": stored_artifact_count,
            "artifact_breakdown_by_provider": artifact_breakdown_by_provider,
            "immutable_audit_log_count": immutable_audit_log_count,
            "total_safety_events": total_safety_events,
            "high_risk_safety_events": high_risk_safety_events,
            "organizations": organizations,
        }

    async def get_organization_detail(self, *, organization_id: str) -> dict[str, Any]:
        organization = await self.session.get(Organization, organization_id)
        if organization is None:
            raise ValueError("Organization not found")

        organizations = await self.list_organizations(limit=500)
        organization_summary = next(
            (item for item in organizations if item["id"] == organization_id),
            None,
        )
        if organization_summary is None:
            organization_summary = {
                "id": organization.id,
                "name": organization.name,
                "slug": organization.slug,
                "status": organization.status,
                "is_active": organization.is_active,
                "membership_count": 0,
                "active_session_count": 0,
                "latest_session_at": None,
                "latest_setting_updated_at": None,
                "created_at": organization.created_at,
                "updated_at": organization.updated_at,
            }

        membership_rows = (
            await self.session.execute(
                select(Role.name, func.count(OrganizationMembership.id).label("count"))
                .join(OrganizationMembership, OrganizationMembership.role_id == Role.id)
                .where(OrganizationMembership.organization_id == organization_id)
                .group_by(Role.name)
                .order_by(desc("count"))
            )
        ).all()
        membership_breakdown_by_role = {
            str(row.name): int(row.count or 0)
            for row in membership_rows
            if row.name
        }

        recent_auth_sessions_rows = (
            await self.session.execute(
                select(AuthSession)
                .where(AuthSession.organization_id == organization_id)
                .order_by(desc(AuthSession.created_at))
                .limit(10)
            )
        ).scalars().all()

        recent_auth_sessions = [
            {
                "id": item.id,
                "user_id": item.user_id,
                "auth_provider": item.auth_provider,
                "session_status": item.session_status,
                "issued_at": item.issued_at,
                "expires_at": item.expires_at,
                "revoked_at": item.revoked_at,
                "last_seen_at": item.last_seen_at,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
            }
            for item in recent_auth_sessions_rows
        ]

        organization_setting = await self.enterprise_settings.get_organization_settings(
            organization_id
        )
        resolved_settings = await self.enterprise_settings.resolve_settings(
            organization_id=organization_id
        )
        infrastructure_summary = await self.infrastructure.build_runtime_summary(
            organization_id=organization_id
        )

        recent_artifact_rows = (
            await self.session.execute(
                select(StoredArtifact)
                .where(StoredArtifact.scope_id == organization_id)
                .order_by(desc(StoredArtifact.created_at))
                .limit(10)
            )
        ).scalars().all()

        recent_artifacts = [
            {
                "id": item.id,
                "scope_type": item.scope_type,
                "scope_id": item.scope_id,
                "artifact_kind": item.artifact_kind,
                "file_name": item.file_name,
                "storage_provider": item.storage_provider,
                "storage_uri": item.storage_uri,
                "byte_size": item.byte_size,
                "created_at": item.created_at,
            }
            for item in recent_artifact_rows
        ]

        return {
            "organization": organization_summary,
            "membership_breakdown_by_role": membership_breakdown_by_role,
            "recent_auth_sessions": recent_auth_sessions,
            "organization_settings": organization_setting.payload_json,
            "effective_settings": resolved_settings.get("effective_settings", {}),
            "infrastructure_summary": infrastructure_summary,
            "recent_artifacts": recent_artifacts,
        }