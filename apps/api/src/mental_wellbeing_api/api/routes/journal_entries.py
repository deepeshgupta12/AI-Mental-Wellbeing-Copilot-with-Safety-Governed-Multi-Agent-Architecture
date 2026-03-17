from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import db_session_dep
from mental_wellbeing_api.models.journal_entry import JournalEntry
from mental_wellbeing_api.schemas.journal_entry import (
    JournalEntryCreateRequest,
    JournalEntryResponse,
)

router = APIRouter(prefix="/journal-entries", tags=["journal-entries"])


@router.post("", response_model=JournalEntryResponse)
async def create_journal_entry(
    payload: JournalEntryCreateRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> JournalEntryResponse:
    item = JournalEntry(**payload.model_dump())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.get("", response_model=list[JournalEntryResponse])
async def list_journal_entries(
    user_id: str,
    session: AsyncSession = Depends(db_session_dep),
) -> list[JournalEntryResponse]:
    result = await session.scalars(
        select(JournalEntry)
        .where(JournalEntry.user_id == user_id)
        .order_by(desc(JournalEntry.created_at))
    )
    return list(result.all())