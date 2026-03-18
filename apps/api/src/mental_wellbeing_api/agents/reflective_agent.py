from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_prompt
from mental_wellbeing_api.services.llm_service import LLMService


def run_reflective_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    llm = LLMService()
    system_prompt = load_prompt(
        "agents/reflective_support.txt",
        """
You are a calm, supportive, non-clinical reflective wellbeing assistant.
Validate gently, avoid diagnosis, and keep the tone grounded.
""",
    )

    user_prompt = (
        f"User input:\n{state['user_input']}\n\n"
        f"Session context:\n{state.get('session_context', '')}\n\n"
        f"Tone label: {state.get('tone_label', '')}\n"
        f"Emotion label: {state.get('emotion_label', '')}\n"
        f"Emotion intensity: {state.get('emotion_intensity', '')}\n\n"
        f"Structured summary:\n{state['structured_input']}\n\n"
        "Write a brief reflective response."
    )
    specialist_response = llm.generate_text(state["provider"], system_prompt, user_prompt)

    state = {
        **state,
        "reflective_response": specialist_response,
        "specialist_response": specialist_response,
        "coping_recommendations": [],
        "journaling_insights": [],
        "follow_up_suggestions": [
            "Notice one moment today that felt slightly easier than the rest.",
            "Return and share what feels most important to unpack next.",
        ],
    }
    state = append_execution_event(
        state,
        node_name="reflective_support",
        metadata={"response_length": len(specialist_response)},
    )
    state = append_handoff(
        state,
        from_agent="reflective_support",
        to_agent="response_composer",
        reason="reflective draft prepared",
    )
    return state