from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field

from mental_wellbeing_api.schemas.enterprise import (
    OrganizationMembershipResponse,
    OrganizationResponse,
)
from mental_wellbeing_api.schemas.user import UserResponse


class DevSessionCreateRequest(BaseModel):
    email: EmailStr
    display_name: str | None = None
    organization_name: str | None = None
    organization_slug: str | None = None
    role_name: str = "platform_admin"
    auth_provider: str = "dev_bootstrap"


class AuthSessionResponse(BaseModel):
    id: str
    user_id: str
    organization_id: str | None = None
    membership_id: str | None = None
    auth_provider: str
    session_status: str
    issued_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None
    last_seen_at: datetime | None = None
    session_metadata_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AuthBootstrapResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: UserResponse
    organization: OrganizationResponse
    membership: OrganizationMembershipResponse
    session: AuthSessionResponse
    permissions: list[str] = Field(default_factory=list)


class RequestContextResponse(BaseModel):
    is_authenticated: bool
    auth_mode: str
    auth_subject: str
    user_id: str | None = None
    organization_id: str | None = None
    membership_id: str | None = None
    role_name: str | None = None
    permissions: list[str] = Field(default_factory=list)
    deployment_name: str | None = None
    user: UserResponse | None = None
    organization: OrganizationResponse | None = None
    membership: OrganizationMembershipResponse | None = None


class LogoutResponse(BaseModel):
    status: str
    session_id: str | None = None