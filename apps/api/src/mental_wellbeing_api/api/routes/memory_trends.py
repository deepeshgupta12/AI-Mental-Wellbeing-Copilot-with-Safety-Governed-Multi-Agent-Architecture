from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mental_wellbeing_api.api.deps import db_session_dep
from mental_wellbeing_api.models.check_in import CheckIn
from mental_wellbeing_api.models.conversation import ConversationMessage, ConversationSession
from mental_wellbeing_api.models.journal_entry import JournalEntry
from mental_wellbeing_api.models.user import User
from mental_wellbeing_api.schemas.memory_trends import (
    MemoryItemResponse,
    MemorySummaryResponse,
    TrendSummaryResponse,
)

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

        memory_items.append(
            MemoryItemResponse(
                source_type="check_in",
                source_id=item.id,
                title="Check-in snapshot",
                summary=" • ".join(summary_parts) if summary_parts else "Recent check-in recorded",
                created_at=item.created_at,
            )
        )

    for item in recent_journals:
        memory_items.append(
            MemoryItemResponse(
                source_type="journal_entry",
                source_id=item.id,
                title=item.title or "Journal entry",
                summary=_truncate(item.content, 140),
                created_at=item.created_at,
            )
        )

    for item in recent_sessions:
        memory_items.append(
            MemoryItemResponse(
                source_type="conversation_session",
                source_id=item.id,
                title=item.title or "Conversation session",
                summary=f"Status: {item.status}",
                created_at=item.updated_at,
            )
        )

    memory_items.sort(key=lambda x: x.created_at, reverse=True)
    memory_items = memory_items[:5]

    return MemorySummaryResponse(
        user_id=user.id,
        display_name=user.profile.display_name if user.profile else None,
        wellbeing_goals=user.profile.wellbeing_goals if user.profile else None,
        recent_memories=memory_items,
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
    )