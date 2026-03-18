from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from mental_wellbeing_api.orchestration.state import AgentRuntimeState


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clone_list(value: list[Any] | None) -> list[Any]:
    return list(value) if value else []


def _clone_dict(value: dict[str, Any] | None) -> dict[str, Any]:
    return dict(value) if value else {}


def append_execution_event(
    state: AgentRuntimeState,
    *,
    node_name: str,
    status: str = "completed",
    metadata: dict[str, Any] | None = None,
) -> AgentRuntimeState:
    execution_path = _clone_list(state.get("execution_path"))
    node_trace = _clone_list(state.get("node_trace"))

    execution_path.append(node_name)
    node_trace.append(
        {
            "node_name": node_name,
            "status": status,
            "timestamp": utc_now_iso(),
            "metadata": metadata or {},
        }
    )

    return {
        **state,
        "current_node": node_name,
        "execution_path": execution_path,
        "node_trace": node_trace,
    }


def append_handoff(
    state: AgentRuntimeState,
    *,
    from_agent: str,
    to_agent: str,
    reason: str,
    contract: dict[str, str] | None = None,
) -> AgentRuntimeState:
    handoff_history = _clone_list(state.get("handoff_history"))
    handoff_history.append(
        {
            "from_agent": from_agent,
            "to_agent": to_agent,
            "reason": reason,
            "timestamp": utc_now_iso(),
            "contract": contract or {},
        }
    )

    return {
        **state,
        "handoff_history": handoff_history,
    }


def set_routing_contract(
    state: AgentRuntimeState,
    *,
    contract_name: str,
    intent_label: str,
    support_strategy: str,
    specialist_agent: str,
    routing_reason: str,
) -> AgentRuntimeState:
    routing_contract = _clone_dict(state.get("routing_contract"))
    routing_contract.update(
        {
            "contract_name": contract_name,
            "intent_label": intent_label,
            "support_strategy": support_strategy,
            "specialist_agent": specialist_agent,
            "routing_reason": routing_reason,
        }
    )

    return {
        **state,
        "routing_contract": routing_contract,
        "intent_label": intent_label,
        "support_strategy": support_strategy,
        "specialist_agent": specialist_agent,
        "routing_reason": routing_reason,
    }