from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreateRequest(BaseModel):
    email: EmailStr
    display_name: str | None = None
    timezone: str | None = None
    support_style: str | None = None
    wellbeing_goals: str | None = None
    focus_areas: str | None = None


class UserProfileResponse(BaseModel):
    id: str
    user_id: str
    display_name: str | None
    timezone: str | None
    support_style: str | None
    wellbeing_goals: str | None
    focus_areas: str | None
    preferred_support_mode: str | None = None
    preference_profile_json: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    profile: UserProfileResponse | None = None

    model_config = {"from_attributes": True}


class UserLookupParams(BaseModel):
    user_id: UUID