from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import db_session_dep
from mental_wellbeing_api.api.utils import ensure_user_exists
from mental_wellbeing_api.models.journal_entry import JournalEntry
from mental_wellbeing_api.schemas.journal_entry import (
    JournalEntryCreateRequest,
    JournalEntryResponse,
)
from mental_wellbeing_api.services.journaling_intelligence_service import (
    JournalingIntelligenceService,
)
from mental_wellbeing_api.services.memory_service import MemoryService

router = APIRouter(prefix="/journal-entries", tags=["journal-entries"])


@router.post("", response_model=JournalEntryResponse)
async def create_journal_entry(
    payload: JournalEntryCreateRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> JournalEntryResponse:
    await ensure_user_exists(session, str(payload.user_id))

    journaling_service = JournalingIntelligenceService(session)
    analysis = journaling_service.analyze_entry(
        content=payload.content,
        title=payload.title,
        entry_type=payload.entry_type,
    )

    item = JournalEntry(
        **payload.model_dump(mode="json"),
        summary=analysis.summary,
        emotional_tone=analysis.emotional_tone,
        structured_insights_json=analysis.structured_insights_json,
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)

    await journaling_service.persist_journal_derivatives(
        user_id=item.user_id,
        journal_entry=item,
        analysis=analysis,
    )
    await journaling_service.upsert_weekly_reflection_snapshot(user_id=item.user_id)

    await MemoryService(session).add_memory(
        user_id=item.user_id,
        source_type="journal_entry",
        source_id=item.id,
        content=item.content,
    )

    await session.refresh(item)
    return item


@router.get("", response_model=list[JournalEntryResponse])
async def list_journal_entries(
    user_id: UUID,
    session: AsyncSession = Depends(db_session_dep),
) -> list[JournalEntryResponse]:
    await ensure_user_exists(session, str(user_id))

    result = await session.scalars(
        select(JournalEntry)
        .where(JournalEntry.user_id == str(user_id))
        .order_by(desc(JournalEntry.created_at))
    )
    return list(result.all())