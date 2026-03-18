from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event
from mental_wellbeing_api.orchestration.state import AgentRuntimeState


def run_execution_finalize_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    execution_path = state.get("execution_path", [])
    handoff_history = state.get("handoff_history", [])
    summary = (
        f"Executed {len(execution_path)} nodes with "
        f"{len(handoff_history)} handoffs. Final strategy: "
        f"{state.get('support_strategy', 'unknown')}."
    )

    state = append_execution_event(
        state,
        node_name="execution_finalize",
        metadata={
            "execution_path_length": len(execution_path),
            "handoff_count": len(handoff_history),
        },
    )

    return {
        **state,
        "execution_summary": summary,
    }