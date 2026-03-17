from __future__ import annotations

from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_prompt
from mental_wellbeing_api.services.llm_service import LLMService


def run_response_composer_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    if state.get("safety_override"):
        final_response = (
            "I'm glad you reached out. What you shared sounds serious, and I want to respond carefully. "
            "If you may be in immediate danger or might act on these thoughts, contact local emergency services "
            "or a crisis helpline right now, and reach out to a trusted person who can be with you. "
            "If you're not in immediate danger, tell me whether you want help taking the next safe step right now."
        )
        return {
            **state,
            "reflective_response": state.get("reflective_response", ""),
            "final_response": final_response,
        }

    llm = LLMService()
    system_prompt = load_prompt(
        "agents/response_composer.txt",
        """
Compose a final user-facing response from the upstream agent outputs.
Keep it concise, calm, and supportive.
""",
    )

    user_prompt = (
        f"User input:\n{state['user_input']}\n\n"
        f"Session context:\n{state.get('session_context', '')}\n\n"
        f"Structured summary:\n{state.get('structured_input', '')}\n\n"
        f"Support strategy:\n{state.get('support_strategy', 'reflective')}\n\n"
        f"Draft response:\n{state.get('reflective_response', '')}\n\n"
        "Compose the final response."
    )
    final_response = llm.generate_text(state["provider"], system_prompt, user_prompt)

    return {
        **state,
        "final_response": final_response,
    }