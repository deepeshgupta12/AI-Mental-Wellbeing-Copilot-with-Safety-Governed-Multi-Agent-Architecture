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
  preferred_support_mode?: string | null;
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

export type CreateUserPayload = {
  email: string;
  display_name?: string | null;
  timezone?: string | null;
  support_style?: string | null;
  wellbeing_goals?: string | null;
  focus_areas?: string | null;
};

export type CheckIn = {
  id: string;
  user_id: string;
  mood_score: number | null;
  stress_score: number | null;
  energy_score: number | null;
  sleep_hours: number | null;
  notes: string | null;
  created_at: string;
};

export type CreateCheckInPayload = {
  user_id: string;
  mood_score?: number | null;
  stress_score?: number | null;
  energy_score?: number | null;
  sleep_hours?: number | null;
  notes?: string | null;
};

export type JournalEntry = {
  id: string;
  user_id: string;
  title: string | null;
  content: string;
  summary?: string | null;
  emotional_tone?: string | null;
  structured_insights_json?: Record<string, unknown> | null;
  entry_type: string | null;
  created_at: string;
  updated_at?: string;
};

export type CreateJournalEntryPayload = {
  user_id: string;
  title?: string | null;
  content: string;
  entry_type?: string | null;
};

export type ConversationSession = {
  id: string;
  user_id: string;
  title: string | null;
  status: string;
  support_mode?: string | null;
  resolved_mode?: string | null;
  session_summary?: string | null;
  started_at: string;
  updated_at: string;
};

export type CreateConversationSessionPayload = {
  user_id: string;
  title?: string | null;
  status?: string;
};

export type ConversationMessage = {
  id: string;
  session_id: string;
  role: string;
  content: string;
  message_type: string;
  created_at: string;
};

export type CreateConversationMessagePayload = {
  session_id: string;
  role: string;
  content: string;
  message_type?: string;
};

export type ActionPlan = {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  timeframe: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
};

export type CreateActionPlanPayload = {
  user_id: string;
  title: string;
  description?: string | null;
  timeframe?: string | null;
};

export type MemoryItem = {
  source_type: string;
  source_id: string;
  title: string;
  summary: string;
  created_at: string;
  memory_kind?: string | null;
  importance_score?: number | null;
};

export type MemorySummary = {
  user_id: string;
  display_name: string | null;
  wellbeing_goals: string | null;
  recent_memories: MemoryItem[];
  helpful_before: string[];
  recurring_triggers: string[];
  preference_signals: Record<string, string>;
  weekly_reflection_summary: string | null;
  recent_journal_themes: string[];
};

export type TrendSummary = {
  user_id: string;
  total_check_ins: number;
  avg_mood_score: number | null;
  avg_stress_score: number | null;
  avg_energy_score: number | null;
  avg_sleep_hours: number | null;
  total_journal_entries: number;
  total_conversation_sessions: number;
  total_conversation_messages: number;
  latest_check_in_at: string | null;
  latest_journal_entry_at: string | null;
  latest_conversation_at: string | null;
  latest_snapshot_window_type?: string | null;
  latest_snapshot_created_at?: string | null;
  top_journal_themes?: string[];
  recurring_trigger_count?: number;
  support_progress_summary?: string | null;
  recurring_patterns?: string[];
  intervention_effectiveness?: Record<string, unknown>;
  trend_visualization?: Record<string, unknown>;
  trend_series: {
    mood_series: TrendSeriesPoint[];
    trigger_frequency: TriggerFrequencyPoint[];
  };
};

export type SafetyFlag = {
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

export type CreateSafetyFlagPayload = {
  user_id: string;
  severity: string;
  flag_type: string;
  summary?: string | null;
  needs_review?: boolean;
};

export type UpdateSafetyFlagPayload = {
  needs_review?: boolean;
  is_resolved?: boolean;
  reviewer_note?: string | null;
};

export type SafetyQueueItem = {
  id: string;
  user_id: string;
  severity: string;
  flag_type: string;
  summary: string | null;
  needs_review: boolean;
  is_resolved: boolean;
  created_at: string;
};

export type SafetyDashboardCounts = {
  total_flags: number;
  open_flags: number;
  resolved_flags: number;
  high_severity_open_flags: number;
};

export type SafetyEvaluationResponse = {
  risk_level: string;
  safety_flag_type: string | null;
  safety_summary: string | null;
  safety_override: boolean;
};

export type RecalledMemoryItem = {
  source_type: string;
  source_id: string;
  memory_kind: string;
  content: string;
  importance_score?: number | null;
  relevance_score?: number | null;
  created_at?: string | null;
};

export type NodeTraceEvent = {
  node_name: string;
  status: string;
  timestamp?: string | null;
  metadata: Record<string, unknown>;
};

export type HandoffEvent = {
  from_agent: string;
  to_agent: string;
  reason: string;
  timestamp?: string | null;
  contract: Record<string, string>;
};

export type FollowUpPlan = {
  id: string;
  user_id: string;
  session_id: string | null;
  action_plan_id: string | null;
  source_agent: string;
  plan_type: string;
  title: string;
  description: string | null;
  status: string;
  delivery_channel: string;
  scheduled_for: string | null;
  timezone: string | null;
  cadence_json?: Record<string, unknown> | null;
  scheduling_contract_json?: Record<string, unknown> | null;
  metadata_json?: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
};

export type AgentRuntimeSmokePayload = {
  user_input: string;
  provider?: "openai" | "ollama" | "mock";
  user_id?: string | null;
  support_track?: string | null;
};

export type AgentRuntimeSmokeResponse = {
  status: string;
  provider: string;
  structured_input: string;
  reflective_response: string;
  specialist_response?: string | null;
  final_response: string;
  risk_level: string;
  safety_flag_type?: string | null;
  safety_summary?: string | null;
  safety_override: boolean;
  support_track?: string | null;

  tone_label?: string | null;
  emotion_label?: string | null;
  emotion_intensity?: string | null;
  emotional_signals: string[];

  intent_label?: string | null;
  support_mode?: string | null;
  support_strategy?: string | null;
  specialist_agent?: string | null;
  routing_reason?: string | null;
  routing_contract: Record<string, string>;

  session_context?: string | null;
  preference_signals: Record<string, string>;
  what_helped_before: string[];
  coping_recommendations: string[];
  journaling_insights: string[];
  follow_up_suggestions: string[];

  progress_summary?: string | null;
  support_progress_summary?: string | null;
  trend_summary?: string | null;
  recurring_patterns: string[];
  intervention_effectiveness: Record<string, unknown>;
  trend_visualization: Record<string, unknown>;

  follow_up_required?: boolean;
  follow_up_plan?: Record<string, unknown>;
  follow_up_contract?: Record<string, unknown>;
  follow_up_plan_id?: string | null;
  follow_up_event_ids?: string[];
  temporal_contract?: Record<string, unknown>;
  scheduler_backend?: string | null;

  generated_follow_up_plan?: FollowUpPlan | null;
  memory_hits: RecalledMemoryItem[];

  execution_path: string[];
  node_trace: NodeTraceEvent[];
  handoff_history: HandoffEvent[];
  execution_summary?: string | null;
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

export type SupportTrack = {
  id: string;
  title: string;
  description: string;
  suggested_prompt: string;
};

export type TrendSeriesPoint = {
  timestamp: string;
  mood_score: number | null;
  stress_score: number | null;
  energy_score: number | null;
  sleep_hours: number | null;
};

export type TriggerFrequencyPoint = {
  trigger: string;
  frequency: number;
};