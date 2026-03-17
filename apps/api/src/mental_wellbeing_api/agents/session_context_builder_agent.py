from __future__ import annotations

from mental_wellbeing_api.orchestration.state import AgentRuntimeState


def run_session_context_builder_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    recalled = state.get("recalled_memories", [])

    if not recalled:
        context = "No relevant prior memory was recalled."
    else:
        joined = "\n".join(f"- {item}" for item in recalled)
        context = f"Relevant prior memories:\n{joined}"

    return {
        **state,
        "session_context": context,
    }