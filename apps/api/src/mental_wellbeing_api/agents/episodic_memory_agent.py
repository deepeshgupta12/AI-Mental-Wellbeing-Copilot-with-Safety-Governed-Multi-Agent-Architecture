from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState


def run_episodic_memory_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    recalled_items = state.get("recalled_memory_items", [])
    episodic_hits = [
        item for item in recalled_items if item.get("memory_kind") in {"episodic", "helpful_strategy"}
    ]

    state = {
        **state,
        "episodic_memory_hits": episodic_hits,
    }
    state = append_execution_event(
        state,
        node_name="episodic_memory",
        metadata={"episodic_hit_count": len(episodic_hits)},
    )
    state = append_handoff(
        state,
        from_agent="episodic_memory",
        to_agent="semantic_memory_retriever",
        reason="episodic memory hits isolated",
    )
    return state