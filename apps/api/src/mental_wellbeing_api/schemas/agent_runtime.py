from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class AgentRuntimeSmokeRequest(BaseModel):
    user_input: str = Field(min_length=1, max_length=4000)
    provider: Literal["openai", "ollama", "mock"] = "mock"
    user_id: UUID | None = None


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