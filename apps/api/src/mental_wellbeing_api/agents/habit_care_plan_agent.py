from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_prompt
from mental_wellbeing_api.services.llm_service import LLMService


def _build_habit_recommendations(state: AgentRuntimeState) -> list[str]:
    language = (
        state.get("preferred_language")
        or state.get("content_language")
        or state.get("preference_signals", {}).get("preferred_language")
        or "en"
    )

    if language == "hi":
        recommendations = [
            "इस आदत को किसी ऐसी चीज़ से जोड़ें जो आप पहले से रोज़ करते हैं।",
            "मुश्किल दिनों के लिए एक आसान fallback version तय करें।",
        ]
    elif language == "hinglish":
        recommendations = [
            "Is habit ko kisi aisi cheez ke saath anchor karo jo aap roz waise hi karte ho.",
            "Hard days ke liye ek easy fallback version decide karo jo phir bhi count ho.",
        ]
    else:
        recommendations = [
            "Anchor the habit to something that already happens daily.",
            "Decide on a fallback version that still counts on hard days.",
        ]

    support_style = state.get("preference_signals", {}).get("support_style", "").lower()
    if support_style in {"direct", "structured", "action-oriented"}:
        if language == "hi":
            recommendations.insert(0, "आदत इतनी स्पष्ट रखें कि आज हुआ या नहीं, यह पता चल सके।")
        elif language == "hinglish":
            recommendations.insert(0, "Habit itni measurable rakho ki aaj hui ya nahi, ye clear ho.")
        else:
            recommendations.insert(0, "Make the habit measurable enough to know whether it happened today.")

    return recommendations[:3]


def run_habit_care_plan_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    llm = LLMService()
    language = (
        state.get("preferred_language")
        or state.get("content_language")
        or state.get("preference_signals", {}).get("preferred_language")
        or "en"
    )

    system_prompt = load_prompt(
        "agents/habit_care_plan.txt",
        """
You are a non-clinical wellbeing assistant helping the user build a small, sustainable care plan.
Focus on realistic consistency, not intensity. Keep the plan very small and specific.
""",
    )

    coping_recommendations = _build_habit_recommendations(state)

    if language == "hi":
        user_instruction = "एक बहुत छोटा habit plan, एक trigger, और एक आसान fallback option लिखिए।"
    elif language == "hinglish":
        user_instruction = "Ek chhota habit plan, ek trigger, aur ek easy fallback option likho."
    else:
        user_instruction = "Write a brief response with one tiny habit plan, one trigger, and one easy fallback option."

    user_prompt = (
        f"User input:\n{state['user_input']}\n\n"
        f"Structured summary:\n{state.get('structured_input', '')}\n\n"
        f"Session context:\n{state.get('session_context', '')}\n\n"
        f"Preferred support style:\n{state.get('preference_signals', {}).get('support_style', '')}\n\n"
        f"Preferred language:\n{language}\n\n"
        f"{user_instruction}"
    )
    specialist_response = llm.generate_text(
        state["provider"],
        system_prompt,
        user_prompt,
        agent_name="habit_care_plan",
    )

    if language == "hi":
        journaling_insights = [
            "लगातार perfect होने से ज़्यादा मदद restart करना करता है।",
        ]
        follow_up_suggestions = [
            "मैं इसे morning, evening, या after-work version में बदलने में मदद कर सकता हूँ।",
            "अगर यह अभी भी भारी लग रहा है, तो मैं इसे एक-minute baseline तक छोटा कर सकता हूँ।",
        ]
    elif language == "hinglish":
        journaling_insights = [
            "Perfect hone se zyada zaroori hota hai ki habit ko restart karna easy ho.",
        ]
        follow_up_suggestions = [
            "Main ise morning, evening, ya after-work version mein convert karne mein help kar sakta hoon.",
            "Agar ye abhi bhi heavy lag raha hai, to main ise one-minute baseline tak chhota kar sakta hoon.",
        ]
    else:
        journaling_insights = [
            "Consistency usually improves when the habit is easier to restart than to perfect.",
        ]
        follow_up_suggestions = [
            "I can help turn this into a morning, evening, or after-work version.",
            "If the plan still feels heavy, I can reduce it to a one-minute baseline.",
        ]

    state = {
        **state,
        "reflective_response": specialist_response,
        "specialist_response": specialist_response,
        "coping_recommendations": coping_recommendations,
        "journaling_insights": journaling_insights,
        "follow_up_suggestions": follow_up_suggestions,
        "care_plan_required": True,
        "care_program_key": "habit_care_plan",
        "care_plan_language": language,
    }
    state = append_execution_event(
        state,
        node_name="habit_care_plan",
        metadata={
            "response_length": len(specialist_response),
            "coping_recommendation_count": len(coping_recommendations),
            "language": language,
        },
    )
    state = append_handoff(
        state,
        from_agent="habit_care_plan",
        to_agent="response_composer",
        reason="habit care plan draft prepared",
    )
    return state