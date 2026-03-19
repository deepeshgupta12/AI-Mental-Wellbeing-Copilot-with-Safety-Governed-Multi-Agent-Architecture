from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState


def run_session_context_builder_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    episodic_hits = state.get("episodic_memory_hits", [])
    semantic_hits = state.get("semantic_memory_hits", [])
    preference_signals = state.get("preference_signals", {})
    what_helped_before = state.get("what_helped_before", [])

    sections: list[str] = []

    if preference_signals:
        preference_lines = [f"- {key}: {value}" for key, value in preference_signals.items()]
        sections.append("Preference signals:\n" + "\n".join(preference_lines))

    if episodic_hits:
        lines = [
            f"- [{item.get('memory_kind', 'episodic')}] {item.get('content', '')}"
            for item in episodic_hits
        ]
        sections.append("Relevant episodic memories:\n" + "\n".join(lines))

    if semantic_hits:
        lines = [
            f"- [{item.get('memory_kind', 'semantic')}] {item.get('content', '')}"
            for item in semantic_hits
        ]
        sections.append("Relevant semantic memories:\n" + "\n".join(lines))

    if not episodic_hits and not semantic_hits:
        sections.append("Relevant prior memories:\n- No relevant prior memory was recalled.")

    if what_helped_before:
        helpful_lines = [f"- {item}" for item in what_helped_before]
        sections.append("What helped before:\n" + "\n".join(helpful_lines))

    session_context = "\n\n".join(sections)

    state = {
        **state,
        "session_context": session_context,
    }
    state = append_execution_event(
        state,
        node_name="session_context_builder",
        metadata={
            "episodic_count": len(episodic_hits),
            "semantic_count": len(semantic_hits),
            "preference_count": len(preference_signals),
            "helpful_before_count": len(what_helped_before),
        },
    )
    state = append_handoff(
        state,
        from_agent="session_context_builder",
        to_agent="input_structuring",
        reason="context assembled for downstream structuring",
    )
    return state