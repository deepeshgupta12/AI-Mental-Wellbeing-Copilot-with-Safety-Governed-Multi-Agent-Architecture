from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_prompt
from mental_wellbeing_api.services.llm_service import LLMService


def run_cbt_reframing_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    llm = LLMService()
    system_prompt = load_prompt(
        "agents/cbt_reframing.txt",
        """
You are a non-clinical wellbeing assistant using gentle CBT-style reframing.
Help the user notice thought patterns, soften absolutes, and find a more balanced interpretation.
Stay supportive and concise.
""",
    )

    user_prompt = (
        f"User input:\n{state['user_input']}\n\n"
        f"Structured summary:\n{state.get('structured_input', '')}\n\n"
        f"Session context:\n{state.get('session_context', '')}\n\n"
        "Write a brief response that validates the feeling, identifies one possible distorted pattern, "
        "and offers one more balanced alternative thought."
    )
    specialist_response = llm.generate_text(state["provider"], system_prompt, user_prompt)

    state = {
        **state,
        "reflective_response": specialist_response,
        "specialist_response": specialist_response,
        "coping_recommendations": [
            "Replace one extreme word like 'always' or 'never' with something more accurate.",
        ],
        "journaling_insights": [
            "Notice whether the mind is turning one moment into a full identity statement.",
        ],
        "follow_up_suggestions": [
            "Share the thought you want help reframing next.",
        ],
    }
    state = append_execution_event(
        state,
        node_name="cbt_reframing",
        metadata={"response_length": len(specialist_response)},
    )
    state = append_handoff(
        state,
        from_agent="cbt_reframing",
        to_agent="response_composer",
        reason="reframing draft prepared",
    )
    return state