from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_prompt
from mental_wellbeing_api.services.llm_service import LLMService


def run_distress_stabilization_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    llm = LLMService()
    system_prompt = load_prompt(
        "agents/distress_stabilization.txt",
        """
You are a calm, grounded, non-clinical wellbeing assistant.
Help the user stabilize in the next few minutes.
Keep the response brief, gentle, and concrete.
""",
    )

    user_prompt = (
        f"User input:\n{state['user_input']}\n\n"
        f"Session context:\n{state.get('session_context', '')}\n\n"
        f"Tone label: {state.get('tone_label', '')}\n"
        f"Emotion label: {state.get('emotion_label', '')}\n"
        f"Emotion intensity: {state.get('emotion_intensity', '')}\n\n"
        f"Structured summary:\n{state.get('structured_input', '')}\n\n"
        "Write a brief stabilization response with 1-2 immediate next steps."
    )
    specialist_response = llm.generate_text(state["provider"], system_prompt, user_prompt)

    state = {
        **state,
        "reflective_response": specialist_response,
        "specialist_response": specialist_response,
        "coping_recommendations": [
            "Slow one exhale slightly longer than the inhale.",
            "Orient to one nearby object and describe it quietly.",
        ],
        "journaling_insights": [],
        "follow_up_suggestions": [
            "Let me know if the intensity shifts over the next few minutes.",
        ],
    }
    state = append_execution_event(
        state,
        node_name="distress_stabilization",
        metadata={"response_length": len(specialist_response)},
    )
    state = append_handoff(
        state,
        from_agent="distress_stabilization",
        to_agent="response_composer",
        reason="stabilization draft prepared",
    )
    return state