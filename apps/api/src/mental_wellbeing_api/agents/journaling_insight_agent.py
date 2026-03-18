from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_prompt
from mental_wellbeing_api.services.llm_service import LLMService


def _build_journaling_insights(state: AgentRuntimeState) -> list[str]:
    insights = [
        "There may be a recurring pattern worth naming more explicitly.",
        "The feeling and the meaning attached to it may not be exactly the same thing.",
    ]

    helpful_before = state.get("what_helped_before", [])
    if helpful_before:
        insights.append(f"A past helpful pattern may be worth re-examining: {helpful_before[0]}")

    return insights[:3]


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

    journaling_insights = _build_journaling_insights(state)

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
        "coping_recommendations": [
            "Write one sentence about what felt most important beneath the event itself.",
        ],
        "journaling_insights": journaling_insights,
        "follow_up_suggestions": [
            "Share the part of the journal entry that feels most charged or confusing.",
            "I can help turn the reflection into a clearer theme or question.",
        ],
    }
    state = append_execution_event(
        state,
        node_name="journaling_insight",
        metadata={
            "response_length": len(specialist_response),
            "journaling_insight_count": len(journaling_insights),
        },
    )
    state = append_handoff(
        state,
        from_agent="journaling_insight",
        to_agent="response_composer",
        reason="journaling insight draft prepared",
    )
    return state