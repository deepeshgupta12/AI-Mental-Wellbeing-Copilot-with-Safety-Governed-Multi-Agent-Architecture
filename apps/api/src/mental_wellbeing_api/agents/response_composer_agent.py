from __future__ import annotations

from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_prompt
from mental_wellbeing_api.services.llm_service import LLMService


def run_response_composer_agent(state: AgentRuntimeState) -> AgentRuntimeState:
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
        f"Structured summary:\n{state['structured_input']}\n\n"
        f"Reflective response draft:\n{state['reflective_response']}\n\n"
        "Compose the final response."
    )
    final_response = llm.generate_text(state["provider"], system_prompt, user_prompt)

    return {
        **state,
        "final_response": final_response,
    }