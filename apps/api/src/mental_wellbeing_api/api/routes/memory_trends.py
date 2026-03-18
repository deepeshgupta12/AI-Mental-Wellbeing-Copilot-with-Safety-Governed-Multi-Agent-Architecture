from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mental_wellbeing_api.api.deps import db_session_dep
from mental_wellbeing_api.models.check_in import CheckIn
from mental_wellbeing_api.models.conversation import ConversationMessage, ConversationSession
from mental_wellbeing_api.models.journal_entry import JournalEntry
from mental_wellbeing_api.models.journal_theme import JournalTheme
from mental_wellbeing_api.models.memory_chunk import MemoryChunk
from mental_wellbeing_api.models.trend_snapshot import TrendSnapshot
from mental_wellbeing_api.models.trigger_cluster import TriggerCluster
from mental_wellbeing_api.models.user import User
from mental_wellbeing_api.schemas.memory_trends import (
    MemoryItemResponse,
    MemorySummaryResponse,
    TrendSummaryResponse,
)
from mental_wellbeing_api.services.preference_service import PreferenceService

router = APIRouter(prefix="/memory-trends", tags=["memory-trends"])


def _truncate(text: str | None, max_length: int = 140) -> str:
    if not text:
        return ""
    cleaned = " ".join(text.split())
    if len(cleaned) <= max_length:
        return cleaned
    return cleaned[: max_length - 3] + "..."


def _as_float(value: object) -> float | None:
    if value is None:
        return None
    return round(float(value), 2)


