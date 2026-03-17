from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import db_session_dep
from mental_wellbeing_api.models.action_plan import ActionPlan
from mental_wellbeing_api.schemas.action_plan import ActionPlanCreateRequest, ActionPlanResponse

router = APIRouter(prefix="/action-plans", tags=["action-plans"])


@router.post("", response_model=ActionPlanResponse)
async def create_action_plan(
    payload: ActionPlanCreateRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> ActionPlanResponse:
    item = ActionPlan(**payload.model_dump())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.get("", response_model=list[ActionPlanResponse])
async def list_action_plans(
    user_id: str,
    session: AsyncSession = Depends(db_session_dep),
) -> list[ActionPlanResponse]:
    result = await session.scalars(
        select(ActionPlan)
        .where(ActionPlan.user_id == user_id)
        .order_by(desc(ActionPlan.created_at))
    )
    return list(result.all())