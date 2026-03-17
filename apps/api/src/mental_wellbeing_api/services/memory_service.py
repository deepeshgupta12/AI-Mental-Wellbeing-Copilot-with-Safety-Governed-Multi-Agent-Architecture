from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.models.memory_chunk import MemoryChunk
from mental_wellbeing_api.services.embeddings_service import EmbeddingsService


class MemoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.embeddings = EmbeddingsService()

    async def add_memory(
        self,
        *,
        user_id: str,
        source_type: str,
        source_id: str,
        content: str,
    ) -> None:
        cleaned = " ".join(content.split()).strip()
        if not cleaned:
            return

        item = MemoryChunk(
            user_id=user_id,
            source_type=source_type,
            source_id=source_id,
            content=cleaned,
            embedding=self.embeddings.embed_text(cleaned),
        )
        self.session.add(item)
        await self.session.commit()

    async def recall(
        self,
        *,
        user_id: str,
        query: str,
        limit: int = 3,
    ) -> list[str]:
        query_embedding = self.embeddings.embed_text(query)

        try:
            result = await self.session.scalars(
                select(MemoryChunk)
                .where(MemoryChunk.user_id == user_id)
                .order_by(MemoryChunk.embedding.cosine_distance(query_embedding))
                .limit(limit)
            )
            items = list(result.all())
            if items:
                return [item.content for item in items]
        except Exception:
            await self.session.rollback()

        fallback = await self.session.scalars(
            select(MemoryChunk)
            .where(MemoryChunk.user_id == user_id)
            .order_by(desc(MemoryChunk.created_at))
            .limit(limit)
        )
        return [item.content for item in fallback.all()]