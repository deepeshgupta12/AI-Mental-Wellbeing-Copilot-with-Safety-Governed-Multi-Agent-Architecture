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
    emotion_label = state.get("emotion_label", "reflective")
    emotion_intensity = state.get("emotion_intensity", "low")

    if risk_level == "medium":
        support_mode = "stabilize"
        support_strategy = "distress_stabilization"
        specialist_agent = "distress_stabilization"
        routing_reason = "medium-risk state prefers stabilization"
    elif intent_label == "sleep_recovery":
        support_mode = "recover"
        support_strategy = "sleep_recovery"
        specialist_agent = "sleep_recovery"
        routing_reason = "sleep recovery intent selected"
    elif intent_label == "social_support":
        support_mode = "connect"
        support_strategy = "social_support"
        specialist_agent = "social_support"
        routing_reason = "social support intent selected"
    elif intent_label == "journaling_insight":
        support_mode = "reflect"
        support_strategy = "journaling_insight"
        specialist_agent = "journaling_insight"
        routing_reason = "journaling insight intent selected"
    elif intent_label == "cognitive_reframing":
        support_mode = "reframe"
        support_strategy = "cbt_reframing"
        specialist_agent = "cbt_reframing"
        routing_reason = "cognitive reframing intent selected"
    elif intent_label == "habit_support":
        support_mode = "plan"
        support_strategy = "habit_care_plan"
        specialist_agent = "habit_care_plan"
        routing_reason = "habit support intent selected"
    elif any(hint in user_input for hint in BEHAVIORAL_ACTIVATION_HINTS):
        support_mode = "activate"
        support_strategy = "behavioral_activation"
        specialist_agent = "behavioral_activation"
        routing_reason = "behavioral activation cues detected"
    elif support_style in DIRECT_STYLE_VALUES and emotion_label in {"exhaustion", "frustration"}:
        support_mode = "activate"
        support_strategy = "behavioral_activation"
        specialist_agent = "behavioral_activation"
        routing_reason = "direct style matched with activation-friendly emotion"
    else:
        support_mode = "reflect"
        support_strategy = "reflective"
        specialist_agent = "reflective_support"
        if support_style in REFLECTIVE_STYLE_VALUES or emotion_intensity == "low":
            routing_reason = "reflective style preference matched"
        else:
            routing_reason = "default reflective pathway"

    state = {
        **state,
        "support_mode": support_mode,
        "support_strategy": support_strategy,
        "specialist_agent": specialist_agent,
        "routing_reason": routing_reason,
    }
    state = set_routing_contract(
        state,
        contract_name="v2-specialist-routing",
        intent_label=intent_label,
        support_strategy=support_strategy,
        specialist_agent=specialist_agent,
        routing_reason=routing_reason,
    )
    state = append_execution_event(
        state,
        node_name="support_mode_router",
        metadata={
            "support_mode": support_mode,
            "support_strategy": support_strategy,
            "specialist_agent": specialist_agent,
            "routing_reason": routing_reason,
        },
    )
    state = append_handoff(
        state,
        from_agent="support_mode_router",
        to_agent=specialist_agent,
        reason=routing_reason,
        contract={
            "intent_label": intent_label,
            "support_mode": support_mode,
            "support_strategy": support_strategy,
            "specialist_agent": specialist_agent,
        },
    )
    return state