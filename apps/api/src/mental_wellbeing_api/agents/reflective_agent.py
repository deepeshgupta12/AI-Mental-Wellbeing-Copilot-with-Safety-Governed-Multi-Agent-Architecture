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
        f"Structured summary:\n{state['structured_input']}\n\n"
        "Write a brief reflective response."
    )
    reflective_response = llm.generate_text(state["provider"], system_prompt, user_prompt)

    state = {
        **state,
        "reflective_response": reflective_response,
    }
    state = append_execution_event(
        state,
        node_name="reflective_support",
        metadata={"response_length": len(reflective_response)},
    )
    state = append_handoff(
        state,
        from_agent="reflective_support",
        to_agent="response_composer",
        reason="reflective draft prepared",
    )
    return state