from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import db_session_dep
from mental_wellbeing_api.api.utils import ensure_user_exists
from mental_wellbeing_api.models.check_in import CheckIn
from mental_wellbeing_api.schemas.check_in import CheckInCreateRequest, CheckInResponse
from mental_wellbeing_api.services.memory_service import MemoryService

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

    summary_parts: list[str] = []
    if item.mood_score is not None:
        summary_parts.append(f"Mood {item.mood_score}")
    if item.stress_score is not None:
        summary_parts.append(f"Stress {item.stress_score}")
    if item.energy_score is not None:
        summary_parts.append(f"Energy {item.energy_score}")
    if item.sleep_hours is not None:
        summary_parts.append(f"Sleep {item.sleep_hours}h")
    if item.notes:
        summary_parts.append(item.notes)

    await MemoryService(session).add_memory(
        user_id=item.user_id,
        source_type="check_in",
        source_id=item.id,
        content=" • ".join(summary_parts) if summary_parts else "Recent wellbeing check-in",
    )
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