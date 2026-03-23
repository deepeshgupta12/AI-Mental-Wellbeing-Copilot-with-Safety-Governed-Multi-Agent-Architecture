export type CarePlan = {
  id: string;
  user_id: string;
  organization_id?: string | null;
  session_id?: string | null;
  action_plan_id?: string | null;
  source_agent: string;
  program_key: string;
  plan_type: string;
  title: string;
  description?: string | null;
  status: string;
  current_step_key?: string | null;
  preferred_language: string;
  timezone?: string | null;
  start_at?: string | null;
  next_check_in_at?: string | null;
  last_completed_at?: string | null;
  cadence_json?: Record<string, unknown> | null;
  sequence_json?: Record<string, unknown> | null;
  progress_json?: Record<string, unknown> | null;
  adherence_json?: Record<string, unknown> | null;
  schedule_contract_json?: Record<string, unknown> | null;
  metadata_json?: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
};

export type CarePlanEvent = {
  id: string;
  care_plan_id: string;
  user_id: string;
  event_type: string;
  event_status?: string | null;
  step_key?: string | null;
  adherence_score?: number | null;
  notes?: string | null;
  event_payload_json?: Record<string, unknown> | null;
  created_at: string;
};

export type CarePlanUserSummary = {
  user_id: string;
  total_care_plans: number;
  active_care_plans: number;
  completed_care_plans: number;
  avg_adherence_score?: number | null;
  due_today_count: number;
  by_program_key: Record<string, number>;
};

export type AdminCarePlanOverview = {
  total_care_plans: number;
  active_care_plans: number;
  completed_care_plans: number;
  paused_care_plans: number;
  overdue_check_ins: number;
  avg_adherence_score?: number | null;
  status_breakdown: Record<string, number>;
  program_breakdown: Record<string, number>;
  language_breakdown: Record<string, number>;
  recent_events: CarePlanEvent[];
};