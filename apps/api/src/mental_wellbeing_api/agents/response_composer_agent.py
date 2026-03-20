from __future__ import annotations

import re

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_prompt
from mental_wellbeing_api.services.llm_service import LLMService


def _sanitize_text(value: str | None) -> str:
    if not value:
        return ""

    text = value
    text = re.sub(
        r"\[(?:mock-response:[^\]]+|mock-response|ollama-error|openai-error|openai-unavailable|unsupported-provider)[^\]]*\]",
        "",
        text,
    )
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _safe_specialist_text(state: AgentRuntimeState) -> str:
    specialist_response = _sanitize_text(
        state.get("specialist_response") or state.get("reflective_response", "")
    )
    if specialist_response:
        return specialist_response

    support_mode = (state.get("support_mode") or "").lower()
    fallback_by_mode = {
        "reflect": "It sounds like this has been weighing on you, and slowing down to understand it is a meaningful step.",
        "activate": "Let's focus on one very small next step so this feels more manageable.",
        "reframe": "We can look at the thought more carefully and separate the hard moment from the harsher conclusion.",
        "recover": "Let's keep this gentle and focus on one realistic recovery step.",
        "connect": "You do not have to carry this alone. We can think about one safe connection point.",
        "journal": "There may be a pattern here worth naming before trying to solve everything at once.",
        "plan": "Let's make this smaller and more concrete so it is easier to follow through.",
        "stabilize": "For now, let's focus on getting a little steadier, one moment at a time.",
    }
    return fallback_by_mode.get(
        support_mode,
        "It sounds like this has been difficult, and we can take it one clear step at a time.",
    )


def _normalize_visible_response(text: str) -> str:
    cleaned = _sanitize_text(text)
    cleaned = re.sub(
        r"(Support summary:|Progress:|Patterns:|Intervention trend:|Follow-up:|Reminder timing:|Delivery channel:|Scheduler backend:|Follow-up plan:)",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _build_mock_final_response(state: AgentRuntimeState) -> str:
    specialist_response = _safe_specialist_text(state)
    coping_recommendations = state.get("coping_recommendations", [])
    follow_up_suggestions = state.get("follow_up_suggestions", [])

    parts: list[str] = []

    if specialist_response:
        parts.append(specialist_response)

    if coping_recommendations:
        parts.append(coping_recommendations[0])

    if follow_up_suggestions:
        parts.append(follow_up_suggestions[0])

    final_text = " ".join(part.strip() for part in parts if part).strip()
    return _normalize_visible_response(final_text)


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
            "reflective_response": _sanitize_text(state.get("reflective_response", "")),
            "specialist_response": _sanitize_text(state.get("specialist_response", "")),
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
            "reflective_response": _sanitize_text(state.get("reflective_response", "")),
            "specialist_response": _sanitize_text(state.get("specialist_response", "")),
            "final_response": final_response,
        }
        state = append_execution_event(
            state,
            node_name="response_composer",
            metadata={
                "mode": "mock_specialist_blend",
                "response_length": len(final_response),
                "follow_up_required": bool(state.get("follow_up_required", False)),
            },
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
Adapt the tone to the user's support-style preferences when available.
Do not expose internal system metadata, runtime summaries, scheduler details, delivery channels,
backend names, contracts, queue states, trace data, policy labels, or audit fields.
Do not list "support summary", "follow-up plan", "delivery channel", "scheduler backend",
or reminder timestamps in the visible reply.
Keep the answer natural and conversational.
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
        f"Preference signals:\n{state.get('preference_signals', {})}\n\n"
        f"Primary draft:\n{_safe_specialist_text(state)}\n\n"
        f"Coping recommendations:\n{state.get('coping_recommendations', [])}\n\n"
        f"Journaling insights:\n{state.get('journaling_insights', [])}\n\n"
        f"Follow-up suggestions:\n{state.get('follow_up_suggestions', [])}\n\n"
        f"Follow-up required:\n{state.get('follow_up_required', False)}\n\n"
        "Write one natural user-facing reply. Keep any continuity mention subtle and non-technical."
    )
    final_response = _normalize_visible_response(
        llm.generate_text(
            state["provider"],
            system_prompt,
            user_prompt,
            agent_name="response_composer",
            risk_level=state.get("risk_level"),
            final_stage=True,
        )
    )

    if not final_response:
        final_response = _build_mock_final_response(state)

    state = {
        **state,
        "reflective_response": _sanitize_text(state.get("reflective_response", "")),
        "specialist_response": _sanitize_text(state.get("specialist_response", "")),
        "final_response": final_response,
    }
    state = append_execution_event(
        state,
        node_name="response_composer",
        metadata={
            "mode": "standard",
            "response_length": len(final_response),
            "follow_up_required": bool(state.get("follow_up_required", False)),
        },
    )
    state = append_handoff(
        state,
        from_agent="response_composer",
        to_agent="policy_guardrail",
        reason="final response composed",
    )
    return state