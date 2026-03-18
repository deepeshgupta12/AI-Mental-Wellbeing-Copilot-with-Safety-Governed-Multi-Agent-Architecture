from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import (
    append_execution_event,
    append_handoff,
    set_routing_contract,
)
from mental_wellbeing_api.orchestration.state import AgentRuntimeState

SLEEP_HINTS = ["sleep", "insomnia", "rest", "night", "awake"]
SOCIAL_HINTS = ["alone", "lonely", "friend", "family", "partner", "support"]
HABIT_HINTS = ["routine", "habit", "consistency", "discipline", "practice"]
OVERWHELM_HINTS = ["overwhelmed", "stress", "stressed", "burnout", "heavy"]


def run_intent_router_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    text = " ".join(
        [
            state.get("user_input", ""),
            state.get("structured_input", ""),
            state.get("session_context", ""),
        ]
    ).lower()

    if any(token in text for token in SLEEP_HINTS):
        intent_label = "sleep_recovery"
        routing_reason = "sleep-oriented cues detected"
    elif any(token in text for token in SOCIAL_HINTS):
        intent_label = "social_support"
        routing_reason = "social-support cues detected"
    elif any(token in text for token in HABIT_HINTS):
        intent_label = "habit_support"
        routing_reason = "habit-building cues detected"
    elif any(token in text for token in OVERWHELM_HINTS):
        intent_label = "stress_overwhelm"
        routing_reason = "stress or overwhelm cues detected"
    else:
        intent_label = "general_reflection"
        routing_reason = "default reflection pathway"

    state = set_routing_contract(
        state,
        contract_name="v2-routing-core",
        intent_label=intent_label,
        support_strategy=state.get("support_strategy", ""),
        specialist_agent=state.get("specialist_agent", ""),
        routing_reason=routing_reason,
    )
    state = append_execution_event(
        state,
        node_name="intent_router",
        metadata={
            "intent_label": intent_label,
            "routing_reason": routing_reason,
        },
    )
    state = append_handoff(
        state,
        from_agent="input_structuring",
        to_agent="intent_router",
        reason="structured input ready for intent classification",
        contract={"intent_label": intent_label},
    )
    return state