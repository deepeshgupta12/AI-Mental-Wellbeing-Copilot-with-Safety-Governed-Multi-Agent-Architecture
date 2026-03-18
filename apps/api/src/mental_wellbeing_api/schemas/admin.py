from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AdminFlaggedSessionResponse(BaseModel):
    id: str
    user_id: str
    severity: str
    flag_type: str
    summary: str | None
    needs_review: bool
    is_resolved: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminSessionLogResponse(BaseModel):
    session_id: str
    user_id: str
    title: str | None
    status: str
    started_at: datetime
    updated_at: datetime
    message_count: int
    latest_message_at: datetime | None


class AdminAuditItemResponse(BaseModel):
    event_type: str
    entity_type: str
    entity_id: str
    title: str
    details: str
    user_id: str | None
    occurred_at: datetime


class AdminPolicyConfigResponse(BaseModel):
    runtime_policy: dict
    prompt_registry: dict