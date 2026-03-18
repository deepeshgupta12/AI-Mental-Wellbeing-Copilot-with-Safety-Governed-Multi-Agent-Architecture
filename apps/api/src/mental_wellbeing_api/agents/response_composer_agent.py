from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_prompt
from mental_wellbeing_api.services.llm_service import LLMService


def _build_mock_final_response(state: AgentRuntimeState) -> str:
    specialist_response = state.get("specialist_response") or state.get("reflective_response", "")
    coping_recommendations = state.get("coping_recommendations", [])
    journaling_insights = state.get("journaling_insights", [])
    follow_up_suggestions = state.get("follow_up_suggestions", [])

    parts: list[str] = []

    if specialist_response:
        parts.append(specialist_response)

    if coping_recommendations:
        parts.append("Suggestions:\n- " + "\n- ".join(coping_recommendations[:2]))

    if journaling_insights:
        parts.append("Insight:\n- " + "\n- ".join(journaling_insights[:2]))

    if follow_up_suggestions:
        parts.append("Next:\n- " + follow_up_suggestions[0])

    return "\n\n".join(parts).strip()


def run_response_composer_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    if state.get("safety_override"):
        final_response = (
            "I'm glad you reached out. What you shared sounds serious, and I want to respond carefully. "
            "If you may be in immediate danger or might act on these thoughts, contact local emergency services "
            "or a crisis helpline right now, and reach out to a trusted person who can be with you. "
            "If you're not in immediate danger, tell me whether you want help taking the next safe step right now."
        )
        state = {
            **state,
            "reflective_response": state.get("reflective_response", ""),
            "specialist_response": state.get("specialist_response", ""),
            "final_response": final_response,
        }
        state = append_execution_event(
            state,
            node_name="response_composer",
            metadata={"mode": "safety_override", "response_length": len(final_response)},
        )
        state = append_handoff(
            state,
            from_agent="response_composer",
            to_agent="policy_guardrail",
            reason="safe redirect response prepared",
        )
        return state

    if state.get("provider") == "mock":
        final_response = _build_mock_final_response(state)
        state = {
            **state,
            "final_response": final_response,
        }
        state = append_execution_event(
            state,
            node_name="response_composer",
            metadata={"mode": "mock_specialist_blend", "response_length": len(final_response)},
        )
        state = append_handoff(
            state,
            from_agent="response_composer",
            to_agent="policy_guardrail",
            reason="mock final response composed from specialist outputs",
        )
        return state

    llm = LLMService()
    system_prompt = load_prompt(
        "agents/response_composer.txt",
        """
Compose a final user-facing response from the upstream agent outputs.
Keep it concise, calm, supportive, and clearly non-clinical.
Prefer the specialist draft when present.
Use coping recommendations and follow-up suggestions selectively instead of repeating everything.
""",
    )

    user_prompt = (
        f"User input:\n{state['user_input']}\n\n"
        f"Session context:\n{state.get('session_context', '')}\n\n"
        f"Structured summary:\n{state.get('structured_input', '')}\n\n"
        f"Tone label: {state.get('tone_label', '')}\n"
        f"Emotion label: {state.get('emotion_label', '')}\n"
        f"Emotion intensity: {state.get('emotion_intensity', '')}\n\n"
        f"Intent label:\n{state.get('intent_label', 'general_reflection')}\n\n"
        f"Support mode:\n{state.get('support_mode', 'reflect')}\n\n"
        f"Support strategy:\n{state.get('support_strategy', 'reflective')}\n\n"
        f"Specialist agent:\n{state.get('specialist_agent', 'reflective_support')}\n\n"
        f"Primary draft:\n{state.get('specialist_response', state.get('reflective_response', ''))}\n\n"
        f"Coping recommendations:\n{state.get('coping_recommendations', [])}\n\n"
        f"Journaling insights:\n{state.get('journaling_insights', [])}\n\n"
        f"Follow-up suggestions:\n{state.get('follow_up_suggestions', [])}\n\n"
        "Compose the final response."
    )
    final_response = llm.generate_text(state["provider"], system_prompt, user_prompt)

    state = {
        **state,
        "final_response": final_response,
    }
    state = append_execution_event(
        state,
        node_name="response_composer",
        metadata={"mode": "standard", "response_length": len(final_response)},
    )
    state = append_handoff(
        state,
        from_agent="response_composer",
        to_agent="policy_guardrail",
        reason="final response composed",
    )
    return state