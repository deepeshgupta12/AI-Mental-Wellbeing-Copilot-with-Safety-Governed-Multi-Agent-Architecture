from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import db_session_dep
from mental_wellbeing_api.api.utils import ensure_user_exists
from mental_wellbeing_api.models.conversation import ConversationMessage, ConversationSession
from mental_wellbeing_api.schemas.conversation import (
    ConversationMessageCreateRequest,
    ConversationMessageResponse,
    ConversationSessionCreateRequest,
    ConversationSessionResponse,
)
from mental_wellbeing_api.services.memory_service import MemoryService

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/sessions", response_model=ConversationSessionResponse)
async def create_conversation_session(
    payload: ConversationSessionCreateRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> ConversationSessionResponse:
    await ensure_user_exists(session, str(payload.user_id))

    item = ConversationSession(**payload.model_dump(mode="json"))
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.get("/sessions", response_model=list[ConversationSessionResponse])
async def list_conversation_sessions(
    user_id: UUID,
    session: AsyncSession = Depends(db_session_dep),
) -> list[ConversationSessionResponse]:
    await ensure_user_exists(session, str(user_id))

    result = await session.scalars(
        select(ConversationSession)
        .where(ConversationSession.user_id == str(user_id))
        .order_by(desc(ConversationSession.updated_at))
    )
    return list(result.all())


@router.post("/messages", response_model=ConversationMessageResponse)
async def create_conversation_message(
    payload: ConversationMessageCreateRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> ConversationMessageResponse:
    conversation_session = await session.scalar(
        select(ConversationSession).where(
            ConversationSession.id == str(payload.session_id)
        )
    )
    if not conversation_session:
        raise HTTPException(status_code=404, detail="Conversation session not found")

    item = ConversationMessage(**payload.model_dump(mode="json"))
    session.add(item)
    await session.commit()
    await session.refresh(item)

    if item.role == "user":
        await MemoryService(session).add_memory(
            user_id=conversation_session.user_id,
            source_type="conversation_message",
            source_id=item.id,
            content=item.content,
        )
        await session.refresh(item)

    return item


@router.get("/messages", response_model=list[ConversationMessageResponse])
async def list_conversation_messages(
    session_id: UUID,
    session: AsyncSession = Depends(db_session_dep),
) -> list[ConversationMessageResponse]:
    result = await session.scalars(
        select(ConversationMessage)
        .where(ConversationMessage.session_id == str(session_id))
        .order_by(ConversationMessage.created_at.asc())
    )
    return list(result.all())