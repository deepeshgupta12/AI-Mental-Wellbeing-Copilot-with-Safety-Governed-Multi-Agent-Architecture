from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_runtime_policy

BANNED_PHRASES = [
    "i diagnose",
    "you are diagnosed",
    "you definitely have",
    "as your therapist",
]


def run_policy_guardrail_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    policy = load_runtime_policy()
    max_chars = int(policy.get("response", {}).get("max_final_response_chars", 1200))

    response = state.get("final_response", "").strip()

    for phrase in BANNED_PHRASES:
        response = response.replace(phrase, "")

    response = " ".join(response.split())

    if len(response) > max_chars:
        response = response[: max_chars - 3] + "..."

    state = {
        **state,
        "final_response": response,
    }
    state = append_execution_event(
        state,
        node_name="policy_guardrail",
        metadata={"max_chars": max_chars, "final_length": len(response)},
    )
    state = append_handoff(
        state,
        from_agent="policy_guardrail",
        to_agent="execution_finalize",
        reason="response passed guardrails",
    )
    return state