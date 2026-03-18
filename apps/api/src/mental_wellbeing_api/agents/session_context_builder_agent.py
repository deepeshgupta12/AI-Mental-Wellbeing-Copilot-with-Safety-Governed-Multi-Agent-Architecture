from __future__ import annotations

from mental_wellbeing_api.orchestration.state import AgentRuntimeState


def run_session_context_builder_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    recalled_items = state.get("recalled_memory_items", [])
    preference_signals = state.get("preference_signals", {})
    what_helped_before = state.get("what_helped_before", [])

    sections: list[str] = []

    if preference_signals:
        preference_lines = [f"- {key}: {value}" for key, value in preference_signals.items()]
        sections.append("Preference signals:\n" + "\n".join(preference_lines))

    if recalled_items:
        memory_lines = []
        for item in recalled_items:
            memory_kind = item.get("memory_kind", "memory")
            content = item.get("content", "")
            memory_lines.append(f"- [{memory_kind}] {content}")
        sections.append("Relevant prior memories:\n" + "\n".join(memory_lines))
    else:
        sections.append("Relevant prior memories:\n- No relevant prior memory was recalled.")

    if what_helped_before:
        helpful_lines = [f"- {item}" for item in what_helped_before]
        sections.append("What helped before:\n" + "\n".join(helpful_lines))

    return {
        **state,
        "session_context": "\n\n".join(sections),
    }