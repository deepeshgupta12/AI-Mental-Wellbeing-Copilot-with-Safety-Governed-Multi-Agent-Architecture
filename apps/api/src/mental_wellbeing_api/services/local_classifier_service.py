from __future__ import annotations

from typing import Any


class LocalClassifierService:
    HIGH_RISK_HINTS = ["kill myself", "end my life", "suicide", "want to die", "hurt myself"]
    MEDIUM_RISK_HINTS = ["panic attack", "can't breathe", "losing control", "breaking down"]

    ANXIOUS_HINTS = ["panic", "anxious", "overwhelmed", "can't breathe"]
    LOW_ENERGY_HINTS = ["tired", "exhausted", "drained", "burnout"]
    SADNESS_HINTS = ["sad", "hopeless", "low", "down", "alone", "lonely"]

    def pre_screen(self, text: str) -> dict[str, Any]:
        lowered = text.lower()

        risk_guess = "low"
        if any(hint in lowered for hint in self.HIGH_RISK_HINTS):
            risk_guess = "high"
        elif any(hint in lowered for hint in self.MEDIUM_RISK_HINTS):
            risk_guess = "medium"

        tone_guess = "steady"
        emotion_guess = "reflective"

        if any(hint in lowered for hint in self.ANXIOUS_HINTS):
            tone_guess = "distressed"
            emotion_guess = "anxious"
        elif any(hint in lowered for hint in self.LOW_ENERGY_HINTS):
            tone_guess = "fatigued"
            emotion_guess = "exhaustion"
        elif any(hint in lowered for hint in self.SADNESS_HINTS):
            tone_guess = "heavy"
            emotion_guess = "sadness"

        return {
            "risk_guess": risk_guess,
            "tone_guess": tone_guess,
            "emotion_guess": emotion_guess,
            "source": "local_classifier_experiment",
        }