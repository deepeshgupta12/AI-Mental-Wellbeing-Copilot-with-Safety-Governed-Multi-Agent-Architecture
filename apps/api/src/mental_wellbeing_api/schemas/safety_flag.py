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


class SafetyFlagUpdateRequest(BaseModel):
    needs_review: bool | None = None
    is_resolved: bool | None = None
    reviewer_note: str | None = None


class SafetyFlagResponse(BaseModel):
    id: str
    user_id: str
    severity: str
    flag_type: str
    summary: str | None
    needs_review: bool
    is_resolved: bool
    reviewed_at: datetime | None
    resolved_at: datetime | None
    reviewer_note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SafetyQueueItemResponse(BaseModel):
    id: str
    user_id: str
    severity: str
    flag_type: str
    summary: str | None
    needs_review: bool
    is_resolved: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SafetyDashboardCountsResponse(BaseModel):
    total_flags: int
    open_flags: int
    review_needed_flags: int
    resolved_flags: int
    high_severity_open_flags: int