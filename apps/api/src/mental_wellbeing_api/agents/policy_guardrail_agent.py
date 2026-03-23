from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_runtime_policy
from mental_wellbeing_api.services.localization_service import LocalizationService

BANNED_PHRASES = [
    "i diagnose",
    "you are diagnosed",
    "you definitely have",
    "as your therapist",
]


def _resolve_language(state: AgentRuntimeState) -> str:
    return (
        state.get("preferred_language")
        or state.get("content_language")
        or state.get("preference_signals", {}).get("preferred_language")
        or "en"
    )


def _high_risk_safe_redirect(state: AgentRuntimeState) -> str:
    service = LocalizationService(None)  # type: ignore[arg-type]
    language = _resolve_language(state)
    summary = state.get("safety_summary") or "High-risk safety language detected."

    response = " ".join(
        [
            service.localize_text("crisis_open", language, "I'm glad you reached out."),
            service.localize_text(
                "crisis_immediate",
                language,
                "If you may be in immediate danger or might act on these thoughts, contact local emergency services now.",
            ),
            service.localize_text(
                "crisis_support",
                language,
                "If possible, reach out to a trusted person and ask them to stay with you right now.",
            ),
            service.localize_text(
                "crisis_follow_up",
                language,
                "If you're not in immediate danger, tell me whether you want help taking the next safe step right now.",
            ),
            f"Safety note: {summary}" if language == "en" else summary,
        ]
    ).strip()
    return response


def run_policy_guardrail_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    policy = load_runtime_policy()
    max_chars = int(policy.get("response", {}).get("max_final_response_chars", 1200))
    high_risk_requires_safe_redirect = bool(
        policy.get("safety", {}).get("high_risk_requires_safe_redirect", True)
    )
    language = _resolve_language(state)

    response = state.get("final_response", "").strip()

    if high_risk_requires_safe_redirect and (state.get("risk_level") or "").lower() == "high":
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
            "language": language,
        },
    )
    state = append_handoff(
        state,
        from_agent="policy_guardrail",
        to_agent="execution_finalize",
        reason="response passed guardrails",
    )
    return state