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
  entry_type: string | null;
  created_at: string;
  updated_at: string;
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
};

export type MemorySummary = {
  user_id: string;
  display_name: string | null;
  wellbeing_goals: string | null;
  recent_memories: MemoryItem[];
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
};

export type SafetyFlag = {
  id: string;
  user_id: string;
  severity: string;
  flag_type: string;
  summary: string | null;
  needs_review: boolean;
  is_resolved: boolean;
  reviewed_at: string | null;
  resolved_at: string | null;
  reviewer_note: string | null;
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
  review_needed_flags: number;
  resolved_flags: number;
  high_severity_open_flags: number;
};

export type AgentRuntimeSmokePayload = {
  user_input: string;
  provider?: "openai" | "ollama" | "mock";
  user_id?: string | null;
};

export type AgentRuntimeSmokeResponse = {
  status: string;
  provider: string;
  structured_input: string;
  reflective_response: string;
  final_response: string;
  risk_level: string;
  safety_flag_type: string | null;
  safety_summary: string | null;
  safety_override: boolean;
};

export type SafetyEvaluationResponse = {
  risk_level: string;
  safety_flag_type: string | null;
  safety_summary: string | null;
  safety_override: boolean;
};