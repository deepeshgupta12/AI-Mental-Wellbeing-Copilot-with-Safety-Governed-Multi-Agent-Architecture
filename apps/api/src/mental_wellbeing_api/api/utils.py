from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.models.conversation import ConversationSession
from mental_wellbeing_api.models.user import User


async def ensure_user_exists(session: AsyncSession, user_id: str) -> None:
    user_exists = await session.scalar(select(User.id).where(User.id == user_id))
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")


async def ensure_conversation_session_exists(
    session: AsyncSession, session_id: str
) -> None:
    conversation_exists = await session.scalar(
        select(ConversationSession.id).where(ConversationSession.id == session_id)
    )
    if not conversation_exists:
        raise HTTPException(status_code=404, detail="Conversation session not found")