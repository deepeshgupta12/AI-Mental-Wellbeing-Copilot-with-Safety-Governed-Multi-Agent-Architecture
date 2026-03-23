from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class CarePlanCreateRequest(BaseModel):
    user_id: UUID
    organization_id: UUID | None = None
    session_id: UUID | None = None
    action_plan_id: UUID | None = None
    source_agent: str
    program_key: str
    title: str
    description: str | None = None
    preferred_language: str = "en"
    timezone: str | None = None
    start_at: datetime | None = None
    cadence_json: dict[str, Any] | None = None
    sequence_json: dict[str, Any] | None = None
    metadata_json: dict[str, Any] | None = None


class CarePlanUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    current_step_key: str | None = None
    preferred_language: str | None = None
    timezone: str | None = None
    next_check_in_at: datetime | None = None
    cadence_json: dict[str, Any] | None = None
    sequence_json: dict[str, Any] | None = None
    metadata_json: dict[str, Any] | None = None
    progress_json: dict[str, Any] | None = None
    adherence_json: dict[str, Any] | None = None


class CarePlanResponse(BaseModel):
    id: str
    user_id: str
    organization_id: str | None = None
    session_id: str | None = None
    action_plan_id: str | None = None
    source_agent: str
    program_key: str
    plan_type: str
    title: str
    description: str | None = None
    status: str
    current_step_key: str | None = None
    preferred_language: str
    timezone: str | None = None
    start_at: datetime | None = None
    next_check_in_at: datetime | None = None
    last_completed_at: datetime | None = None
    cadence_json: dict[str, Any] | None = None
    sequence_json: dict[str, Any] | None = None
    progress_json: dict[str, Any] | None = None
    adherence_json: dict[str, Any] | None = None
    schedule_contract_json: dict[str, Any] | None = None
    metadata_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CarePlanEventCreateRequest(BaseModel):
    user_id: UUID
    event_type: str
    event_status: str | None = None
    step_key: str | None = None
    adherence_score: float | None = None
    notes: str | None = None
    event_payload_json: dict[str, Any] | None = None


class CarePlanEventResponse(BaseModel):
    id: str
    care_plan_id: str
    user_id: str
    event_type: str
    event_status: str | None = None
    step_key: str | None = None
    adherence_score: float | None = None
    notes: str | None = None
    event_payload_json: dict[str, Any] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CarePlanAdvanceStepRequest(BaseModel):
    next_step_key: str | None = None
    notes: str | None = None


class CarePlanLifecycleRequest(BaseModel):
    action: Literal["pause", "resume", "restart"]
    notes: str | None = None
    reset_history: bool = True


class CarePlanUserSummaryResponse(BaseModel):
    user_id: str
    total_care_plans: int = 0
    active_care_plans: int = 0
    completed_care_plans: int = 0
    avg_adherence_score: float | None = None
    due_today_count: int = 0
    by_program_key: dict[str, int] = Field(default_factory=dict)


class AdminCarePlanOverviewResponse(BaseModel):
    total_care_plans: int = 0
    active_care_plans: int = 0
    completed_care_plans: int = 0
    paused_care_plans: int = 0
    overdue_check_ins: int = 0
    at_risk_care_plans: int = 0
    upcoming_check_ins_24h: int = 0
    needs_attention_count: int = 0
    avg_adherence_score: float | None = None
    status_breakdown: dict[str, int] = Field(default_factory=dict)
    program_breakdown: dict[str, int] = Field(default_factory=dict)
    language_breakdown: dict[str, int] = Field(default_factory=dict)
    recent_events: list[CarePlanEventResponse] = Field(default_factory=list)