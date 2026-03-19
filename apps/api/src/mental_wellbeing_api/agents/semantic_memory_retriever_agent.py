from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState


def run_semantic_memory_retriever_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    recalled_items = state.get("recalled_memory_items", [])
    semantic_hits = [
        item for item in recalled_items if item.get("memory_kind") in {"semantic", "preference"}
    ]

    state = {
        **state,
        "semantic_memory_hits": semantic_hits,
    }
    state = append_execution_event(
        state,
        node_name="semantic_memory_retriever",
        metadata={"semantic_hit_count": len(semantic_hits)},
    )
    state = append_handoff(
        state,
        from_agent="semantic_memory_retriever",
        to_agent="session_context_builder",
        reason="semantic memory hits isolated",
    )
    return state