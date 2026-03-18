from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_prompt
from mental_wellbeing_api.services.llm_service import LLMService


def _build_reframing_recommendations(state: AgentRuntimeState) -> list[str]:
    recommendations = [
        "Replace one extreme word like 'always' or 'never' with something more precise.",
        "Ask what evidence supports the thought and what evidence complicates it.",
    ]

    helpful_before = state.get("what_helped_before", [])
    if helpful_before:
        recommendations.insert(0, f"What helped before: {helpful_before[0]}")

    return recommendations[:3]


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

    coping_recommendations = _build_reframing_recommendations(state)

    user_prompt = (
        f"User input:\n{state['user_input']}\n\n"
        f"Structured summary:\n{state.get('structured_input', '')}\n\n"
        f"Session context:\n{state.get('session_context', '')}\n\n"
        f"Tone label: {state.get('tone_label', '')}\n"
        f"Emotion label: {state.get('emotion_label', '')}\n\n"
        "Write a brief response that validates the feeling, identifies one possible distorted pattern, "
        "and offers one more balanced alternative thought."
    )
    specialist_response = llm.generate_text(state["provider"], system_prompt, user_prompt)

    state = {
        **state,
        "reflective_response": specialist_response,
        "specialist_response": specialist_response,
        "coping_recommendations": coping_recommendations,
        "journaling_insights": [
            "The mind may be turning a painful moment into a total identity judgment.",
        ],
        "follow_up_suggestions": [
            "Send me the exact thought you want to challenge next.",
            "I can help you rewrite that thought into something more accurate, not artificially positive.",
        ],
    }
    state = append_execution_event(
        state,
        node_name="cbt_reframing",
        metadata={
            "response_length": len(specialist_response),
            "coping_recommendation_count": len(coping_recommendations),
        },
    )
    state = append_handoff(
        state,
        from_agent="cbt_reframing",
        to_agent="response_composer",
        reason="reframing draft prepared",
    )
    return state