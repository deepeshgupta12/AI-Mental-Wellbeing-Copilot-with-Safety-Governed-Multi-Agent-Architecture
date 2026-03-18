from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_prompt
from mental_wellbeing_api.services.llm_service import LLMService


def run_journaling_insight_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    llm = LLMService()
    system_prompt = load_prompt(
        "agents/journaling_insight.txt",
        """
You are a non-clinical wellbeing assistant helping the user extract insight from reflection or journaling.
Identify themes, patterns, and one gentle question worth exploring next.
Keep it concise and grounded.
""",
    )

    user_prompt = (
        f"User input:\n{state['user_input']}\n\n"
        f"Structured summary:\n{state.get('structured_input', '')}\n\n"
        f"Session context:\n{state.get('session_context', '')}\n\n"
        "Write a brief response that highlights one or two themes and one reflective next question."
    )
    specialist_response = llm.generate_text(state["provider"], system_prompt, user_prompt)

    state = {
        **state,
        "reflective_response": specialist_response,
        "specialist_response": specialist_response,
        "coping_recommendations": [],
        "journaling_insights": [
            "There may be a recurring pattern worth naming more explicitly.",
            "The feeling and the meaning you attach to it may be slightly different things.",
        ],
        "follow_up_suggestions": [
            "Write one sentence about what felt most important beneath the event itself.",
        ],
    }
    state = append_execution_event(
        state,
        node_name="journaling_insight",
        metadata={"response_length": len(specialist_response)},
    )
    state = append_handoff(
        state,
        from_agent="journaling_insight",
        to_agent="response_composer",
        reason="journaling insight draft prepared",
    )
    return state