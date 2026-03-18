from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState


def run_safety_triage_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    route = "response_composer" if state.get("safety_override") else "session_context_builder"

    state = append_execution_event(
        state,
        node_name="safety_triage",
        metadata={
            "risk_level": state.get("risk_level", "low"),
            "safety_override": bool(state.get("safety_override", False)),
            "next_route": route,
        },
    )

    state = append_handoff(
        state,
        from_agent="entrypoint",
        to_agent=route,
        reason="safety gate routing decision",
        contract={
            "risk_level": state.get("risk_level", "low"),
            "safety_override": str(bool(state.get("safety_override", False))).lower(),
        },
    )
    return state