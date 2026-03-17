from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mental_wellbeing_api.api.deps import db_session_dep
from mental_wellbeing_api.models.user import User, UserProfile
from mental_wellbeing_api.schemas.user import UserCreateRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse)
async def create_user(
    payload: UserCreateRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> UserResponse:
    existing = await session.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="User with this email already exists")

    user = User(email=payload.email)
    profile = UserProfile(
        user=user,
        display_name=payload.display_name,
        timezone=payload.timezone,
        support_style=payload.support_style,
        wellbeing_goals=payload.wellbeing_goals,
        focus_areas=payload.focus_areas,
    )
    session.add_all([user, profile])
    await session.commit()

    created = await session.scalar(
        select(User)
        .options(selectinload(User.profile))
        .where(User.id == user.id)
    )
    return created


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    session: AsyncSession = Depends(db_session_dep),
) -> UserResponse:
    user = await session.scalar(
        select(User)
        .options(selectinload(User.profile))
        .where(User.id == user_id)
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user