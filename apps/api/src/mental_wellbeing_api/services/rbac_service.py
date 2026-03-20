from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mental_wellbeing_api.db.base import Base
from mental_wellbeing_api.models.auth_session import AuthSession
from mental_wellbeing_api.models.organization import (
    Organization,
    OrganizationMembership,
    Role,
    RolePermission,
)


class RBACService:
    DEFAULT_ROLE_PERMISSIONS: dict[str, list[str]] = {
        "platform_admin": [
            "admin:read",
            "admin:write",
            "enterprise:read",
            "enterprise:write",
            "org:read",
            "org:write",
            "membership:read",
            "membership:write",
            "session:manage",
        ],
        "org_admin": [
            "enterprise:read",
            "enterprise:write",
            "org:read",
            "org:write",
            "membership:read",
            "membership:write",
        ],
        "reviewer": [
            "admin:read",
            "enterprise:read",
            "membership:read",
        ],
        "member": [
            "enterprise:read",
            "org:read",
            "membership:read",
        ],
    }

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def ensure_enterprise_tables(self) -> None:
        """
        Pack 1 must not break pre-existing V1-V3 tests that may run without
        a fresh alembic upgrade path for the newly introduced enterprise tables.
        This creates only the Pack 1 foundation tables if they do not exist yet.
        """
        conn = await self.session.connection()

        await conn.run_sync(
            lambda sync_conn: Base.metadata.create_all(
                bind=sync_conn,
                tables=[
                    Organization.__table__,
                    Role.__table__,
                    RolePermission.__table__,
                    OrganizationMembership.__table__,
                    AuthSession.__table__,
                ],
                checkfirst=True,
            )
        )

    async def ensure_system_roles(self) -> None:
        await self.ensure_enterprise_tables()

        existing_roles = list(
            (
                await self.session.scalars(
                    select(Role).options(selectinload(Role.permissions))
                )
            ).all()
        )
        existing_by_name = {item.name: item for item in existing_roles}

        changed = False

        for role_name, permission_keys in self.DEFAULT_ROLE_PERMISSIONS.items():
            role = existing_by_name.get(role_name)
            if role is None:
                role = Role(
                    name=role_name,
                    scope="organization" if role_name != "platform_admin" else "platform",
                    description=f"System role: {role_name}",
                    is_system=True,
                    is_active=True,
                )
                self.session.add(role)
                await self.session.flush()
                changed = True

            existing_permissions = {item.permission_key for item in role.permissions}
            for permission_key in permission_keys:
                if permission_key not in existing_permissions:
                    self.session.add(
                        RolePermission(
                            role_id=role.id,
                            permission_key=permission_key,
                        )
                    )
                    changed = True

        if changed:
            await self.session.commit()

    async def get_role_by_name(self, role_name: str) -> Role | None:
        await self.ensure_enterprise_tables()
        return await self.session.scalar(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.name == role_name)
        )

    async def list_permissions_for_role(self, role: Role | None) -> list[str]:
        if role is None:
            return []
        if not role.permissions:
            role = await self.get_role_by_name(role.name)
            if role is None:
                return []
        return sorted({item.permission_key for item in role.permissions})

    @staticmethod
    def has_permission(permission_key: str, granted_permissions: Iterable[str]) -> bool:
        return permission_key in set(granted_permissions)

    @classmethod
    def all_default_permissions(cls) -> list[str]:
        return sorted(
            {
                permission
                for permissions in cls.DEFAULT_ROLE_PERMISSIONS.values()
                for permission in permissions
            }
        )