from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EnterpriseSettingResponse(BaseModel):
    id: str
    scope_type: str
    scope_id: str
    setting_key: str
    payload_json: dict[str, Any]
    is_active: bool
    created_by: str | None = None
    updated_by: str | None = None
    change_note: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EnterpriseSettingUpdateRequest(BaseModel):
    payload_json: dict[str, Any]
    change_note: str | None = None


class ResolvedEnterpriseSettingsResponse(BaseModel):
    deployment_name: str
    organization_id: str | None = None
    deployment_settings: dict[str, Any] = Field(default_factory=dict)
    organization_settings: dict[str, Any] | None = None
    effective_settings: dict[str, Any] = Field(default_factory=dict)