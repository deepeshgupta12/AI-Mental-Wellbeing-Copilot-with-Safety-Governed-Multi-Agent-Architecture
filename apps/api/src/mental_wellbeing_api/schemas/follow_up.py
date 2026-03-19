from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class FollowUpPlanCreateRequest(BaseModel):
    user_id: UUID
    session_id: UUID | None = None
    action_plan_id: UUID | None = None
    source_agent: str
    plan_type: str
    title: str
    description: str | None = None
    delivery_channel: str = "in_app"
    scheduled_for: datetime | None = None
    timezone: str | None = None
    cadence_json: dict | None = None
    scheduling_contract_json: dict | None = None
    metadata_json: dict | None = None


class FollowUpPlanUpdateRequest(BaseModel):
    status: str | None = None
    scheduled_for: datetime | None = None
    timezone: str | None = None
    metadata_json: dict | None = None


class FollowUpPlanActionRequest(BaseModel):
    notes: str | None = None
    outcome_status: str | None = None


class FollowUpPlanResponse(BaseModel):
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


class FollowUpEventCreateRequest(BaseModel):
    follow_up_plan_id: UUID
    user_id: UUID
    event_type: str
    outcome_status: str | None = None
    notes: str | None = None
    event_payload_json: dict | None = None


class FollowUpEventResponse(BaseModel):
    id: str
    follow_up_plan_id: str
    user_id: str
    event_type: str
    outcome_status: str | None
    notes: str | None
    event_payload_json: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SchedulingContractResponse(BaseModel):
    plan_type: str
    delivery_channel: str
    scheduled_for: datetime | None = None
    timezone: str | None = None
    cadence_json: dict = Field(default_factory=dict)
    scheduling_contract_json: dict = Field(default_factory=dict)