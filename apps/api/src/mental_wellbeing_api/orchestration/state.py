from __future__ import annotations

from typing import Any, TypedDict


class AgentRuntimeState(TypedDict, total=False):
    user_id: str
    user_input: str
    provider: str
    support_track: str | None

    trace_id: str
    current_node: str
    execution_path: list[str]
    node_trace: list[dict[str, Any]]
    handoff_history: list[dict[str, Any]]

    recalled_memories: list[str]
    recalled_memory_items: list[dict[str, Any]]
    episodic_memory_hits: list[dict[str, Any]]
    semantic_memory_hits: list[dict[str, Any]]

    preference_signals: dict[str, str]
    learned_preferences: dict[str, str]
    what_helped_before: list[str]
    session_context: str

    local_classifier_signals: dict[str, Any]

    tone_label: str
    emotion_label: str
    emotion_intensity: str
    emotional_signals: list[str]

    intent_label: str
    support_mode: str
    support_strategy: str
    specialist_agent: str
    routing_reason: str
    routing_contract: dict[str, str]

    structured_input: str
    reflective_response: str
    specialist_response: str
    final_response: str
    execution_summary: str

    coping_recommendations: list[str]
    journaling_insights: list[str]
    follow_up_suggestions: list[str]

    progress_summary: str
    support_progress_summary: str
    trend_summary: str
    recurring_patterns: list[str]
    intervention_effectiveness: dict[str, Any]
    trend_visualization: dict[str, Any]

    follow_up_required: bool
    follow_up_plan_type: str | None
    follow_up_plan_title: str | None
    follow_up_plan_description: str | None
    follow_up_due_at: str | None
    follow_up_delivery_channel: str | None
    follow_up_status: str | None
    follow_up_contract: dict[str, Any]
    follow_up_plan_id: str | None
    follow_up_event_ids: list[str]
    temporal_contract: dict[str, Any]
    scheduler_backend: str | None

    risk_level: str
    safety_flag_type: str
    safety_summary: str
    safety_override: bool