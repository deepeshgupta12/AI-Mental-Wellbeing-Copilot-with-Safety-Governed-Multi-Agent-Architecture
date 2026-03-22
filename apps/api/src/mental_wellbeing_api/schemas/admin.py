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


class AdminSafetyFlowOverviewResponse(BaseModel):
    total_safety_events: int = 0
    queued_safety_events: int = 0
    in_review_safety_events: int = 0
    resolved_safety_events: int = 0
    high_risk_safety_events: int = 0
    critical_safety_events: int = 0
    alertable_trace_count: int = 0
    immutable_audit_log_count: int = 0
    decision_path_breakdown: dict[str, int] = Field(default_factory=dict)
    review_priority_breakdown: dict[str, int] = Field(default_factory=dict)
    escalation_status_breakdown: dict[str, int] = Field(default_factory=dict)
    temporal_safety_contract_status_breakdown: dict[str, int] = Field(default_factory=dict)


class AdminOpsOverviewResponse(BaseModel):
    total_flags: int
    unresolved_flags: int
    total_traces: int
    total_intervention_logs: int
    total_follow_up_plans: int
    total_follow_up_events: int
    active_config_versions: int
    latest_runtime_executions: list[AdminTraceExecutionSummaryResponse] = Field(
        default_factory=list
    )
    intervention_overview: AdminInterventionOverviewResponse
    safety_flow_overview: AdminSafetyFlowOverviewResponse = Field(
        default_factory=AdminSafetyFlowOverviewResponse
    )


class AdminAnalyticsOverviewResponse(BaseModel):
    runtime_status_breakdown: dict[str, int] = Field(default_factory=dict)
    specialist_agent_breakdown: dict[str, int] = Field(default_factory=dict)
    support_strategy_breakdown: dict[str, int] = Field(default_factory=dict)
    follow_up_status_breakdown: dict[str, int] = Field(default_factory=dict)
    intervention_overview: AdminInterventionOverviewResponse
    safety_flow_overview: AdminSafetyFlowOverviewResponse = Field(
        default_factory=AdminSafetyFlowOverviewResponse
    )


class AdminSafetyEventResponse(BaseModel):
    id: str
    user_id: str
    session_id: str | None
    safety_flag_id: str | None
    event_type: str
    severity: str
    risk_level: str
    queue_status: str
    requires_human_review: bool
    escalation_channel: str | None
    escalation_status: str
    title: str
    summary: str | None
    evidence_json: dict | None = None
    event_payload_json: dict | None = None
    detected_at: datetime
    assigned_at: datetime | None
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminSafetyReviewResponse(BaseModel):
    id: str
    safety_event_id: str
    safety_flag_id: str | None
    user_id: str
    session_id: str | None
    reviewer_id: str | None
    review_status: str
    resolution_type: str | None
    reviewer_note: str | None
    human_summary: str | None
    decision_rationale: str | None
    review_payload_json: dict | None = None
    escalation_required: bool
    escalation_status: str | None
    reviewed_at: datetime | None
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminSafetyEventDetailResponse(BaseModel):
    event: AdminSafetyEventResponse
    reviews: list[AdminSafetyReviewResponse] = Field(default_factory=list)


class AdminSafetyReviewCreateRequest(BaseModel):
    reviewer_id: str | None = None
    review_status: str
    reviewer_note: str | None = None
    human_summary: str | None = None
    decision_rationale: str | None = None
    resolution_type: str | None = None
    escalation_required: bool = False
    escalation_status: str | None = None
    review_payload_json: dict[str, Any] | None = None


class AdminReviewerDashboardResponse(BaseModel):
    total_events: int
    queued_events: int
    in_review_events: int
    resolved_events: int
    severity_breakdown: dict[str, int] = Field(default_factory=dict)
    escalation_status_breakdown: dict[str, int] = Field(default_factory=dict)
    recent_reviews: list[AdminSafetyReviewResponse] = Field(default_factory=list)


class AdminEscalationAnalyticsResponse(BaseModel):
    total_events: int
    escalated_events: int
    high_risk_events: int
    critical_events: int
    event_type_breakdown: dict[str, int] = Field(default_factory=dict)


