export type HealthResponse = {
  status: string;
  service: string;
  version: string;
  environment: string;
};

export type DependencyStatus = "ok" | "error";

export type HealthDependenciesResponse = {
  status: "ok" | "degraded";
  dependencies: {
    postgres: {
      status: DependencyStatus;
      error: string | null;
    };
    redis: {
      status: DependencyStatus;
      error: string | null;
    };
  };
};

export type UserProfile = {
  id: string;
  user_id: string;
  display_name: string | null;
  timezone: string | null;
  support_style: string | null;
  wellbeing_goals: string | null;
  focus_areas: string | null;
  created_at: string;
  updated_at: string;
};

export type User = {
  id: string;
  email: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  profile: UserProfile | null;
};

export type AdminFlaggedSession = {
  id: string;
  user_id: string;
  severity: string;
  flag_type: string;
  summary: string | null;
  needs_review: boolean;
  is_resolved: boolean;
  reviewer_note?: string | null;
  reviewed_at?: string | null;
  resolved_at?: string | null;
  created_at: string;
};

export type AdminTraceItem = {
  id: string;
  trace_name: string;
  user_id: string | null;
  agent_name: string;
  handoff_from_agent: string | null;
  handoff_to_agent: string | null;
  input_payload_json: Record<string, unknown> | null;
  output_payload_json: Record<string, unknown> | null;
  status: string;
  latency_ms: number | null;
  notes: string | null;
  created_at: string;
};

export type AdminTraceExecutionSummary = {
  trace_name: string;
  user_id: string | null;
  status: string;
  started_at: string;
  latest_at: string;
  event_count: number;
  agents: string[];
  handoff_pairs: string[];
};

export type AdminTraceExecutionDetail = {
  trace_name: string;
  event_count: number;
  events: AdminTraceItem[];
};

export type AdminInterventionLog = {
  id: string;
  user_id: string;
  session_id: string | null;
  action_plan_id: string | null;
  intervention_type: string;
  recommendation_text: string | null;
  outcome_status: string | null;
  effectiveness_rating: number | null;
  feedback_note: string | null;
  created_at: string;
  updated_at: string;
};

export type AdminInterventionOverview = {
  total_logs: number;
  avg_effectiveness_rating: number | null;
  intervention_type_breakdown: Record<string, number>;
  outcome_status_breakdown: Record<string, number>;
  recent_logs_count: number;
};

export type AdminConfigVersion = {
  id: string;
  config_key: string;
  version_number: number;
  payload_json: Record<string, unknown>;
  change_note: string | null;
  is_active: boolean;
  created_by: string | null;
  created_at: string;
};

export type AdminConfigAudit = {
  id: string;
  config_key: string;
  from_version_id: string | null;
  to_version_id: string;
  changed_keys_json: string[] | null;
  diff_json: Record<string, unknown>;
  actor: string | null;
  created_at: string;
};

export type AdminConfigDiff = {
  config_key: string;
  from_version_id: string;
  to_version_id: string;
  from_version_number: number;
  to_version_number: number;
  changed_keys: string[];
  diff_json: Record<string, unknown>;
};

export type AdminPolicyConfig = {
  runtime_policy: Record<string, unknown>;
  prompt_registry: Record<string, unknown>;
  routing_rules: Record<string, unknown>;
};

export type AdminRoutingRulesResponse = {
  active_version: AdminConfigVersion;
  live_payload: Record<string, unknown>;
};

export type AdminFollowUpOverview = {
  total_follow_up_plans: number;
  active_scheduled_plans: number;
  completed_plans: number;
  cancelled_plans: number;
  overdue_plans: number;
  failed_follow_up_events: number;
  delivery_channel_breakdown: Record<string, number>;
  scheduler_backend_breakdown: Record<string, number>;
  upcoming_due_follow_ups: Array<Record<string, unknown>>;
  recent_completion_outcomes: Array<Record<string, unknown>>;
};

export type AdminOpsOverview = {
  total_flags: number;
  unresolved_flags: number;
  total_traces: number;
  total_intervention_logs: number;
  total_follow_up_plans: number;
  total_follow_up_events: number;
  active_config_versions: number;
  latest_runtime_executions: AdminTraceExecutionSummary[];
  intervention_overview: AdminInterventionOverview;
};

export type AdminAnalyticsOverview = {
  runtime_status_breakdown: Record<string, number>;
  specialist_agent_breakdown: Record<string, number>;
  support_strategy_breakdown: Record<string, number>;
  follow_up_status_breakdown: Record<string, number>;
  intervention_overview: AdminInterventionOverview;
};

export type AdminFlaggedSessionDetail = {
  flag: AdminFlaggedSession;
  related_traces: Array<Record<string, unknown>>;
  related_sessions: Array<Record<string, unknown>>;
};

export type AdminAuditItem = {
  event_type: string;
  entity_type: string;
  entity_id: string;
  title: string;
  details: string;
  user_id: string | null;
  occurred_at: string;
};