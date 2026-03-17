from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SafetyFlagCreateRequest(BaseModel):
    user_id: UUID
    severity: str
    flag_type: str
    summary: str | None = None
    needs_review: bool = True


class SafetyFlagResponse(BaseModel):
    id: str
    user_id: str
    severity: str
    flag_type: str
    summary: str | None
    needs_review: bool
    created_at: datetime

    model_config = {"from_attributes": True}