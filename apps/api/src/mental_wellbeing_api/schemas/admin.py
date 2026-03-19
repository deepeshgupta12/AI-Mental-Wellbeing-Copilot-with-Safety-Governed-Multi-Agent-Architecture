from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


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


class AdminTrendOverviewResponse(BaseModel):
    total_users_with_snapshots: int
    recent_snapshot_count: int
    weekly_reflection_snapshot_count: int
    top_recurring_patterns: list[str] = Field(default_factory=list)
    intervention_effectiveness_summary: dict[str, Any] = Field(default_factory=dict)
    recent_support_progress_summaries: list[str] = Field(default_factory=list)