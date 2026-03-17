from __future__ import annotations

from mental_wellbeing_api.orchestration.state import AgentRuntimeState

BANNED_PHRASES = [
    "i diagnose",
    "you are diagnosed",
    "you definitely have",
    "as your therapist",
]


def run_policy_guardrail_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    response = state.get("final_response", "").strip()

    for phrase in BANNED_PHRASES:
        response = response.replace(phrase, "")

    response = " ".join(response.split())

    if len(response) > 1200:
        response = response[:1197] + "..."

    return {
        **state,
        "final_response": response,
    }