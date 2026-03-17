from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import db_session_dep
from mental_wellbeing_api.api.utils import ensure_user_exists
from mental_wellbeing_api.models.check_in import CheckIn
from mental_wellbeing_api.schemas.check_in import CheckInCreateRequest, CheckInResponse

router = APIRouter(prefix="/check-ins", tags=["check-ins"])


@router.post("", response_model=CheckInResponse)
async def create_check_in(
    payload: CheckInCreateRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> CheckInResponse:
    await ensure_user_exists(session, str(payload.user_id))

    item = CheckIn(**payload.model_dump(mode="json"))
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.get("", response_model=list[CheckInResponse])
async def list_check_ins(
    user_id: UUID,
    session: AsyncSession = Depends(db_session_dep),
) -> list[CheckInResponse]:
    await ensure_user_exists(session, str(user_id))

    result = await session.scalars(
        select(CheckIn)
        .where(CheckIn.user_id == str(user_id))
        .order_by(desc(CheckIn.created_at))
    )
    return list(result.all())