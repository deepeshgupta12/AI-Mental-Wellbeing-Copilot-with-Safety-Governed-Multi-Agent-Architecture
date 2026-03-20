from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import (
    append_execution_event,
    append_handoff,
    set_routing_contract,
)
from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_routing_rules, load_runtime_policy


def _contains_any(text: str, hints: list[str]) -> bool:
    return any(hint in text for hint in hints)


def run_intent_router_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    text = " ".join(
        [
            state.get("user_input", ""),
            state.get("structured_input", ""),
        ]
    ).lower()

    support_track = (state.get("support_track") or "").strip().lower()

    policy = load_runtime_policy()
    routing_policy = policy.get("routing", {}) if isinstance(policy, dict) else {}
    rules = load_routing_rules()
    intent_rules = rules.get("intent_router", {}) if isinstance(rules, dict) else {}

    sleep_hints = list(intent_rules.get("sleep_hints", []))
    social_hints = list(intent_rules.get("social_hints", []))
    habit_hints = list(intent_rules.get("habit_hints", []))
    overwhelm_hints = list(intent_rules.get("overwhelm_hints", []))
    journaling_strong_hints = list(intent_rules.get("journaling_strong_hints", []))
    journaling_reflection_hints = list(intent_rules.get("journaling_reflection_hints", []))
    cognitive_reframe_hints = list(intent_rules.get("cognitive_reframe_hints", []))

    if support_track in {
        "stress_overwhelm",
        "sleep_recovery",
        "journaling_reflection",
        "social_support",
        "habit_support",
    }:
        track_to_intent = {
            "stress_overwhelm": "stress_overwhelm",
            "sleep_recovery": "sleep_recovery",
            "journaling_reflection": "journaling_insight",
            "social_support": "social_support",
            "habit_support": "habit_support",
        }
        intent_label = track_to_intent[support_track]
        routing_reason = f"support track '{support_track}' selected"
    elif _contains_any(text, sleep_hints):
        intent_label = "sleep_recovery"
        routing_reason = "sleep-oriented cues detected"
    elif _contains_any(text, social_hints):
        intent_label = "social_support"
        routing_reason = "social-support cues detected"
    elif _contains_any(text, cognitive_reframe_hints):
        intent_label = "cognitive_reframing"
        routing_reason = "cognitive distortion or self-judgment cues detected"
    elif _contains_any(text, habit_hints):
        intent_label = "habit_support"
        routing_reason = "habit-building cues detected"
    elif _contains_any(text, journaling_strong_hints) or (
        _contains_any(text, journaling_reflection_hints) and "journal" in text
    ):
        intent_label = "journaling_insight"
        routing_reason = "journaling or reflection-on-writing cues detected"
    elif _contains_any(text, overwhelm_hints):
        intent_label = "stress_overwhelm"
        routing_reason = "stress or overwhelm cues detected"
    else:
        intent_label = str(routing_policy.get("default_intent", "general_reflection"))
        routing_reason = "default reflection pathway"

    contract_name = str(routing_policy.get("contract_name", "v2-routing-core"))

    state = {
      **state,
      "intent_label": intent_label,
      "routing_reason": routing_reason,
    }
    state = set_routing_contract(
        state,
        contract_name=contract_name,
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
            "contract_name": contract_name,
            "support_track": support_track,
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