from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.models.memory_chunk import MemoryChunk
from mental_wellbeing_api.services.embeddings_service import EmbeddingsService


@dataclass
class MemoryRecallItem:
    source_type: str
    source_id: str
    memory_kind: str
    content: str
    importance_score: float | None
    relevance_score: float
    created_at: datetime | None


class MemoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.embeddings = EmbeddingsService()

    def _infer_memory_kind(self, source_type: str, content: str) -> str:
        normalized_source = source_type.strip().lower()
        normalized_content = content.lower()

        if normalized_source in {"user_preference", "preference", "support_preference"}:
            return "preference"

        if normalized_source in {"trend_snapshot", "journal_theme", "trigger_cluster"}:
            return "semantic"

        if normalized_source in {"intervention_log", "action_plan"}:
            return "helpful_strategy"

        if any(
            phrase in normalized_content
            for phrase in [
                "helped before",
                "worked for me",
                "this helped",
                "i should try again",
                "short walk",
                "breathing exercise",
                "journal for",
            ]
        ):
            return "helpful_strategy"

        if normalized_source in {"check_in", "journal_entry", "conversation_message"}:
            return "episodic"

        return "episodic"

    def _estimate_importance_score(self, source_type: str, content: str) -> float:
        normalized = content.lower().strip()
        score = 0.35

        if source_type in {"journal_entry", "conversation_message"}:
            score += 0.15
        if source_type == "check_in":
            score += 0.1

        if len(normalized) > 180:
            score += 0.1

        if any(word in normalized for word in ["panic", "overwhelmed", "burnout", "unsafe"]):
            score += 0.15

        if any(word in normalized for word in ["helped", "worked", "useful", "better"]):
            score += 0.15

        return round(min(score, 1.0), 2)

    def _text_overlap_score(self, query: str, content: str) -> float:
        query_tokens = {token for token in query.lower().split() if len(token) > 2}
        content_tokens = {token for token in content.lower().split() if len(token) > 2}
        if not query_tokens or not content_tokens:
            return 0.0
        overlap = len(query_tokens & content_tokens)
        return min(overlap / max(len(query_tokens), 1), 1.0)

    def _recency_score(self, created_at: datetime | None) -> float:
        if created_at is None:
            return 0.0

        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        age_hours = max((datetime.now(timezone.utc) - created_at).total_seconds() / 3600, 0.0)
        return max(0.0, min(1.0, math.exp(-age_hours / 168)))

    def _preference_alignment_score(
        self,
        content: str,
        preference_signals: dict[str, str] | None = None,
    ) -> float:
        if not preference_signals:
            return 0.0

        lowered_content = content.lower()
        score = 0.0

        support_style = preference_signals.get("support_style", "").lower()
        preferred_support_mode = preference_signals.get("preferred_support_mode", "").lower()
        focus_areas = preference_signals.get("focus_areas", "").lower()

        if support_style and support_style in lowered_content:
            score += 0.2
        if preferred_support_mode and preferred_support_mode in lowered_content:
            score += 0.25

        if focus_areas:
            focus_tokens = [token.strip() for token in focus_areas.split(",") if token.strip()]
            for token in focus_tokens[:4]:
                if token in lowered_content:
                    score += 0.1

        return min(score, 0.35)

    async def add_memory(
        self,
        *,
        user_id: str,
        source_type: str,
        source_id: str,
        content: str,
        memory_kind: str | None = None,
        importance_score: float | None = None,
    ) -> None:
        cleaned = " ".join(content.split()).strip()
        if not cleaned:
            return

        resolved_memory_kind = memory_kind or self._infer_memory_kind(source_type, cleaned)
        resolved_importance = (
            importance_score
            if importance_score is not None
            else self._estimate_importance_score(source_type, cleaned)
        )

        item = MemoryChunk(
            user_id=user_id,
            source_type=source_type,
            source_id=source_id,
            memory_kind=resolved_memory_kind,
            content=cleaned,
            embedding=self.embeddings.embed_text(cleaned),
            importance_score=resolved_importance,
        )
        self.session.add(item)
        await self.session.commit()

    async def recall(
        self,
        *,
        user_id: str,
        query: str,
        limit: int = 3,
        memory_kinds: list[str] | None = None,
        preference_signals: dict[str, str] | None = None,
    ) -> list[MemoryRecallItem]:
        query_embedding = self.embeddings.embed_text(query)

        try:
            stmt = select(
                MemoryChunk,
                MemoryChunk.embedding.cosine_distance(query_embedding).label("distance"),
            ).where(MemoryChunk.user_id == user_id)

            if memory_kinds:
                stmt = stmt.where(MemoryChunk.memory_kind.in_(memory_kinds))

            stmt = stmt.limit(max(limit * 5, 10))
            rows = (await self.session.execute(stmt)).all()

            scored_items: list[MemoryRecallItem] = []
            for memory_chunk, distance in rows:
                similarity = 1.0 - float(distance or 1.0)
                overlap_score = self._text_overlap_score(query, memory_chunk.content)
                recency_score = self._recency_score(memory_chunk.created_at)
                importance = memory_chunk.importance_score or 0.0
                preference_alignment = self._preference_alignment_score(
                    memory_chunk.content,
                    preference_signals,
                )

                blended_score = (
                    (similarity * 0.38)
                    + (overlap_score * 0.22)
                    + (recency_score * 0.14)
                    + (importance * 0.14)
                    + (preference_alignment * 0.12)
                )

                scored_items.append(
                    MemoryRecallItem(
                        source_type=memory_chunk.source_type,
                        source_id=memory_chunk.source_id,
                        memory_kind=memory_chunk.memory_kind,
                        content=memory_chunk.content,
                        importance_score=memory_chunk.importance_score,
                        relevance_score=round(blended_score, 4),
                        created_at=memory_chunk.created_at,
                    )
                )

            if scored_items:
                scored_items.sort(key=lambda item: item.relevance_score, reverse=True)
                return scored_items[:limit]

        except Exception:
            await self.session.rollback()

        fallback_stmt = (
            select(MemoryChunk)
            .where(MemoryChunk.user_id == user_id)
            .order_by(desc(MemoryChunk.created_at))
            .limit(limit)
        )
        if memory_kinds:
            fallback_stmt = fallback_stmt.where(MemoryChunk.memory_kind.in_(memory_kinds))

        fallback = await self.session.scalars(fallback_stmt)
        return [
            MemoryRecallItem(
                source_type=item.source_type,
                source_id=item.source_id,
                memory_kind=item.memory_kind,
                content=item.content,
                importance_score=item.importance_score,
                relevance_score=0.0,
                created_at=item.created_at,
            )
            for item in fallback.all()
        ]

    async def recall_texts(
        self,
        *,
        user_id: str,
        query: str,
        limit: int = 3,
        memory_kinds: list[str] | None = None,
        preference_signals: dict[str, str] | None = None,
    ) -> list[str]:
        recalled = await self.recall(
            user_id=user_id,
            query=query,
            limit=limit,
            memory_kinds=memory_kinds,
            preference_signals=preference_signals,
        )
        return [item.content for item in recalled]

    def build_context_block(
        self,
        recalled_items: list[MemoryRecallItem],
        preference_signals: dict[str, str] | None = None,
        what_helped_before: list[str] | None = None,
    ) -> str:
        sections: list[str] = []

        if preference_signals:
            preference_lines = [f"- {key}: {value}" for key, value in preference_signals.items()]
            sections.append("Preference signals:\n" + "\n".join(preference_lines))

        if recalled_items:
            memory_lines = [
                f"- [{item.memory_kind}] {item.content}"
                for item in recalled_items
            ]
            sections.append("Relevant prior memories:\n" + "\n".join(memory_lines))
        else:
            sections.append("Relevant prior memories:\n- No relevant prior memory was recalled.")

        if what_helped_before:
            helpful_lines = [f"- {item}" for item in what_helped_before]
            sections.append("What helped before:\n" + "\n".join(helpful_lines))

        return "\n\n".join(sections)