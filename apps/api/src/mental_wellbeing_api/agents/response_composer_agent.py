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


def _safe_specialist_text(state: AgentRuntimeState) -> str:
    specialist_response = _sanitize_text(
        state.get("specialist_response") or state.get("reflective_response", "")
    )
    if specialist_response:
        return specialist_response

    support_mode = (state.get("support_mode") or "").lower()
    fallback_by_mode = {
        "reflective": "It sounds like this has been weighing on you, and slowing down to understand it is a meaningful step.",
        "reflect": "It sounds like this has been weighing on you, and slowing down to understand it is a meaningful step.",
        "activate": "Let's focus on one very small next step so this feels more manageable.",
        "reframe": "We can look at the thought more carefully and separate the hard moment from the harsher conclusion.",
        "recover": "Let's keep this gentle and focus on one realistic recovery step.",
        "connect": "You do not have to carry this alone. We can think about one safe connection point.",
        "journal": "There may be a pattern here worth naming before trying to solve everything at once.",
        "plan": "Let's make this concrete. We can turn this into a small plan that feels realistic today.",
        "stabilize": "For now, let's focus on getting a little steadier, one moment at a time.",
    }
    return fallback_by_mode.get(
        support_mode,
        "It sounds like this has been difficult, and we can take it one clear step at a time.",
    )


def _resolve_language(state: AgentRuntimeState) -> str:
    return (
        state.get("preferred_language")
        or state.get("content_language")
        or state.get("preference_signals", {}).get("preferred_language")
        or "en"
    )


def _build_mock_final_response(state: AgentRuntimeState) -> str:
    support_mode = (state.get("support_mode") or "").lower()
    support_style = (state.get("preference_signals") or {}).get("support_style", "").lower()
    coping_recommendations = state.get("coping_recommendations", [])
    follow_up_suggestions = state.get("follow_up_suggestions", [])
    language = _resolve_language(state)

    if language == "hi":
        mode_openers = {
            "reflect": "लगता है यह बात आपके मन पर काफी असर डाल रही है।",
            "activate": "इसे व्यावहारिक और साफ़ रखते हैं।",
            "reframe": "इसे थोड़ा धीमे होकर ज़्यादा स्पष्ट रूप से देखते हैं।",
            "recover": "अभी इसे कोमल और संभालने लायक रखते हैं।",
            "connect": "आपको यह अकेले नहीं उठाना है।",
            "journal": "यहाँ शायद कुछ ऐसा है जिसे थोड़ा और साफ़ नाम देना ज़रूरी है।",
            "plan": "इसे ठोस बनाते हैं।",
            "stabilize": "अभी अगले सुरक्षित और स्थिर कदम पर ध्यान देते हैं।",
        }
    elif language == "hinglish":
        mode_openers = {
            "reflect": "Lagta hai ye baat aap par kaafi weight daal rahi hai.",
            "activate": "Chalo ise practical aur clear rakhte hain.",
            "reframe": "Chalo ise thoda dheere hokar zyada clearly dekhte hain.",
            "recover": "Abhi ise gentle aur manageable rakhte hain.",
            "connect": "Aapko ye sab akela nahi sambhalna hai.",
            "journal": "Yahan shayad kuch aisa hai jise thoda aur clearly naam dena zaroori hai.",
            "plan": "Chalo ise concrete banate hain.",
            "stabilize": "Abhi next safe aur steady step par focus karte hain.",
        }
    else:
        mode_openers = {
            "reflect": "It sounds like this has been weighing on you.",
            "activate": "Let's keep this practical and clear.",
            "reframe": "Let's slow this down and look at it more clearly.",
            "recover": "Let's keep this gentle and manageable for right now.",
            "connect": "You do not have to carry this alone.",
            "journal": "There may be something important here worth naming more clearly.",
            "plan": "Let's make this concrete.",
            "stabilize": "Let's focus on the next safe and steady step.",
        }

    opener = mode_openers.get(
        support_mode,
        {
            "hi": "मैं आपके साथ हूँ, और हम इसे एक-एक कदम करके देख सकते हैं।",
            "hinglish": "Main aapke saath hoon, aur hum ise ek-ek step mein dekh sakte hain.",
        }.get(language, "I'm here with you, and we can take this one step at a time."),
    )

    specialist_text = _safe_specialist_text(state)
    parts: list[str] = [opener]

    if language == "hi":
        if support_mode == "plan":
            parts.append(
                "हम इसे छोटा और दोहराने लायक बना सकते हैं ताकि इसे निभाना आसान लगे।"
                if support_style == "direct"
                else "हम इसे एक छोटे और वास्तविक प्लान में बदल सकते हैं।"
            )
        elif support_mode == "activate":
            parts.append("आज सिर्फ एक बहुत छोटा अगला कदम चुनिए।")
        elif support_mode == "recover":
            parts.append("अभी सब कुछ हल करने के बजाय एक शांत करने वाले कदम पर ध्यान दें।")
        elif support_mode == "reframe":
            parts.append("एक कठिन पल पूरी तस्वीर तय नहीं करता।")
        elif support_mode == "reflect":
            parts.append("इसे और स्पष्ट समझना चाहना बिल्कुल स्वाभाविक है।")
    elif language == "hinglish":
        if support_mode == "plan":
            parts.append(
                "Hum ise chhota aur repeatable bana sakte hain taaki follow through easy lage."
                if support_style == "direct"
                else "Hum ise ek realistic chhote plan mein convert kar sakte hain."
            )
        elif support_mode == "activate":
            parts.append("Aaj sirf ek bahut chhota next step choose karo.")
        elif support_mode == "recover":
            parts.append("Abhi sab solve karne ki jagah ek calming step par focus karo.")
        elif support_mode == "reframe":
            parts.append("Ek tough moment poori story define nahi karta.")
        elif support_mode == "reflect":
            parts.append("Isse aur clearly samajhna bilkul valid hai.")
    else:
        if support_mode == "plan":
            parts.append(
                "We can make this smaller and more repeatable so it feels easier to follow through."
                if support_style == "direct"
                else "We can turn this into a small plan that feels realistic and not overwhelming."
            )
        elif support_mode == "activate":
            parts.append("Choose one tiny next step today so this feels slightly more manageable.")
        elif support_mode == "recover":
            parts.append("For now, focus on one calming action rather than solving everything at once.")
        elif support_mode == "reframe":
            parts.append("A hard moment does not automatically define the whole picture.")
        elif support_mode == "reflect":
            parts.append("It makes sense that you want to understand this more clearly.")

    if coping_recommendations:
        parts.append(coping_recommendations[0])
    elif specialist_text and specialist_text not in parts:
        parts.append(specialist_text)

    if follow_up_suggestions:
        parts.append(follow_up_suggestions[0])

    final_text = " ".join(part.strip() for part in parts if part).strip()
    return _normalize_visible_response(final_text)


