from __future__ import annotations

from ollama import Client as OllamaClient
from openai import OpenAI

from mental_wellbeing_api.core.config import get_settings


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def generate_text(self, provider: str, system_prompt: str, user_prompt: str) -> str:
        normalized_provider = provider.strip().lower()

        if normalized_provider == "mock":
            return f"[mock-response] {user_prompt}"

        if normalized_provider == "openai":
            if not self.settings.openai_api_key:
                return "[openai-unavailable] OPENAI_API_KEY not configured"

            try:
                client = OpenAI(api_key=self.settings.openai_api_key)
                response = client.responses.create(
                    model=self.settings.openai_model,
                    input=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                return response.output_text.strip()
            except Exception as exc:
                return f"[openai-error] {exc}"

        if normalized_provider == "ollama":
            try:
                client = OllamaClient(host=self.settings.ollama_base_url)
                response = client.chat(
                    model=self.settings.ollama_default_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                return response["message"]["content"].strip()
            except Exception as exc:
                return f"[ollama-error] {exc}"

        return f"[unsupported-provider] {provider}"