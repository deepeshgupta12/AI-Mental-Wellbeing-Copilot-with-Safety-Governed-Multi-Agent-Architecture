from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState


def _build_crisis_response(state: AgentRuntimeState) -> str:
    risk_level = (state.get("risk_level") or "unknown").lower()
    summary = state.get("safety_summary") or "High-risk language detected."

    lines = [
        "I'm really glad you said this out loud.",
        "What you shared may need immediate human support rather than only an in-app response.",
        "If you may act on these thoughts, contact local emergency services now or go to the nearest emergency department.",
        "If you can, reach out to one trusted person and ask them to stay with you right now.",
        "If you are in the U.S. or Canada, call or text 988. If you're elsewhere, contact your local crisis line or emergency number now.",
        f"Safety note: {summary}",
    ]

    if risk_level == "high":
        lines.append("Reply with: SAFE NOW / NEED HELP NOW / CONTACTING SOMEONE.")
    else:
        lines.append("Reply with: NEED SUPPORT / CONTACTING SOMEONE / NOT IN IMMEDIATE DANGER.")

    return "\n\n".join(lines)


def run_crisis_escalation_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    crisis_response = _build_crisis_response(state)

    state = {
        **state,
        "reflective_response": crisis_response,
        "specialist_response": crisis_response,
        "coping_recommendations": [],
        "journaling_insights": [],
        "follow_up_suggestions": [],
        "human_summary": state.get("human_summary")
        or "High-risk safety escalation path triggered. Human review strongly recommended.",
        "review_recommended": True,
        "requires_human_review": True,
        "decision_path_label": "crisis_escalation",
    }
    state = append_execution_event(
        state,
        node_name="crisis_escalation",
        metadata={
            "risk_level": state.get("risk_level"),
            "requires_human_review": True,
            "response_length": len(crisis_response),
        },
    )
    state = append_handoff(
        state,
        from_agent="crisis_escalation",
        to_agent="evidence_quality",
        reason="crisis escalation response prepared for reviewable safety path",
    )
    return state