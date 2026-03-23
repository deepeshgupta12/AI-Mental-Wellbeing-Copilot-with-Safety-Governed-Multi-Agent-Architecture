from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import db_session_dep
from mental_wellbeing_api.api.utils import ensure_user_exists
from mental_wellbeing_api.schemas.care_plan import (
    CarePlanAdvanceStepRequest,
    CarePlanCreateRequest,
    CarePlanEventCreateRequest,
    CarePlanEventResponse,
    CarePlanResponse,
    CarePlanUpdateRequest,
    CarePlanUserSummaryResponse,
)
from mental_wellbeing_api.services.care_plan_service import CarePlanService

router = APIRouter(prefix="/care-plans", tags=["care-plans"])


@router.post("", response_model=CarePlanResponse)
async def create_care_plan(
    payload: CarePlanCreateRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> CarePlanResponse:
    await ensure_user_exists(session, str(payload.user_id))
    service = CarePlanService(session)
    return await service.create_care_plan(payload=payload.model_dump())


@router.get("", response_model=list[CarePlanResponse])
async def list_care_plans(
    user_id: UUID | None = Query(default=None),
    organization_id: UUID | None = Query(default=None),
    session: AsyncSession = Depends(db_session_dep),
) -> list[CarePlanResponse]:
    service = CarePlanService(session)
    return await service.list_care_plans(
        user_id=str(user_id) if user_id else None,
        organization_id=str(organization_id) if organization_id else None,
    )


@router.get("/summary", response_model=CarePlanUserSummaryResponse)
async def get_care_plan_user_summary(
    user_id: UUID,
    session: AsyncSession = Depends(db_session_dep),
) -> CarePlanUserSummaryResponse:
    await ensure_user_exists(session, str(user_id))
    service = CarePlanService(session)
    return CarePlanUserSummaryResponse(**(await service.build_user_summary(user_id=str(user_id))))


@router.get("/{care_plan_id}", response_model=CarePlanResponse)
async def get_care_plan(
    care_plan_id: UUID,
    session: AsyncSession = Depends(db_session_dep),
) -> CarePlanResponse:
    service = CarePlanService(session)
    item = await service.get_care_plan(str(care_plan_id))
    if item is None:
        raise HTTPException(status_code=404, detail="Care plan not found")
    return item


@router.patch("/{care_plan_id}", response_model=CarePlanResponse)
async def update_care_plan(
    care_plan_id: UUID,
    payload: CarePlanUpdateRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> CarePlanResponse:
    service = CarePlanService(session)
    try:
        return await service.update_care_plan(
            care_plan_id=str(care_plan_id),
            payload=payload.model_dump(exclude_none=True),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{care_plan_id}/events", response_model=CarePlanEventResponse)
async def create_care_plan_event(
    care_plan_id: UUID,
    payload: CarePlanEventCreateRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> CarePlanEventResponse:
    await ensure_user_exists(session, str(payload.user_id))
    service = CarePlanService(session)
    try:
        return await service.record_event(
            care_plan_id=str(care_plan_id),
            user_id=str(payload.user_id),
            event_type=payload.event_type,
            event_status=payload.event_status,
            step_key=payload.step_key,
            adherence_score=payload.adherence_score,
            notes=payload.notes,
            event_payload_json=payload.event_payload_json,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{care_plan_id}/events", response_model=list[CarePlanEventResponse])
async def list_care_plan_events(
    care_plan_id: UUID,
    session: AsyncSession = Depends(db_session_dep),
) -> list[CarePlanEventResponse]:
    service = CarePlanService(session)
    return await service.list_events(care_plan_id=str(care_plan_id))


@router.post("/{care_plan_id}/advance", response_model=CarePlanResponse)
async def advance_care_plan_step(
    care_plan_id: UUID,
    payload: CarePlanAdvanceStepRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> CarePlanResponse:
    service = CarePlanService(session)
    try:
        return await service.advance_step(
            care_plan_id=str(care_plan_id),
            next_step_key=payload.next_step_key,
            notes=payload.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc