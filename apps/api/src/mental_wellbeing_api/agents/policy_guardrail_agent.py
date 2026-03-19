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


def _high_risk_safe_redirect(state: AgentRuntimeState) -> str:
    summary = state.get("safety_summary") or "High-risk safety language detected."

    return " ".join(
        [
            "I'm glad you reached out.",
            "What you shared may need immediate human support rather than only an in-app response.",
            "If you may be in immediate danger or might act on these thoughts, contact local emergency services now or go to the nearest emergency department.",
            "If possible, contact a trusted person and ask them to stay with you right now.",
            "If you're in the U.S. or Canada, call or text 988. If you're elsewhere, contact your local crisis line or emergency number now.",
            f"Safety note: {summary}",
        ]
    ).strip()


def run_policy_guardrail_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    policy = load_runtime_policy()
    max_chars = int(policy.get("response", {}).get("max_final_response_chars", 1200))
    high_risk_requires_safe_redirect = bool(
        policy.get("safety", {}).get("high_risk_requires_safe_redirect", True)
    )

    response = state.get("final_response", "").strip()

    if (
        high_risk_requires_safe_redirect
        and (state.get("risk_level") or "").lower() == "high"
    ):
        response = _high_risk_safe_redirect(state)

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
        metadata={
            "max_chars": max_chars,
            "final_length": len(response),
            "risk_level": state.get("risk_level"),
            "safe_redirect_applied": (state.get("risk_level") or "").lower() == "high",
        },
    )
    state = append_handoff(
        state,
        from_agent="policy_guardrail",
        to_agent="execution_finalize",
        reason="response passed guardrails",
    )
    return state