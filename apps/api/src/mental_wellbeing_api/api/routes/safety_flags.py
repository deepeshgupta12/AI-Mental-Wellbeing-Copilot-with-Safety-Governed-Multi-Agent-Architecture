from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import db_session_dep
from mental_wellbeing_api.models.safety_flag import SafetyFlag
from mental_wellbeing_api.schemas.safety_flag import SafetyFlagResponse

router = APIRouter(prefix="/safety-flags", tags=["safety-flags"])


@router.get("", response_model=list[SafetyFlagResponse])
async def list_safety_flags(
    user_id: str,
    session: AsyncSession = Depends(db_session_dep),
) -> list[SafetyFlagResponse]:
    result = await session.scalars(
        select(SafetyFlag)
        .where(SafetyFlag.user_id == user_id)
        .order_by(desc(SafetyFlag.created_at))
    )
    return list(result.all())