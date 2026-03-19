from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import (
    append_execution_event,
    append_handoff,
    set_routing_contract,
)
from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_routing_rules, load_runtime_policy


def run_support_mode_router_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    risk_level = state.get("risk_level", "low")
    user_input = state.get("user_input", "").lower()
    preference_signals = state.get("preference_signals", {})
    support_style = preference_signals.get("support_style", "").lower()
    intent_label = state.get("intent_label", "general_reflection")
    emotion_label = state.get("emotion_label", "reflective")
    emotion_intensity = state.get("emotion_intensity", "low")

    policy = load_runtime_policy()
    routing_policy = policy.get("routing", {}) if isinstance(policy, dict) else {}
    rules = load_routing_rules()
    support_rules = rules.get("support_mode_router", {}) if isinstance(rules, dict) else {}

    behavioral_activation_hints = list(
        support_rules.get(
            "behavioral_activation_hints",
            routing_policy.get("behavioral_activation_hints", []),
        )
    )
    direct_style_values = set(support_rules.get("direct_style_values", ["direct", "structured", "action-oriented"]))
    reflective_style_values = set(support_rules.get("reflective_style_values", ["reflective", "soft", "calm", "minimal"]))
    contract_name = str(routing_policy.get("contract_name", "v2-routing-core"))

    if risk_level == "medium":
        support_mode = "stabilize"
        support_strategy = str(routing_policy.get("medium_risk_strategy", "distress_stabilization"))
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
    elif any(hint in user_input for hint in behavioral_activation_hints):
        support_mode = "activate"
        support_strategy = "behavioral_activation"
        specialist_agent = "behavioral_activation"
        routing_reason = "behavioral activation cues detected"
    elif support_style in direct_style_values and emotion_label in {"exhaustion", "frustration"}:
        support_mode = "activate"
        support_strategy = "behavioral_activation"
        specialist_agent = "behavioral_activation"
        routing_reason = "direct style matched with activation-friendly emotion"
    else:
        support_mode = "reflect"
        support_strategy = str(routing_policy.get("default_strategy", "reflective"))
        specialist_agent = "reflective_support"
        if support_style in reflective_style_values or emotion_intensity == "low":
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
        contract_name=contract_name,
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
            "contract_name": contract_name,
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