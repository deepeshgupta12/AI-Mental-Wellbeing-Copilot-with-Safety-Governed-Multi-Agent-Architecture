from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import db_session_dep
from mental_wellbeing_api.api.utils import (
    ensure_conversation_session_exists,
    ensure_user_exists,
)
from mental_wellbeing_api.models.conversation import ConversationMessage, ConversationSession
from mental_wellbeing_api.schemas.conversation import (
    ConversationMessageCreateRequest,
    ConversationMessageResponse,
    ConversationSessionCreateRequest,
    ConversationSessionResponse,
)

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
    await ensure_conversation_session_exists(session, str(payload.session_id))

    item = ConversationMessage(**payload.model_dump(mode="json"))
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.get("/messages", response_model=list[ConversationMessageResponse])
async def list_conversation_messages(
    session_id: UUID,
    session: AsyncSession = Depends(db_session_dep),
) -> list[ConversationMessageResponse]:
    await ensure_conversation_session_exists(session, str(session_id))

    result = await session.scalars(
        select(ConversationMessage)
        .where(ConversationMessage.session_id == str(session_id))
        .order_by(ConversationMessage.created_at.asc())
    )
    return list(result.all())