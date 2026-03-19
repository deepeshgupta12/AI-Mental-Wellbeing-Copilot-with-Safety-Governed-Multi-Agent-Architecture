from __future__ import annotations

from ollama import Client as OllamaClient
from openai import OpenAI

from mental_wellbeing_api.core.config import get_settings
from mental_wellbeing_api.services.agent_model_assignment_service import (
    AgentModelAssignmentService,
)


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.assignment_service = AgentModelAssignmentService()

    def _fallback_text(self, agent_name: str | None) -> str:
        fallback_map = {
            "input_structuring": "User wants help unpacking overwhelm at work and is looking for clear emotional support.",
            "reflective_support": "It sounds like work has been feeling heavy, and it makes sense that you want to understand it more clearly.",
            "behavioral_activation": "Try choosing one very small step today so the situation feels more workable, not more perfect.",
            "cbt_reframing": "One possibility is that your mind is treating a hard moment like a total pattern. We can slow that down and look at it more carefully.",
            "distress_stabilization": "Let's narrow the goal to the next few minutes and focus on one steadying action at a time.",
            "sleep_recovery": "Let's keep tonight simple and focus on one small wind-down step that feels realistic.",
            "social_support": "You do not have to carry this alone. We can identify one low-pressure way to reconnect with support.",
            "journaling_insight": "There may be a pattern here worth naming more clearly before trying to solve all of it at once.",
            "habit_care_plan": "Let's make this smaller and more repeatable so it can actually fit into your day.",
            "response_composer": "It sounds like this has been weighing on you. Let's take one clear next step together.",
        }
        return fallback_map.get(
            agent_name or "",
            "I'm here with you, and we can take this one small step at a time.",
        )

    def _mock_text(self, agent_name: str | None) -> str:
        mock_map = {
            "input_structuring": "User wants to unpack overwhelm at work and understand what is making it feel heavy.",
            "reflective_support": "It sounds like work has been emotionally heavy, and slowing down to understand that makes sense.",
            "behavioral_activation": "Choose one tiny next step today so the day feels slightly more manageable.",
            "cbt_reframing": "A hard day at work does not automatically mean everything is going wrong. We can look at the thought more carefully.",
            "distress_stabilization": "For the next two minutes, focus only on grounding and getting a little steadier.",
            "sleep_recovery": "Keep tonight simple and choose one calming wind-down cue you can repeat.",
            "social_support": "Think of one safe person you could reach out to without needing the perfect words.",
            "journaling_insight": "There may be a repeating emotional pattern here that is worth naming before solving.",
            "habit_care_plan": "Build the smallest version of the habit so it is easy to restart tomorrow too.",
            "response_composer": "It sounds like this has been weighing on you, and we can take it one clear step at a time.",
        }
        return mock_map.get(agent_name or "", self._fallback_text(agent_name))

    def generate_text(
        self,
        provider: str,
        system_prompt: str,
        user_prompt: str,
        *,
        agent_name: str | None = None,
    ) -> str:
        resolution = self.assignment_service.resolve(
            provider=provider,
            agent_name=agent_name,
        )
        normalized_provider = resolution["provider"]
        assigned_model = resolution.get("model")

        if normalized_provider == "mock":
            return self._mock_text(agent_name)

        if normalized_provider == "openai":
            if not self.settings.openai_api_key:
                return self._fallback_text(agent_name)

            try:
                client = OpenAI(api_key=self.settings.openai_api_key)
                response = client.responses.create(
                    model=assigned_model or self.settings.openai_model,
                    input=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                text = (response.output_text or "").strip()
                return text or self._fallback_text(agent_name)
            except Exception:
                return self._fallback_text(agent_name)

        if normalized_provider == "ollama":
            try:
                client = OllamaClient(host=self.settings.ollama_base_url)
                response = client.chat(
                    model=assigned_model or self.settings.ollama_default_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                text = (response.get("message", {}).get("content") or "").strip()
                return text or self._fallback_text(agent_name)
            except Exception:
                return self._fallback_text(agent_name)

        return self._fallback_text(agent_name)