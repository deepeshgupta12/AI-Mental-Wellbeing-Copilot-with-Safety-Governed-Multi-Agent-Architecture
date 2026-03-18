from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_prompt
from mental_wellbeing_api.services.llm_service import LLMService


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

    user_prompt = (
        f"User input:\n{state['user_input']}\n\n"
        f"Structured summary:\n{state.get('structured_input', '')}\n\n"
        f"Session context:\n{state.get('session_context', '')}\n\n"
        "Write a brief response that validates loneliness or disconnection and suggests one small support-seeking step."
    )
    specialist_response = llm.generate_text(state["provider"], system_prompt, user_prompt)

    state = {
        **state,
        "reflective_response": specialist_response,
        "specialist_response": specialist_response,
        "coping_recommendations": [
            "Choose the lowest-pressure person or channel to reconnect through.",
        ],
        "journaling_insights": [
            "Notice whether the hardest part is reaching out, trusting, or asking clearly.",
        ],
        "follow_up_suggestions": [
            "I can help draft a simple message to someone safe if that would help.",
        ],
    }
    state = append_execution_event(
        state,
        node_name="social_support",
        metadata={"response_length": len(specialist_response)},
    )
    state = append_handoff(
        state,
        from_agent="social_support",
        to_agent="response_composer",
        reason="social support draft prepared",
    )
    return state