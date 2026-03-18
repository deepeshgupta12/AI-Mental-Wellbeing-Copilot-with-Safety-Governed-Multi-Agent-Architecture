from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState

HIGH_DISTRESS_HINTS = ["panic", "can't breathe", "losing control", "breaking down"]
LOW_ENERGY_HINTS = ["tired", "exhausted", "drained", "burnout", "heavy"]
SADNESS_HINTS = ["sad", "hopeless", "low", "down", "alone", "lonely"]
FRUSTRATION_HINTS = ["angry", "frustrated", "irritated", "annoyed"]
SELF_CRITICAL_HINTS = ["always ruin", "never good enough", "failure", "worthless", "should have"]


def run_tone_emotion_analyzer_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    text = " ".join(
        [
            state.get("user_input", ""),
            state.get("structured_input", ""),
        ]
    ).lower()

    tone_label = "steady"
    emotion_label = "reflective"
    emotion_intensity = "low"

    if any(token in text for token in HIGH_DISTRESS_HINTS):
        tone_label = "distressed"
        emotion_label = "anxious"
        emotion_intensity = "high"
    elif any(token in text for token in SELF_CRITICAL_HINTS):
        tone_label = "self-critical"
        emotion_label = "shame"
        emotion_intensity = "medium"
    elif any(token in text for token in LOW_ENERGY_HINTS):
        tone_label = "fatigued"
        emotion_label = "exhaustion"
        emotion_intensity = "medium"
    elif any(token in text for token in SADNESS_HINTS):
        tone_label = "heavy"
        emotion_label = "sadness"
        emotion_intensity = "medium"
    elif any(token in text for token in FRUSTRATION_HINTS):
        tone_label = "tense"
        emotion_label = "frustration"
        emotion_intensity = "medium"

    emotional_signals = [tone_label, emotion_label, emotion_intensity]

    state = {
        **state,
        "tone_label": tone_label,
        "emotion_label": emotion_label,
        "emotion_intensity": emotion_intensity,
        "emotional_signals": emotional_signals,
    }
    state = append_execution_event(
        state,
        node_name="tone_emotion_analyzer",
        metadata={
            "tone_label": tone_label,
            "emotion_label": emotion_label,
            "emotion_intensity": emotion_intensity,
        },
    )
    state = append_handoff(
        state,
        from_agent="tone_emotion_analyzer",
        to_agent="intent_router",
        reason="tone and emotion signals extracted",
    )
    return state