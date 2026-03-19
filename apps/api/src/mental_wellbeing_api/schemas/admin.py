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
    reviewer_note: str | None = None
    reviewed_at: datetime | None = None
    resolved_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminFlaggedSessionDetailResponse(BaseModel):
    flag: AdminFlaggedSessionResponse
    related_traces: list[dict[str, Any]] = Field(default_factory=list)
    related_sessions: list[dict[str, Any]] = Field(default_factory=list)


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
    routing_rules: dict = Field(default_factory=dict)


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


class AdminTraceItemResponse(BaseModel):
    id: str
    trace_name: str
    user_id: str | None
    agent_name: str
    handoff_from_agent: str | None
    handoff_to_agent: str | None
    input_payload_json: dict | None = None
    output_payload_json: dict | None = None
    status: str
    latency_ms: float | None = None
    notes: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminTraceExecutionSummaryResponse(BaseModel):
    trace_name: str
    user_id: str | None
    status: str
    started_at: datetime
    latest_at: datetime
    event_count: int
    agents: list[str] = Field(default_factory=list)
    handoff_pairs: list[str] = Field(default_factory=list)


class AdminTraceExecutionDetailResponse(BaseModel):
    trace_name: str
    event_count: int
    events: list[AdminTraceItemResponse] = Field(default_factory=list)


class AdminInterventionLogResponse(BaseModel):
    id: str
    user_id: str
    session_id: str | None
    action_plan_id: str | None
    intervention_type: str
    recommendation_text: str | None
    outcome_status: str | None
    effectiveness_rating: float | None
    feedback_note: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminInterventionOverviewResponse(BaseModel):
    total_logs: int
    avg_effectiveness_rating: float | None = None
    intervention_type_breakdown: dict[str, int] = Field(default_factory=dict)
    outcome_status_breakdown: dict[str, int] = Field(default_factory=dict)
    recent_logs_count: int = 0


class AdminConfigVersionResponse(BaseModel):
    id: str
    config_key: str
    version_number: int
    payload_json: dict[str, Any]
    change_note: str | None = None
    is_active: bool
    created_by: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminConfigAuditResponse(BaseModel):
    id: str
    config_key: str
    from_version_id: str | None
    to_version_id: str
    changed_keys_json: list[str] | None = None
    diff_json: dict[str, Any]
    actor: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminConfigDiffResponse(BaseModel):
    config_key: str
    from_version_id: str
    to_version_id: str
    from_version_number: int
    to_version_number: int
    changed_keys: list[str] = Field(default_factory=list)
    diff_json: dict[str, Any] = Field(default_factory=dict)


class AdminConfigUpdateRequest(BaseModel):
    payload_json: dict[str, Any]
    change_note: str | None = None
    actor: str | None = "admin"


class AdminRoutingRulesResponse(BaseModel):
    active_version: AdminConfigVersionResponse
    live_payload: dict[str, Any]


class AdminOpsOverviewResponse(BaseModel):
    total_flags: int
    unresolved_flags: int
    total_traces: int
    total_intervention_logs: int
    total_follow_up_plans: int
    total_follow_up_events: int
    active_config_versions: int
    latest_runtime_executions: list[AdminTraceExecutionSummaryResponse] = Field(default_factory=list)
    intervention_overview: AdminInterventionOverviewResponse


class AdminAnalyticsOverviewResponse(BaseModel):
    runtime_status_breakdown: dict[str, int] = Field(default_factory=dict)
    specialist_agent_breakdown: dict[str, int] = Field(default_factory=dict)
    support_strategy_breakdown: dict[str, int] = Field(default_factory=dict)
    follow_up_status_breakdown: dict[str, int] = Field(default_factory=dict)
    intervention_overview: AdminInterventionOverviewResponse