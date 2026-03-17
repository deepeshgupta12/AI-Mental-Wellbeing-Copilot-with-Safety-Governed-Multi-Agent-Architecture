from __future__ import annotations

import hashlib
import random

from openai import OpenAI

from mental_wellbeing_api.core.config import get_settings


class EmbeddingsService:
    DIMENSIONS = 1536

    def __init__(self) -> None:
        self.settings = get_settings()

    def embed_text(self, text: str) -> list[float]:
        normalized = " ".join(text.split()).strip()
        if not normalized:
            normalized = "empty"

        if self.settings.openai_api_key:
            client = OpenAI(api_key=self.settings.openai_api_key)
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=normalized,
            )
            return list(response.data[0].embedding)

        return self._pseudo_embedding(normalized)

    def _pseudo_embedding(self, text: str) -> list[float]:
        seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)
        rng = random.Random(seed)
        return [rng.uniform(-1.0, 1.0) for _ in range(self.DIMENSIONS)]