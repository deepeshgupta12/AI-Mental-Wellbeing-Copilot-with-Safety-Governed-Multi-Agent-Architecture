from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from mental_wellbeing_api.schemas.follow_up import FollowUpPlanResponse


class AgentRuntimeSmokeRequest(BaseModel):
    user_input: str = Field(min_length=1, max_length=4000)
    provider: Literal["openai", "ollama", "mock"] = "mock"
    user_id: UUID | None = None


class RecalledMemoryItemResponse(BaseModel):
    source_type: str
    source_id: str
    memory_kind: str
    content: str
    importance_score: float | None = None
    relevance_score: float | None = None
    created_at: str | None = None


class NodeTraceEventResponse(BaseModel):
    node_name: str
    status: str
    timestamp: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class HandoffEventResponse(BaseModel):
    from_agent: str
    to_agent: str
    reason: str
    timestamp: str | None = None
    contract: dict[str, str] = Field(default_factory=dict)


class AgentRuntimeSmokeResponse(BaseModel):
    status: str
    provider: str
    structured_input: str
    reflective_response: str
    specialist_response: str | None = None
    final_response: str
    risk_level: str
    safety_flag_type: str | None = None
    safety_summary: str | None = None
    safety_override: bool

    tone_label: str | None = None
    emotion_label: str | None = None
    emotion_intensity: str | None = None
    emotional_signals: list[str] = Field(default_factory=list)

    intent_label: str | None = None
    support_mode: str | None = None
    support_strategy: str | None = None
    specialist_agent: str | None = None
    routing_reason: str | None = None
    routing_contract: dict[str, str] = Field(default_factory=dict)

    session_context: str | None = None
    preference_signals: dict[str, str] = Field(default_factory=dict)
    what_helped_before: list[str] = Field(default_factory=list)
    coping_recommendations: list[str] = Field(default_factory=list)
    journaling_insights: list[str] = Field(default_factory=list)
    follow_up_suggestions: list[str] = Field(default_factory=list)

    progress_summary: str | None = None
    support_progress_summary: str | None = None
    trend_summary: str | None = None
    recurring_patterns: list[str] = Field(default_factory=list)
    intervention_effectiveness: dict[str, Any] = Field(default_factory=dict)
    trend_visualization: dict[str, Any] = Field(default_factory=dict)

    support_track: str | None = None

    follow_up_required: bool = False
    follow_up_plan: dict[str, Any] = Field(default_factory=dict)
    follow_up_contract: dict[str, Any] = Field(default_factory=dict)
    follow_up_plan_id: str | None = None
    follow_up_event_ids: list[str] = Field(default_factory=list)
    temporal_contract: dict[str, Any] = Field(default_factory=dict)
    scheduler_backend: str | None = None

    generated_follow_up_plan: FollowUpPlanResponse | None = None
    memory_hits: list[RecalledMemoryItemResponse] = Field(default_factory=list)

    execution_path: list[str] = Field(default_factory=list)
    node_trace: list[NodeTraceEventResponse] = Field(default_factory=list)
    handoff_history: list[HandoffEventResponse] = Field(default_factory=list)
    execution_summary: str | None = None