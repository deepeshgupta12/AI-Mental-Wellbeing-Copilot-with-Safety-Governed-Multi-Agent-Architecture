from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState

DIRECT_STYLE_HINTS = {
    "plan",
    "activate",
    "reframe",
    "behavioral_activation",
    "habit_care_plan",
}
REFLECTIVE_STYLE_HINTS = {
    "reflect",
    "reflective",
    "journaling_insight",
    "social_support",
}
RECOVERY_STYLE_HINTS = {
    "recover",
    "sleep_recovery",
}
STABILIZE_STYLE_HINTS = {
    "stabilize",
    "distress_stabilization",
}


def run_preference_learning_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    support_mode = (state.get("support_mode") or "").lower()
    support_strategy = (state.get("support_strategy") or "").lower()
    specialist_agent = (state.get("specialist_agent") or "").lower()
    current_preferences = dict(state.get("preference_signals", {}))

    current_support_style = (current_preferences.get("support_style") or "").lower() or None
    current_preferred_support_mode = (
        (current_preferences.get("preferred_support_mode") or "").lower() or None
    )

    inferred_support_style = current_support_style
    inferred_preferred_support_mode = current_preferred_support_mode

    style_candidates = {support_mode, support_strategy, specialist_agent}

    # Preserve an explicitly direct user preference unless the route is also direct,
    # and never downgrade direct users into reflective/calm just because a single
    # session used a reflective specialist.
    if style_candidates & DIRECT_STYLE_HINTS:
        inferred_support_style = "direct"
    elif current_support_style:
        inferred_support_style = current_support_style
    elif style_candidates & REFLECTIVE_STYLE_HINTS:
        inferred_support_style = "reflective"
    elif style_candidates & RECOVERY_STYLE_HINTS:
        inferred_support_style = "calm"

    if style_candidates & STABILIZE_STYLE_HINTS:
        inferred_preferred_support_mode = "stabilize"
    elif support_mode:
        inferred_preferred_support_mode = support_mode

    updated_preferences = {
        **current_preferences,
    }
    if inferred_support_style:
        updated_preferences["support_style"] = inferred_support_style
    if inferred_preferred_support_mode:
        updated_preferences["preferred_support_mode"] = inferred_preferred_support_mode

    learned_preferences: dict[str, str] = {}
    if inferred_support_style:
        learned_preferences["support_style"] = inferred_support_style
    if inferred_preferred_support_mode:
        learned_preferences["preferred_support_mode"] = inferred_preferred_support_mode

    state = {
        **state,
        "preference_signals": updated_preferences,
        "learned_preferences": learned_preferences,
    }
    state = append_execution_event(
        state,
        node_name="preference_learning",
        metadata={
            "previous_support_style": current_support_style,
            "support_style": inferred_support_style,
            "preferred_support_mode": inferred_preferred_support_mode,
        },
    )
    state = append_handoff(
        state,
        from_agent="preference_learning",
        to_agent="follow_up_planner",
        reason="preference adaptation signals prepared for follow-up planning and composition",
    )
    return state