class AdminAuditLogResponse(BaseModel):
    id: str
    event_type: str
    entity_type: str
    entity_id: str
    user_id: str | None
    session_id: str | None
    safety_event_id: str | None
    safety_review_id: str | None
    actor_type: str
    actor_id: str | None
    title: str
    details: str | None
    before_json: dict | None = None
    after_json: dict | None = None
    event_payload_json: dict | None = None
    is_immutable: bool
    occurred_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}



class AdminOrganizationSummaryResponse(BaseModel):
    id: str
    name: str
    slug: str
    status: str
    is_active: bool
    membership_count: int = 0
    active_session_count: int = 0
    latest_session_at: datetime | None = None
    latest_setting_updated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class AdminOrganizationMemberSummaryResponse(BaseModel):
    membership_id: str
    user_id: str
    email: str | None = None
    display_name: str | None = None
    role_name: str | None = None
    status: str
    is_default: bool = False
    created_at: datetime
    updated_at: datetime


class AdminOperationalKpiResponse(BaseModel):
    window_days: int
    member_count: int = 0
    active_session_count: int = 0
    session_count_window: int = 0
    safety_event_count_window: int = 0
    high_risk_safety_event_count_window: int = 0
    intervention_count_window: int = 0
    follow_up_plan_count_window: int = 0
    follow_up_event_count_window: int = 0
    review_completion_rate_pct: float = 0.0
    avg_queue_age_hours: float = 0.0
    reviewer_count: int = 0


class AdminSafetyRollupResponse(BaseModel):
    total_events: int = 0
    window_days: int = 30
    high_risk_events: int = 0
    critical_events: int = 0
    queue_status_breakdown: dict[str, int] = Field(default_factory=dict)
    risk_level_breakdown: dict[str, int] = Field(default_factory=dict)
    escalation_status_breakdown: dict[str, int] = Field(default_factory=dict)
    review_completion_rate_pct: float = 0.0
    avg_queue_age_hours: float = 0.0


class AdminInterventionRollupResponse(BaseModel):
    total_logs: int = 0
    window_days: int = 30
    avg_effectiveness_rating: float | None = None
    intervention_type_breakdown: dict[str, int] = Field(default_factory=dict)
    outcome_status_breakdown: dict[str, int] = Field(default_factory=dict)


class AdminReviewerProductivityItemResponse(BaseModel):
    reviewer_id: str
    review_count: int = 0
    resolved_count: int = 0
    escalated_count: int = 0
    completion_rate_pct: float = 0.0
    avg_review_lag_hours: float | None = None
    avg_resolution_hours: float | None = None
    latest_reviewed_at: datetime | None = None


class AdminActivityTrendPointResponse(BaseModel):
    date: str
    safety_events: int = 0
    interventions: int = 0
    follow_up_events: int = 0


class AdminArtifactDrilldownItemResponse(BaseModel):
    id: str
    scope_type: str
    scope_id: str
    artifact_kind: str
    file_name: str
    storage_provider: str
    storage_uri: str
    local_path: str | None = None
    byte_size: int
    checksum_sha256: str | None = None
    content_type: str | None = None
    created_at: datetime


class AdminEnterpriseAnalyticsOverviewResponse(BaseModel):
    scope_organization_id: str | None = None
    window_days: int = 30
    total_organizations: int
    active_organizations: int
    total_memberships: int
    membership_breakdown_by_role: dict[str, int] = Field(default_factory=dict)
    total_auth_sessions: int
    active_auth_sessions: int
    expired_auth_sessions: int
    revoked_auth_sessions: int
    organization_settings_count: int
    deployment_settings_count: int
    stored_artifact_count: int
    artifact_breakdown_by_provider: dict[str, int] = Field(default_factory=dict)
    immutable_audit_log_count: int
    total_safety_events: int
    high_risk_safety_events: int
    organizations: list[AdminOrganizationSummaryResponse] = Field(default_factory=list)
    scoped_organization: AdminOrganizationSummaryResponse | None = None
    scoped_operational_kpis: AdminOperationalKpiResponse | None = None
    scoped_safety_rollup: AdminSafetyRollupResponse | None = None
    scoped_intervention_rollup: AdminInterventionRollupResponse | None = None
    scoped_reviewer_productivity: list[AdminReviewerProductivityItemResponse] = Field(default_factory=list)
    scoped_activity_trends: list[AdminActivityTrendPointResponse] = Field(default_factory=list)


