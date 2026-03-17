from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import db_session_dep
from mental_wellbeing_api.models.safety_flag import SafetyFlag
from mental_wellbeing_api.schemas.safety_flag import (
    SafetyFlagCreateRequest,
    SafetyFlagResponse,
)

router = APIRouter(prefix="/safety-flags", tags=["safety-flags"])


@router.post("", response_model=SafetyFlagResponse)
async def create_safety_flag(
    payload: SafetyFlagCreateRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> SafetyFlagResponse:
    item = SafetyFlag(**payload.model_dump(mode="json"))
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.get("", response_model=list[SafetyFlagResponse])
async def list_safety_flags(
    user_id: UUID,
    session: AsyncSession = Depends(db_session_dep),
) -> list[SafetyFlagResponse]:
    result = await session.scalars(
        select(SafetyFlag)
        .where(SafetyFlag.user_id == str(user_id))
        .order_by(desc(SafetyFlag.created_at))
    )
    return list(result.all())