from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_prompt
from mental_wellbeing_api.services.llm_service import LLMService


def run_behavioral_activation_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    llm = LLMService()
    system_prompt = load_prompt(
        "agents/behavioral_activation.txt",
        """
You are a calm, practical, non-clinical wellbeing assistant.
Help the user identify one very small next action.
Keep the response short, concrete, and encouraging.
""",
    )

    user_prompt = (
        f"User input:\n{state['user_input']}\n\n"
        f"Session context:\n{state.get('session_context', '')}\n\n"
        f"Structured summary:\n{state.get('structured_input', '')}\n\n"
        "Write a brief response focused on one tiny doable next step."
    )
    reflective_response = llm.generate_text(state["provider"], system_prompt, user_prompt)

    state = {
        **state,
        "reflective_response": reflective_response,
    }
    state = append_execution_event(
        state,
        node_name="behavioral_activation",
        metadata={"response_length": len(reflective_response)},
    )
    state = append_handoff(
        state,
        from_agent="behavioral_activation",
        to_agent="response_composer",
        reason="behavioral activation draft prepared",
    )
    return state