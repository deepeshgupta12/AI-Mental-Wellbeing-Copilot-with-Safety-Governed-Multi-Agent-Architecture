from __future__ import annotations

from typing import Literal
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

    support_strategy: str | None = None
    session_context: str | None = None
    preference_signals: dict[str, str] = Field(default_factory=dict)
    what_helped_before: list[str] = Field(default_factory=list)
    memory_hits: list[RecalledMemoryItemResponse] = Field(default_factory=list)