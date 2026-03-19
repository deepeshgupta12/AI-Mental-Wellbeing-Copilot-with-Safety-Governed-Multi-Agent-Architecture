from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState


def run_audit_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    audit_snapshot = {
        "trace_id": state.get("trace_id"),
        "decision_path_label": state.get("decision_path_label"),
        "risk_level": state.get("risk_level"),
        "safety_override": bool(state.get("safety_override", False)),
        "requires_human_review": bool(state.get("requires_human_review", False)),
        "review_recommended": bool(state.get("review_recommended", False)),
        "intent_label": state.get("intent_label"),
        "support_mode": state.get("support_mode"),
        "support_strategy": state.get("support_strategy"),
        "specialist_agent": state.get("specialist_agent"),
        "execution_path": state.get("execution_path", []),
    }

    state = {
        **state,
        "audit_snapshot": audit_snapshot,
    }
    state = append_execution_event(
        state,
        node_name="audit_agent",
        metadata={
            "decision_path_label": state.get("decision_path_label"),
            "execution_path_length": len(state.get("execution_path", [])),
            "requires_human_review": bool(state.get("requires_human_review", False)),
        },
    )
    state = append_handoff(
        state,
        from_agent="audit_agent",
        to_agent="response_composer",
        reason="audit snapshot prepared before final response composition",
    )
    return state