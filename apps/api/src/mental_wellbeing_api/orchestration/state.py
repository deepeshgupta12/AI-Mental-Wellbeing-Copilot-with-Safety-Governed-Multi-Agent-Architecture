from __future__ import annotations

from typing import Any, TypedDict


class AgentRuntimeState(TypedDict, total=False):
    user_id: str
    user_input: str
    provider: str

    trace_id: str
    current_node: str
    execution_path: list[str]
    node_trace: list[dict[str, Any]]
    handoff_history: list[dict[str, Any]]

    recalled_memories: list[str]
    recalled_memory_items: list[dict[str, Any]]
    preference_signals: dict[str, str]
    what_helped_before: list[str]
    session_context: str

    intent_label: str
    support_strategy: str
    specialist_agent: str
    routing_reason: str
    routing_contract: dict[str, str]

    structured_input: str
    reflective_response: str
    final_response: str
    execution_summary: str

    risk_level: str
    safety_flag_type: str
    safety_summary: str
    safety_override: bool