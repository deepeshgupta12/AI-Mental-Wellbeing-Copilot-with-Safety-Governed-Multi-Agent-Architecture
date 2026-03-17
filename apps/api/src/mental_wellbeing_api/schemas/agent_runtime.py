from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class AgentRuntimeSmokeRequest(BaseModel):
    user_input: str = Field(min_length=1, max_length=4000)
    provider: Literal["openai", "ollama", "mock"] = "mock"


class AgentRuntimeSmokeResponse(BaseModel):
    status: str
    provider: str
    structured_input: str
    reflective_response: str
    final_response: str