def run_response_composer_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    language = _resolve_language(state)

    if state.get("safety_override"):
        if language == "hi":
            final_response = (
                "मुझे खुशी है कि आपने संपर्क किया। जो आपने साझा किया वह गंभीर लग रहा है, इसलिए मैं सावधानी से जवाब देना चाहता हूँ। "
                "अगर आपको लगता है कि आप तुरंत खतरे में हैं या इन विचारों पर अमल कर सकते हैं, तो अभी स्थानीय आपातकालीन सेवा या संकट हेल्पलाइन से संपर्क करें, "
                "और किसी भरोसेमंद व्यक्ति को अपने पास रहने के लिए कहें। "
                "अगर तत्काल खतरा नहीं है, तो बताइए क्या आप अभी अगला सुरक्षित कदम लेने में मदद चाहते हैं।"
            )
        elif language == "hinglish":
            final_response = (
                "Accha hua aapne reach out kiya. Jo aapne share kiya woh serious lag raha hai, isliye main carefully respond kar raha hoon. "
                "Agar aapko lag raha hai ki immediate danger hai ya aap in thoughts par act kar sakte hain, to abhi local emergency services ya crisis helpline se contact karo, "
                "aur kisi trusted person ko apne saath rehne ke liye bolo. "
                "Agar immediate danger nahi hai, to batao kya tum abhi next safe step lene mein help chahte ho."
            )
        else:
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
            metadata={"mode": "safety_override", "response_length": len(final_response), "language": language},
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
                "language": language,
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
Respect the user's preferred language when provided.
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
        f"Preferred language:\n{language}\n\n"
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
            "language": language,
        },
    )
    state = append_handoff(
        state,
        from_agent="response_composer",
        to_agent="policy_guardrail",
        reason="final response composed",
    )
    return state