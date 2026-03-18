from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_prompt
from mental_wellbeing_api.services.llm_service import LLMService


def _build_social_recommendations(state: AgentRuntimeState) -> list[str]:
    recommendations = [
        "Choose the lowest-pressure person or channel to reconnect through.",
        "Aim for contact, not a perfect conversation.",
    ]

    support_style = state.get("preference_signals", {}).get("support_style", "").lower()
    if support_style in {"direct", "structured", "action-oriented"}:
        recommendations[1] = "Send one simple message instead of waiting to feel fully ready."

    return recommendations[:3]


def run_social_support_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    llm = LLMService()
    system_prompt = load_prompt(
        "agents/social_support.txt",
        """
You are a non-clinical wellbeing assistant focused on social support and connection.
Help the user identify one safe, realistic point of connection without pressure or guilt.
Keep the tone warm and concise.
""",
    )

    coping_recommendations = _build_social_recommendations(state)

    user_prompt = (
        f"User input:\n{state['user_input']}\n\n"
        f"Structured summary:\n{state.get('structured_input', '')}\n\n"
        f"Session context:\n{state.get('session_context', '')}\n\n"
        f"Preferred support style:\n{state.get('preference_signals', {}).get('support_style', '')}\n\n"
        "Write a brief response that validates loneliness or disconnection and suggests one small support-seeking step."
    )
    specialist_response = llm.generate_text(state["provider"], system_prompt, user_prompt)

    state = {
        **state,
        "reflective_response": specialist_response,
        "specialist_response": specialist_response,
        "coping_recommendations": coping_recommendations,
        "journaling_insights": [
            "Notice whether the hardest part is reaching out, trusting, or asking clearly.",
        ],
        "follow_up_suggestions": [
            "I can help draft a simple message to someone safe if that would help.",
            "Tell me whether the harder part is who to contact or what to say.",
        ],
    }
    state = append_execution_event(
        state,
        node_name="social_support",
        metadata={
            "response_length": len(specialist_response),
            "coping_recommendation_count": len(coping_recommendations),
        },
    )
    state = append_handoff(
        state,
        from_agent="social_support",
        to_agent="response_composer",
        reason="social support draft prepared",
    )
    return state