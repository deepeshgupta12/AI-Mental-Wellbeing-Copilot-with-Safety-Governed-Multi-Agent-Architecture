from __future__ import annotations

import json
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from ollama import Client as OllamaClient
from openai import OpenAI

from mental_wellbeing_api.core.config import get_settings
from mental_wellbeing_api.services.agent_model_assignment_service import (
    AgentModelAssignmentService,
)


class LLMService:
    _ollama_model_cache: dict[tuple[str, str], bool] = {}

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
            "crisis_escalation": "What you shared may need immediate human support right now. Please contact local emergency services or a crisis line now, and reach out to a trusted person if you can.",
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
            "crisis_escalation": "This sounds serious enough that immediate human support matters most right now.",
        }
        return mock_map.get(agent_name or "", self._fallback_text(agent_name))

    def _generate_openai_text(
        self,
        *,
        model: str,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        if not self.settings.openai_api_key:
            return ""

        client = OpenAI(api_key=self.settings.openai_api_key)
        response = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return (response.output_text or "").strip()

    def _generate_ollama_text(
        self,
        *,
        model: str,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        client = OllamaClient(host=self.settings.ollama_base_url)
        response = client.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return (response.get("message", {}).get("content") or "").strip()

    def _ollama_model_available(self, model: str | None) -> bool:
        resolved_model = (model or "").strip()
        if not resolved_model:
            return False

        cache_key = (self.settings.ollama_base_url.rstrip("/"), resolved_model)
        cached = self._ollama_model_cache.get(cache_key)
        if cached is not None:
            return cached

        tags_url = urljoin(f"{self.settings.ollama_base_url.rstrip('/')}/", "api/tags")

        try:
            request = Request(tags_url, method="GET")
            with urlopen(request, timeout=2) as response:
                raw = response.read().decode("utf-8")
                payload = json.loads(raw)
        except (URLError, TimeoutError, ValueError, OSError):
            self._ollama_model_cache[cache_key] = False
            return False

        models = payload.get("models", [])
        available_names: set[str] = set()

        if isinstance(models, list):
            for item in models:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("name") or "").strip()
                model_name = str(item.get("model") or "").strip()
                if name:
                    available_names.add(name)
                if model_name:
                    available_names.add(model_name)

        available = (
            resolved_model in available_names
            or f"{resolved_model}:latest" in available_names
            or any(name.startswith(f"{resolved_model}:") for name in available_names)
        )

        self._ollama_model_cache[cache_key] = available
        return available

    def generate_text(
        self,
        provider: str,
        system_prompt: str,
        user_prompt: str,
        *,
        agent_name: str | None = None,
        risk_level: str | None = None,
        final_stage: bool = False,
    ) -> str:
        resolution = self.assignment_service.resolve(
            provider=provider,
            agent_name=agent_name,
            risk_level=risk_level,
            final_stage=final_stage,
        )
        normalized_provider = resolution["provider"]
        assigned_model = resolution.get("model")

        if normalized_provider == "mock":
            return self._mock_text(agent_name)

        if normalized_provider == "openai":
            try:
                text = self._generate_openai_text(
                    model=assigned_model or self.settings.openai_model,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                )
                if text:
                    return text
            except Exception:
                pass

            ollama_model = self.settings.ollama_default_model
            if self._ollama_model_available(ollama_model):
                try:
                    text = self._generate_ollama_text(
                        model=ollama_model,
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                    )
                    if text:
                        return text
                except Exception:
                    pass

            return self._fallback_text(agent_name)

        if normalized_provider == "ollama":
            ollama_model = assigned_model or self.settings.ollama_default_model

            if self._ollama_model_available(ollama_model):
                try:
                    text = self._generate_ollama_text(
                        model=ollama_model,
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                    )
                    if text:
                        return text
                except Exception:
                    pass

            try:
                text = self._generate_openai_text(
                    model=self.settings.openai_model,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                )
                if text:
                    return text
            except Exception:
                pass

            return self._fallback_text(agent_name)

        return self._fallback_text(agent_name)