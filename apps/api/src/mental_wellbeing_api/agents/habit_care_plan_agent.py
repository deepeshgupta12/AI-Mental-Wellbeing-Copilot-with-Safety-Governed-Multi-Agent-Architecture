from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_prompt
from mental_wellbeing_api.services.llm_service import LLMService


def _build_habit_recommendations(state: AgentRuntimeState) -> list[str]:
    recommendations = [
        "Anchor the habit to something that already happens daily.",
        "Decide on a fallback version that still counts on hard days.",
    ]

    support_style = state.get("preference_signals", {}).get("support_style", "").lower()
    if support_style in {"direct", "structured", "action-oriented"}:
        recommendations.insert(0, "Make the habit measurable enough to know whether it happened today.")

    return recommendations[:3]


def run_habit_care_plan_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    llm = LLMService()
    system_prompt = load_prompt(
        "agents/habit_care_plan.txt",
        """
You are a non-clinical wellbeing assistant helping the user build a small, sustainable care plan.
Focus on realistic consistency, not intensity. Keep the plan very small and specific.
""",
    )

    coping_recommendations = _build_habit_recommendations(state)

    user_prompt = (
        f"User input:\n{state['user_input']}\n\n"
        f"Structured summary:\n{state.get('structured_input', '')}\n\n"
        f"Session context:\n{state.get('session_context', '')}\n\n"
        f"Preferred support style:\n{state.get('preference_signals', {}).get('support_style', '')}\n\n"
        "Write a brief response with one tiny habit plan, one trigger, and one easy fallback option."
    )
    specialist_response = llm.generate_text(state["provider"], system_prompt, user_prompt)

    state = {
        **state,
        "reflective_response": specialist_response,
        "specialist_response": specialist_response,
        "coping_recommendations": coping_recommendations,
        "journaling_insights": [
            "Consistency usually improves when the habit is easier to restart than to perfect.",
        ],
        "follow_up_suggestions": [
            "I can help turn this into a morning, evening, or after-work version.",
            "If the plan still feels heavy, I can reduce it to a one-minute baseline.",
        ],
    }
    state = append_execution_event(
        state,
        node_name="habit_care_plan",
        metadata={
            "response_length": len(specialist_response),
            "coping_recommendation_count": len(coping_recommendations),
        },
    )
    state = append_handoff(
        state,
        from_agent="habit_care_plan",
        to_agent="response_composer",
        reason="habit care plan draft prepared",
    )
    return state