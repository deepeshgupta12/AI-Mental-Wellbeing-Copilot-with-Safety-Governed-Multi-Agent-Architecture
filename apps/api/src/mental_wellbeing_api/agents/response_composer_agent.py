from __future__ import annotations

import re
from datetime import datetime

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_prompt
from mental_wellbeing_api.services.llm_service import LLMService


def _style_prefix(preference_signals: dict[str, str]) -> str:
    support_style = preference_signals.get("support_style", "").lower()
    preferred_support_mode = preference_signals.get("preferred_support_mode", "").lower()

    if preferred_support_mode == "plan":
        return "Let's make this concrete."
    if preferred_support_mode == "recover":
        return "Let's keep this calming and restorative."
    if support_style == "direct":
        return "I'll keep this practical and clear."
    if support_style == "reflective":
        return "I'll stay thoughtful and gentle with this."
    return ""


def _format_follow_up_timing(follow_up_due_at: str | None) -> str | None:
    if not follow_up_due_at:
        return None

    try:
        normalized = follow_up_due_at.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        return parsed.strftime("%b %d, %Y at %I:%M %p")
    except ValueError:
        return follow_up_due_at


def _sanitize_text(value: str | None) -> str:
    if not value:
        return ""

    text = value
    text = re.sub(r"\[(?:mock-response:[^\]]+|mock-response|ollama-error|openai-error|openai-unavailable|unsupported-provider)[^\]]*\]", "", text)
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


def _build_mock_final_response(state: AgentRuntimeState) -> str:
    specialist_response = _safe_specialist_text(state)
    coping_recommendations = state.get("coping_recommendations", [])
    journaling_insights = state.get("journaling_insights", [])
    follow_up_suggestions = state.get("follow_up_suggestions", [])
    preference_signals = state.get("preference_signals", {})
    progress_summary = state.get("progress_summary")
    recurring_patterns = state.get("recurring_patterns", [])
    intervention_effectiveness = state.get("intervention_effectiveness", {})
    support_progress_summary = state.get("support_progress_summary")

    follow_up_required = bool(state.get("follow_up_required", False))
    follow_up_title = state.get("follow_up_plan_title")
    follow_up_due_at = state.get("follow_up_due_at")
    follow_up_delivery_channel = state.get("follow_up_delivery_channel")
    scheduler_backend = state.get("scheduler_backend")

    parts: list[str] = []

    prefix = _style_prefix(preference_signals)
    if prefix:
        parts.append(prefix)

    if specialist_response:
        parts.append(specialist_response)

    if progress_summary:
        parts.append(f"Progress:\n- {progress_summary}")

    if support_progress_summary:
        parts.append(f"Support summary:\n- {support_progress_summary}")

    if recurring_patterns:
        parts.append("Patterns:\n- " + "\n- ".join(recurring_patterns[:2]))

    if coping_recommendations:
        parts.append("Suggestions:\n- " + "\n- ".join(coping_recommendations[:2]))

    if journaling_insights:
        parts.append("Insight:\n- " + "\n- ".join(journaling_insights[:2]))

    avg_effectiveness = intervention_effectiveness.get("avg_effectiveness_rating")
    if avg_effectiveness is not None:
        parts.append(
            f"Intervention trend:\n- Average effectiveness so far: {avg_effectiveness}"
        )

    if follow_up_required:
        follow_up_lines: list[str] = []

        if follow_up_title:
            follow_up_lines.append(f"Follow-up plan: {follow_up_title}.")
        else:
            follow_up_lines.append("Follow-up plan: Next continuity step prepared.")

        readable_due_at = _format_follow_up_timing(follow_up_due_at)
        if readable_due_at:
            follow_up_lines.append(f"Reminder timing: {readable_due_at}.")
        else:
            follow_up_lines.append("Reminder timing: scheduled for the next check-in window.")

        if follow_up_delivery_channel:
            follow_up_lines.append(f"Delivery channel: {follow_up_delivery_channel}.")

        if scheduler_backend:
            follow_up_lines.append(f"Scheduler backend: {scheduler_backend}.")

        parts.append("Follow-up:\n- " + "\n- ".join(follow_up_lines))

    if follow_up_suggestions:
        parts.append("Next:\n- " + follow_up_suggestions[0])

    return "\n\n".join(part for part in parts if part).strip()


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
Use coping recommendations, trend summaries, and follow-up suggestions selectively instead of repeating everything.
Adapt the tone to the user's support-style preferences when available.
If a follow-up plan exists, briefly mention the continuity step, reminder timing, and that the next step has been prepared.
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
        f"Progress summary:\n{state.get('progress_summary', '')}\n\n"
        f"Support progress summary:\n{state.get('support_progress_summary', '')}\n\n"
        f"Recurring patterns:\n{state.get('recurring_patterns', [])}\n\n"
        f"Intervention effectiveness:\n{state.get('intervention_effectiveness', {})}\n\n"
        f"Coping recommendations:\n{state.get('coping_recommendations', [])}\n\n"
        f"Journaling insights:\n{state.get('journaling_insights', [])}\n\n"
        f"Follow-up suggestions:\n{state.get('follow_up_suggestions', [])}\n\n"
        f"Follow-up required:\n{state.get('follow_up_required', False)}\n\n"
        f"Follow-up plan title:\n{state.get('follow_up_plan_title', '')}\n\n"
        f"Follow-up due at:\n{state.get('follow_up_due_at', '')}\n\n"
        f"Follow-up delivery channel:\n{state.get('follow_up_delivery_channel', '')}\n\n"
        f"Scheduler backend:\n{state.get('scheduler_backend', '')}\n\n"
        "Compose the final response."
    )
    final_response = _sanitize_text(
        llm.generate_text(
            state["provider"],
            system_prompt,
            user_prompt,
            agent_name="response_composer",
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