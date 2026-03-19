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


class AdminFollowUpOverviewResponse(BaseModel):
    total_follow_up_plans: int
    active_scheduled_plans: int
    completed_plans: int
    cancelled_plans: int
    overdue_plans: int
    failed_follow_up_events: int
    delivery_channel_breakdown: dict[str, int] = Field(default_factory=dict)
    scheduler_backend_breakdown: dict[str, int] = Field(default_factory=dict)
    upcoming_due_follow_ups: list[dict[str, Any]] = Field(default_factory=list)
    recent_completion_outcomes: list[dict[str, Any]] = Field(default_factory=list)


class AdminFollowUpPlanResponse(BaseModel):
    id: str
    user_id: str
    session_id: str | None
    action_plan_id: str | None
    source_agent: str
    plan_type: str
    title: str
    description: str | None
    status: str
    delivery_channel: str
    scheduled_for: datetime | None
    timezone: str | None
    cadence_json: dict | None = None
    scheduling_contract_json: dict | None = None
    metadata_json: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminFollowUpEventResponse(BaseModel):
    id: str
    follow_up_plan_id: str
    user_id: str
    event_type: str
    outcome_status: str | None
    notes: str | None
    event_payload_json: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}