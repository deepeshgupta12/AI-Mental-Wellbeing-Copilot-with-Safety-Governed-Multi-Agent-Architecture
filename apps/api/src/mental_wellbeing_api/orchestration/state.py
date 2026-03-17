from __future__ import annotations

from typing import TypedDict


class AgentRuntimeState(TypedDict, total=False):
    user_input: str
    provider: str
    structured_input: str
    reflective_response: str
    final_response: str