class AdminEnterpriseOrganizationDetailResponse(BaseModel):
    organization: AdminOrganizationSummaryResponse
    window_days: int = 30
    membership_breakdown_by_role: dict[str, int] = Field(default_factory=dict)
    member_summaries: list[AdminOrganizationMemberSummaryResponse] = Field(default_factory=list)
    recent_auth_sessions: list[dict[str, Any]] = Field(default_factory=list)
    safety_rollup: AdminSafetyRollupResponse = Field(default_factory=AdminSafetyRollupResponse)
    intervention_rollup: AdminInterventionRollupResponse = Field(default_factory=AdminInterventionRollupResponse)
    reviewer_productivity: list[AdminReviewerProductivityItemResponse] = Field(default_factory=list)
    operational_kpis: AdminOperationalKpiResponse = Field(default_factory=lambda: AdminOperationalKpiResponse(window_days=30))
    activity_trends: list[AdminActivityTrendPointResponse] = Field(default_factory=list)
    organization_settings: dict[str, Any] = Field(default_factory=dict)
    effective_settings: dict[str, Any] = Field(default_factory=dict)
    infrastructure_summary: dict[str, Any] = Field(default_factory=dict)
    recent_artifacts: list[AdminArtifactDrilldownItemResponse] = Field(default_factory=list)


class AdminReviewerProductivityOverviewResponse(BaseModel):
    organization_id: str | None = None
    window_days: int = 30
    reviewers: list[AdminReviewerProductivityItemResponse] = Field(default_factory=list)


class AdminIntegrationEndpointResponse(BaseModel):
    name: str
    path: str
    method: str
    category: str


class AdminIntegrationConfigFieldResponse(BaseModel):
    key: str
    label: str
    required: bool = False
    secret: bool = False
    placeholder: str | None = None


class AdminIntegrationHealthResponse(BaseModel):
    status: str
    sync_enabled: bool = False
    last_sync_at: datetime | None = None
    last_error: str | None = None


class AdminIntegrationAuditHookResponse(BaseModel):
    action: str
    event_type: str
    enabled: bool = True


class AdminIntegrationRegistryItemResponse(BaseModel):
    integration_key: str
    display_name: str
    category: str
    status: str
    adapter_type: str
    description: str
    config_placeholders: list[AdminIntegrationConfigFieldResponse] = Field(default_factory=list)
    health: AdminIntegrationHealthResponse
    audit_hooks: list[AdminIntegrationAuditHookResponse] = Field(default_factory=list)


class AdminIntegrationOverviewResponse(BaseModel):
    deployment_name: str
    organization_id: str | None = None
    auth_mode: str | None = None
    storage_provider: str
    secret_backend: str
    scheduler_backend: str
    temporal_enabled: bool
    model_provider_policy: dict[str, Any] = Field(default_factory=dict)
    feature_flags: dict[str, Any] = Field(default_factory=dict)
    integration_endpoints: list[AdminIntegrationEndpointResponse] = Field(default_factory=list)
    integration_registry: list[AdminIntegrationRegistryItemResponse] = Field(default_factory=list)
    artifact_exports_enabled: bool = True
    audit_exports_enabled: bool = True
    safety_queue_enabled: bool = True
    redacted: bool = True


class AdminIntegrationRuntimeFeedResponse(BaseModel):
    generated_at: datetime
    deployment_name: str
    organization_id: str | None = None
    capabilities: dict[str, bool] = Field(default_factory=dict)
    counts: dict[str, int] = Field(default_factory=dict)
    artifact_counts_by_scope: dict[str, int] = Field(default_factory=dict)
    model_routing: dict[str, Any] = Field(default_factory=dict)
    endpoints: list[AdminIntegrationEndpointResponse] = Field(default_factory=list)
    integration_registry: list[AdminIntegrationRegistryItemResponse] = Field(default_factory=list)
    recent_artifacts: list[AdminArtifactDrilldownItemResponse] = Field(default_factory=list)
    redacted: bool = True


class AdminIntegrationArtifactDrilldownResponse(BaseModel):
    deployment_name: str
    organization_id: str | None = None
    artifacts: list[AdminArtifactDrilldownItemResponse] = Field(default_factory=list)
    redacted: bool = True
