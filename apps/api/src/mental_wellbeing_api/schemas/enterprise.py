from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class OrganizationResponse(BaseModel):
    id: str
    name: str
    slug: str
    status: str
    is_active: bool
    settings_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RolePermissionResponse(BaseModel):
    id: str
    permission_key: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RoleResponse(BaseModel):
    id: str
    name: str
    scope: str
    description: str | None = None
    is_system: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    permissions: list[RolePermissionResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class OrganizationMembershipResponse(BaseModel):
    id: str
    organization_id: str
    user_id: str
    role_id: str
    status: str
    is_default: bool
    membership_metadata_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime
    organization: OrganizationResponse | None = None
    role: RoleResponse | None = None

    model_config = {"from_attributes": True}