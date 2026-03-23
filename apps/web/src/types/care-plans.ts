export type CarePlan = {
  id: string;
  user_id: string;
  organization_id: string | null;
  session_id: string | null;
  action_plan_id: string | null;
  source_agent: string;
  program_key: string;
  plan_type: string;
  title: string;
  description: string | null;
  status: string;
  current_step_key: string | null;
  preferred_language: string;
  timezone: string | null;
  start_at: string | null;
  next_check_in_at: string | null;
  last_completed_at: string | null;
  cadence_json: Record<string, unknown> | null;
  sequence_json: {
    steps?: Array<{
      key?: string;
      order?: number;
      title?: string;
      goal?: string;
    }>;
    [key: string]: unknown;
  } | null;
  progress_json: {
    completed_step_count?: number;
    total_step_count?: number;
    completion_pct?: number;
  } | null;
  adherence_json: {
    latest_score?: number | null;
    avg_score?: number | null;
    check_in_count?: number;
  } | null;
  schedule_contract_json: Record<string, unknown> | null;
  metadata_json: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
};

export type CarePlanCreatePayload = {
  user_id: string;
  organization_id?: string | null;
  session_id?: string | null;
  action_plan_id?: string | null;
  source_agent: string;
  program_key: string;
  title: string;
  description?: string | null;
  preferred_language?: string;
  timezone?: string | null;
  start_at?: string | null;
  cadence_json?: Record<string, unknown> | null;
  sequence_json?: Record<string, unknown> | null;
  metadata_json?: Record<string, unknown> | null;
};

export type CarePlanUpdatePayload = {
  title?: string | null;
  description?: string | null;
  status?: string | null;
  current_step_key?: string | null;
  preferred_language?: string | null;
  timezone?: string | null;
  next_check_in_at?: string | null;
  cadence_json?: Record<string, unknown> | null;
  sequence_json?: Record<string, unknown> | null;
  metadata_json?: Record<string, unknown> | null;
  progress_json?: Record<string, unknown> | null;
  adherence_json?: Record<string, unknown> | null;
};

export type CarePlanEvent = {
  id: string;
  care_plan_id: string;
  user_id: string;
  event_type: string;
  event_status: string | null;
  step_key: string | null;
  adherence_score: number | null;
  notes: string | null;
  event_payload_json: Record<string, unknown> | null;
  created_at: string;
};

export type CarePlanEventCreatePayload = {
  user_id: string;
  event_type: string;
  event_status?: string | null;
  step_key?: string | null;
  adherence_score?: number | null;
  notes?: string | null;
  event_payload_json?: Record<string, unknown> | null;
};

export type CarePlanAdvancePayload = {
  next_step_key?: string | null;
  notes?: string | null;
};

export type CarePlanLifecyclePayload = {
  action: "pause" | "resume" | "restart";
  notes?: string | null;
  reset_history?: boolean;
};

export type CarePlanSummary = {
  user_id: string;
  total_care_plans: number;
  active_care_plans: number;
  completed_care_plans: number;
  avg_adherence_score: number | null;
  due_today_count: number;
  by_program_key: Record<string, number>;
};

export type AdminCarePlanOverview = {
  total_care_plans: number;
  active_care_plans: number;
  completed_care_plans: number;
  paused_care_plans: number;
  overdue_check_ins: number;
  at_risk_care_plans: number;
  upcoming_check_ins_24h: number;
  needs_attention_count: number;
  avg_adherence_score: number | null;
  status_breakdown: Record<string, number>;
  program_breakdown: Record<string, number>;
  language_breakdown: Record<string, number>;
  recent_events: CarePlanEvent[];
};