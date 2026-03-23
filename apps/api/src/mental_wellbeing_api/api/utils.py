from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.models.action_plan import ActionPlan
from mental_wellbeing_api.models.care_plan import CarePlan
from mental_wellbeing_api.models.conversation import ConversationSession
from mental_wellbeing_api.models.follow_up_plan import FollowUpPlan
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


async def ensure_action_plan_exists(session: AsyncSession, action_plan_id: str) -> None:
    action_plan_exists = await session.scalar(
        select(ActionPlan.id).where(ActionPlan.id == action_plan_id)
    )
    if not action_plan_exists:
        raise HTTPException(status_code=404, detail="Action plan not found")


async def ensure_follow_up_plan_exists(
    session: AsyncSession, follow_up_plan_id: str
) -> None:
    follow_up_plan_exists = await session.scalar(
        select(FollowUpPlan.id).where(FollowUpPlan.id == follow_up_plan_id)
    )
    if not follow_up_plan_exists:
        raise HTTPException(status_code=404, detail="Follow up plan not found")


async def ensure_care_plan_exists(session: AsyncSession, care_plan_id: str) -> None:
    care_plan_exists = await session.scalar(
        select(CarePlan.id).where(CarePlan.id == care_plan_id)
    )
    if not care_plan_exists:
        raise HTTPException(status_code=404, detail="Care plan not found")