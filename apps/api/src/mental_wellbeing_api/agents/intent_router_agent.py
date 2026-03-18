from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import (
    append_execution_event,
    append_handoff,
    set_routing_contract,
)
from mental_wellbeing_api.orchestration.state import AgentRuntimeState

SLEEP_HINTS = ["sleep", "insomnia", "rest", "night", "awake", "waking up"]
SOCIAL_HINTS = [
    "alone",
    "lonely",
    "friend",
    "friends",
    "family",
    "partner",
    "isolated",
    "who to talk to",
    "reach out",
]
HABIT_HINTS = [
    "routine",
    "habit",
    "habits",
    "consistency",
    "discipline",
    "practice",
    "self-care",
]
OVERWHELM_HINTS = ["overwhelmed", "stress", "stressed", "burnout", "heavy"]
JOURNALING_STRONG_HINTS = ["journal", "journaling", "what i wrote", "wrote in my journal"]
JOURNALING_REFLECTION_HINTS = [
    "reflect",
    "reflection",
    "reflecting",
    "process my day",
    "process what i wrote",
]
COGNITIVE_REFRAME_HINTS = [
    "always",
    "never",
    "should",
    "failure",
    "worthless",
    "ruin everything",
    "catastrophe",
    "catastrophizing",
]


def _contains_any(text: str, hints: list[str]) -> bool:
    return any(hint in text for hint in hints)


def run_intent_router_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    text = " ".join(
        [
            state.get("user_input", ""),
            state.get("structured_input", ""),
        ]
    ).lower()

    if _contains_any(text, SLEEP_HINTS):
        intent_label = "sleep_recovery"
        routing_reason = "sleep-oriented cues detected"
    elif _contains_any(text, SOCIAL_HINTS):
        intent_label = "social_support"
        routing_reason = "social-support cues detected"
    elif _contains_any(text, COGNITIVE_REFRAME_HINTS):
        intent_label = "cognitive_reframing"
        routing_reason = "cognitive distortion or self-judgment cues detected"
    elif _contains_any(text, HABIT_HINTS):
        intent_label = "habit_support"
        routing_reason = "habit-building cues detected"
    elif _contains_any(text, JOURNALING_STRONG_HINTS) or (
        _contains_any(text, JOURNALING_REFLECTION_HINTS) and "journal" in text
    ):
        intent_label = "journaling_insight"
        routing_reason = "journaling or reflection-on-writing cues detected"
    elif _contains_any(text, OVERWHELM_HINTS):
        intent_label = "stress_overwhelm"
        routing_reason = "stress or overwhelm cues detected"
    else:
        intent_label = "general_reflection"
        routing_reason = "default reflection pathway"

    state = {
        **state,
        "intent_label": intent_label,
        "routing_reason": routing_reason,
    }
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
        from_agent="intent_router",
        to_agent="support_mode_router",
        reason="intent classified for routing",
        contract={"intent_label": intent_label},
    )
    return state