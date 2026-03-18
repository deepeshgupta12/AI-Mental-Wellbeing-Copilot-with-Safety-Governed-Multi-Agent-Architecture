from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import (
    append_execution_event,
    append_handoff,
    set_routing_contract,
)
from mental_wellbeing_api.orchestration.state import AgentRuntimeState

BEHAVIORAL_ACTIVATION_HINTS = [
    "stuck",
    "no motivation",
    "can't start",
    "tired",
    "exhausted",
    "avoid",
    "procrastinating",
]

DIRECT_STYLE_VALUES = {"direct", "structured", "action-oriented"}
REFLECTIVE_STYLE_VALUES = {"reflective", "soft", "calm", "minimal"}


def run_support_mode_router_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    risk_level = state.get("risk_level", "low")
    user_input = state.get("user_input", "").lower()
    preference_signals = state.get("preference_signals", {})
    support_style = preference_signals.get("support_style", "").lower()
    intent_label = state.get("intent_label", "general_reflection")

    if risk_level == "medium":
        support_strategy = "distress_stabilization"
        specialist_agent = "distress_stabilization"
        routing_reason = "medium-risk state prefers stabilization"
    elif any(hint in user_input for hint in BEHAVIORAL_ACTIVATION_HINTS):
        support_strategy = "behavioral_activation"
        specialist_agent = "behavioral_activation"
        routing_reason = "behavioral activation cues detected"
    elif intent_label in {"habit_support", "sleep_recovery"} and support_style in DIRECT_STYLE_VALUES:
        support_strategy = "behavioral_activation"
        specialist_agent = "behavioral_activation"
        routing_reason = "direct style plus action-oriented intent"
    else:
        support_strategy = "reflective"
        specialist_agent = "reflective_support"
        if support_style in REFLECTIVE_STYLE_VALUES:
            routing_reason = "reflective style preference matched"
        else:
            routing_reason = "default reflective pathway"

    state = set_routing_contract(
        state,
        contract_name="v2-routing-core",
        intent_label=intent_label,
        support_strategy=support_strategy,
        specialist_agent=specialist_agent,
        routing_reason=routing_reason,
    )
    state = append_execution_event(
        state,
        node_name="support_mode_router",
        metadata={
            "support_strategy": support_strategy,
            "specialist_agent": specialist_agent,
            "routing_reason": routing_reason,
        },
    )
    state = append_handoff(
        state,
        from_agent="intent_router",
        to_agent=specialist_agent,
        reason=routing_reason,
        contract={
            "intent_label": intent_label,
            "support_strategy": support_strategy,
            "specialist_agent": specialist_agent,
        },
    )
    return state