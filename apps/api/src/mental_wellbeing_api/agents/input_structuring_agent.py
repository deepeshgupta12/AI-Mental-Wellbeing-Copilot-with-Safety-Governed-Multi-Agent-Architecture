from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_prompt
from mental_wellbeing_api.services.llm_service import LLMService


def run_input_structuring_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    llm = LLMService()
    system_prompt = load_prompt(
        "agents/input_structuring.txt",
        """
You structure a user's emotional wellbeing message into a concise summary.
Keep the output brief, neutral, and useful for downstream routing.
""",
    )

    user_prompt = (
        f"User input:\n{state['user_input']}\n\n"
        f"Session context:\n{state.get('session_context', '')}\n\n"
        f"Preference signals:\n{state.get('preference_signals', {})}\n\n"
        "Return a concise structured summary."
    )
    structured_input = llm.generate_text(state["provider"], system_prompt, user_prompt)

    state = {
        **state,
        "structured_input": structured_input,
    }
    state = append_execution_event(
        state,
        node_name="input_structuring",
        metadata={"structured_input_length": len(structured_input)},
    )
    state = append_handoff(
        state,
        from_agent="input_structuring",
        to_agent="tone_emotion_analyzer",
        reason="structured summary generated",
    )
    return state