@router.get("/memory-summary", response_model=MemorySummaryResponse)
async def get_memory_summary(
    user_id: UUID,
    session: AsyncSession = Depends(db_session_dep),
) -> MemorySummaryResponse:
    user = await session.scalar(
        select(User)
        .options(selectinload(User.profile))
        .where(User.id == str(user_id))
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    recent_check_ins = list(
        (
            await session.scalars(
                select(CheckIn)
                .where(CheckIn.user_id == str(user_id))
                .order_by(CheckIn.created_at.desc())
                .limit(3)
            )
        ).all()
    )

    recent_journals = list(
        (
            await session.scalars(
                select(JournalEntry)
                .where(JournalEntry.user_id == str(user_id))
                .order_by(JournalEntry.created_at.desc())
                .limit(3)
            )
        ).all()
    )

    recent_sessions = list(
        (
            await session.scalars(
                select(ConversationSession)
                .where(ConversationSession.user_id == str(user_id))
                .order_by(ConversationSession.updated_at.desc())
                .limit(3)
            )
        ).all()
    )

    recent_memory_chunks = list(
        (
            await session.scalars(
                select(MemoryChunk)
                .where(MemoryChunk.user_id == str(user_id))
                .order_by(MemoryChunk.created_at.desc())
                .limit(20)
            )
        ).all()
    )

    helpful_before = [
        _truncate(item.content, 120)
        for item in recent_memory_chunks
        if item.memory_kind == "helpful_strategy"
    ][:3]

    recurring_trigger_rows = list(
        (
            await session.scalars(
                select(TriggerCluster)
                .where(TriggerCluster.user_id == str(user_id))
                .order_by(TriggerCluster.frequency.desc(), TriggerCluster.updated_at.desc())
                .limit(5)
            )
        ).all()
    )
    recurring_triggers = [item.cluster_name for item in recurring_trigger_rows]

    recent_theme_rows = (
        await session.execute(
            select(JournalTheme.theme_name, func.count(JournalTheme.id).label("theme_count"))
            .where(JournalTheme.user_id == str(user_id))
            .group_by(JournalTheme.theme_name)
            .order_by(desc("theme_count"), JournalTheme.theme_name.asc())
            .limit(5)
        )
    ).all()
    recent_journal_themes = [row.theme_name for row in recent_theme_rows]

    preference_signals = await PreferenceService(session).get_preference_signals(str(user_id))

    latest_weekly_snapshot = await session.scalar(
        select(TrendSnapshot)
        .where(
            TrendSnapshot.user_id == str(user_id),
            TrendSnapshot.window_type == "weekly_reflection",
        )
        .order_by(TrendSnapshot.created_at.desc())
        .limit(1)
    )

    chunk_lookup: dict[tuple[str, str], MemoryChunk] = {
        (item.source_type, item.source_id): item for item in recent_memory_chunks
    }

    memory_items: list[MemoryItemResponse] = []

    for item in recent_check_ins:
        summary_parts: list[str] = []
        if item.mood_score is not None:
            summary_parts.append(f"Mood {item.mood_score}")
        if item.stress_score is not None:
            summary_parts.append(f"Stress {item.stress_score}")
        if item.energy_score is not None:
            summary_parts.append(f"Energy {item.energy_score}")
        if item.sleep_hours is not None:
            summary_parts.append(f"Sleep {item.sleep_hours}h")
        if item.notes:
            summary_parts.append(_truncate(item.notes, 80))

        linked_chunk = chunk_lookup.get(("check_in", item.id))
        memory_items.append(
            MemoryItemResponse(
                source_type="check_in",
                source_id=item.id,
                title="Check-in snapshot",
                summary=" • ".join(summary_parts) if summary_parts else "Recent check-in recorded",
                created_at=item.created_at,
                memory_kind=linked_chunk.memory_kind if linked_chunk else None,
                importance_score=linked_chunk.importance_score if linked_chunk else None,
            )
        )

    for item in recent_journals:
        linked_chunk = chunk_lookup.get(("journal_entry", item.id))
        memory_items.append(
            MemoryItemResponse(
                source_type="journal_entry",
                source_id=item.id,
                title=item.title or "Journal entry",
                summary=_truncate(item.summary or item.content, 140),
                created_at=item.created_at,
                memory_kind=linked_chunk.memory_kind if linked_chunk else None,
                importance_score=linked_chunk.importance_score if linked_chunk else None,
            )
        )

    for item in recent_sessions:
        memory_items.append(
            MemoryItemResponse(
                source_type="conversation_session",
                source_id=item.id,
                title=item.title or "Conversation session",
                summary=item.session_summary or f"Status: {item.status}",
                created_at=item.updated_at,
                memory_kind="episodic",
                importance_score=None,
            )
        )

    memory_items.sort(key=lambda x: x.created_at, reverse=True)
    memory_items = memory_items[:5]

    return MemorySummaryResponse(
        user_id=user.id,
        display_name=user.profile.display_name if user.profile else None,
        wellbeing_goals=user.profile.wellbeing_goals if user.profile else None,
        recent_memories=memory_items,
        helpful_before=helpful_before,
        recurring_triggers=recurring_triggers,
        preference_signals=preference_signals,
        weekly_reflection_summary=(
            latest_weekly_snapshot.summary_json.get("summary")
            if latest_weekly_snapshot and isinstance(latest_weekly_snapshot.summary_json, dict)
            else None
        ),
        recent_journal_themes=recent_journal_themes,
    )


@router.get("/trend-summary", response_model=TrendSummaryResponse)
async def get_trend_summary(
    user_id: UUID,
    session: AsyncSession = Depends(db_session_dep),
) -> TrendSummaryResponse:
    user_exists = await session.scalar(select(User.id).where(User.id == str(user_id)))
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    check_in_stats = (
        await session.execute(
            select(
                func.count(CheckIn.id),
                func.avg(CheckIn.mood_score),
                func.avg(CheckIn.stress_score),
                func.avg(CheckIn.energy_score),
                func.avg(CheckIn.sleep_hours),
                func.max(CheckIn.created_at),
            ).where(CheckIn.user_id == str(user_id))
        )
    ).one()

    journal_stats = (
        await session.execute(
            select(
                func.count(JournalEntry.id),
                func.max(JournalEntry.created_at),
            ).where(JournalEntry.user_id == str(user_id))
        )
    ).one()

    session_stats = (
        await session.execute(
            select(
                func.count(ConversationSession.id),
                func.max(ConversationSession.updated_at),
            ).where(ConversationSession.user_id == str(user_id))
        )
    ).one()

    message_stats = (
        await session.execute(
            select(func.count(ConversationMessage.id))
            .select_from(ConversationMessage)
            .join(
                ConversationSession,
                ConversationMessage.session_id == ConversationSession.id,
            )
            .where(ConversationSession.user_id == str(user_id))
        )
    ).one()

    latest_snapshot = await session.scalar(
        select(TrendSnapshot)
        .where(TrendSnapshot.user_id == str(user_id))
        .order_by(TrendSnapshot.created_at.desc())
        .limit(1)
    )

    top_theme_rows = (
        await session.execute(
            select(JournalTheme.theme_name, func.count(JournalTheme.id).label("theme_count"))
            .where(JournalTheme.user_id == str(user_id))
            .group_by(JournalTheme.theme_name)
            .order_by(desc("theme_count"), JournalTheme.theme_name.asc())
            .limit(5)
        )
    ).all()

    recurring_trigger_count = int(
        (
            await session.execute(
                select(func.count(TriggerCluster.id)).where(TriggerCluster.user_id == str(user_id))
            )
        ).scalar()
        or 0
    )

    return TrendSummaryResponse(
        user_id=str(user_id),
        total_check_ins=int(check_in_stats[0] or 0),
        avg_mood_score=_as_float(check_in_stats[1]),
        avg_stress_score=_as_float(check_in_stats[2]),
        avg_energy_score=_as_float(check_in_stats[3]),
        avg_sleep_hours=_as_float(check_in_stats[4]),
        latest_check_in_at=check_in_stats[5],
        total_journal_entries=int(journal_stats[0] or 0),
        latest_journal_entry_at=journal_stats[1],
        total_conversation_sessions=int(session_stats[0] or 0),
        latest_conversation_at=session_stats[1],
        total_conversation_messages=int(message_stats[0] or 0),
        latest_snapshot_window_type=latest_snapshot.window_type if latest_snapshot else None,
        latest_snapshot_created_at=latest_snapshot.created_at if latest_snapshot else None,
        top_journal_themes=[row.theme_name for row in top_theme_rows],
        recurring_trigger_count=recurring_trigger_count,
    )