from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


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
    final_response: str
    risk_level: str
    safety_flag_type: str | None = None
    safety_summary: str | None = None
    safety_override: bool

    intent_label: str | None = None
    support_strategy: str | None = None
    specialist_agent: str | None = None
    routing_reason: str | None = None
    routing_contract: dict[str, str] = Field(default_factory=dict)

    session_context: str | None = None
    preference_signals: dict[str, str] = Field(default_factory=dict)
    what_helped_before: list[str] = Field(default_factory=list)
    memory_hits: list[RecalledMemoryItemResponse] = Field(default_factory=list)

    execution_path: list[str] = Field(default_factory=list)
    node_trace: list[NodeTraceEventResponse] = Field(default_factory=list)
    handoff_history: list[HandoffEventResponse] = Field(default_factory=list)
    execution_summary: str | None = None