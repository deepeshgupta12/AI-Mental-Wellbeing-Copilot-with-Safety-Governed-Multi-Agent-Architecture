from __future__ import annotations

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


def run_supervisor_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    if state.get("risk_level") == "medium":
        strategy = "distress_stabilization"
    else:
        text = state.get("user_input", "").lower()
        if any(hint in text for hint in BEHAVIORAL_ACTIVATION_HINTS):
            strategy = "behavioral_activation"
        else:
            strategy = "reflective"

    return {
        **state,
        "support_strategy": strategy,
    }