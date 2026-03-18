from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_prompt
from mental_wellbeing_api.services.llm_service import LLMService


def _build_activation_recommendations(state: AgentRuntimeState) -> list[str]:
    recommendations: list[str] = []

    helpful_before = state.get("what_helped_before", [])
    if helpful_before:
        recommendations.append(f"What helped before: {helpful_before[0]}")

    support_style = state.get("preference_signals", {}).get("support_style", "").lower()
    if support_style in {"direct", "structured", "action-oriented"}:
        recommendations.append("Pick one task that takes under two minutes and do only the first motion.")
    else:
        recommendations.append("Choose one very small reset step that feels gentle enough to begin.")

    recommendations.append("Shrink the bar until completion feels more important than intensity.")
    return recommendations[:3]


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

    coping_recommendations = _build_activation_recommendations(state)

    user_prompt = (
        f"User input:\n{state['user_input']}\n\n"
        f"Session context:\n{state.get('session_context', '')}\n\n"
        f"Tone label: {state.get('tone_label', '')}\n"
        f"Emotion label: {state.get('emotion_label', '')}\n\n"
        f"Structured summary:\n{state.get('structured_input', '')}\n\n"
        f"What helped before:\n{state.get('what_helped_before', [])}\n\n"
        f"Preferred support style:\n{state.get('preference_signals', {}).get('support_style', '')}\n\n"
        "Write a brief response focused on one tiny doable next step."
    )
    specialist_response = llm.generate_text(state["provider"], system_prompt, user_prompt)

    state = {
        **state,
        "reflective_response": specialist_response,
        "specialist_response": specialist_response,
        "coping_recommendations": coping_recommendations,
        "journaling_insights": [
            "Activation usually works better when the first step is smaller than the mind expects.",
        ],
        "follow_up_suggestions": [
            "Tell me the smallest version of the task you could actually do in the next 10 minutes.",
            "If that still feels heavy, I can make the step even smaller.",
        ],
    }
    state = append_execution_event(
        state,
        node_name="behavioral_activation",
        metadata={
            "response_length": len(specialist_response),
            "coping_recommendation_count": len(coping_recommendations),
        },
    )
    state = append_handoff(
        state,
        from_agent="behavioral_activation",
        to_agent="response_composer",
        reason="behavioral activation draft prepared",
    )
    return state