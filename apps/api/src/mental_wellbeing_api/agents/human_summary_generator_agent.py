from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState


def _build_human_summary(state: AgentRuntimeState) -> str:
    parts: list[str] = []

    risk_level = state.get("risk_level")
    if risk_level:
        parts.append(f"Risk level: {risk_level}")

    safety_flag_type = state.get("safety_flag_type")
    if safety_flag_type:
        parts.append(f"Safety flag: {safety_flag_type}")

    safety_summary = state.get("safety_summary")
    if safety_summary:
        parts.append(f"Safety summary: {safety_summary}")

    intent_label = state.get("intent_label")
    if intent_label:
        parts.append(f"Intent: {intent_label}")

    support_mode = state.get("support_mode")
    if support_mode:
        parts.append(f"Support mode: {support_mode}")

    if state.get("requires_human_review"):
        parts.append("Human review recommended.")

    user_input = state.get("user_input")
    if user_input:
        trimmed = user_input[:240]
        parts.append(f"User said: {trimmed}")

    return " | ".join(parts)


def run_human_summary_generator_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    summary = _build_human_summary(state)

    state = {
        **state,
        "human_summary": summary,
    }
    state = append_execution_event(
        state,
        node_name="human_summary_generator",
        metadata={
            "summary_length": len(summary),
            "requires_human_review": bool(state.get("requires_human_review", False)),
        },
    )
    state = append_handoff(
        state,
        from_agent="human_summary_generator",
        to_agent="audit_agent",
        reason="human-readable safety summary prepared",
    )
    return state