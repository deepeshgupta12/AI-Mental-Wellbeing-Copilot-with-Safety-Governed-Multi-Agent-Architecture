from __future__ import annotations

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

    user_prompt = f"User input:\n{state['user_input']}\n\nReturn a concise structured summary."
    structured_input = llm.generate_text(state["provider"], system_prompt, user_prompt)

    return {
        **state,
        "structured_input": structured_input,
    }