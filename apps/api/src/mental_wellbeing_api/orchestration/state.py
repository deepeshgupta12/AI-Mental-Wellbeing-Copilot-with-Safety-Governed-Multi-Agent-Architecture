from __future__ import annotations

from typing import TypedDict


class AgentRuntimeState(TypedDict, total=False):
    user_input: str
    provider: str
    structured_input: str
    reflective_response: str
    final_response: str
    risk_level: str
    safety_flag_type: str
    safety_summary: str
    safety_override: bool