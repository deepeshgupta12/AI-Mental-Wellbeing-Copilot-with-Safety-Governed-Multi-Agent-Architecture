from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import db_session_dep
from mental_wellbeing_api.api.utils import (
    ensure_action_plan_exists,
    ensure_conversation_session_exists,
    ensure_follow_up_plan_exists,
    ensure_user_exists,
)
from mental_wellbeing_api.schemas.follow_up import (
    FollowUpEventCreateRequest,
    FollowUpEventResponse,
    FollowUpPlanCreateRequest,
    FollowUpPlanResponse,
)
from mental_wellbeing_api.services.follow_up_service import FollowUpService

router = APIRouter(prefix="/follow-ups", tags=["follow-ups"])


@router.post("/plans", response_model=FollowUpPlanResponse)
async def create_follow_up_plan(
    payload: FollowUpPlanCreateRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> FollowUpPlanResponse:
    await ensure_user_exists(session, str(payload.user_id))

    if payload.session_id is not None:
        await ensure_conversation_session_exists(session, str(payload.session_id))

    if payload.action_plan_id is not None:
        await ensure_action_plan_exists(session, str(payload.action_plan_id))

    service = FollowUpService(session)
    item = await service.create_plan(
        user_id=str(payload.user_id),
        source_agent=payload.source_agent,
        plan_type=payload.plan_type,
        title=payload.title,
        description=payload.description,
        session_id=str(payload.session_id) if payload.session_id else None,
        action_plan_id=str(payload.action_plan_id) if payload.action_plan_id else None,
        delivery_channel=payload.delivery_channel,
        timezone_name=payload.timezone,
        support_mode=payload.metadata_json.get("support_mode")
        if payload.metadata_json
        else None,
        support_strategy=payload.metadata_json.get("support_strategy")
        if payload.metadata_json
        else None,
        specialist_agent=payload.metadata_json.get("specialist_agent")
        if payload.metadata_json
        else None,
        metadata=payload.metadata_json,
    )
    return item


@router.get("/plans", response_model=list[FollowUpPlanResponse])
async def list_follow_up_plans(
    user_id: UUID,
    session: AsyncSession = Depends(db_session_dep),
) -> list[FollowUpPlanResponse]:
    await ensure_user_exists(session, str(user_id))
    service = FollowUpService(session)
    return await service.list_plans_for_user(user_id=str(user_id))


@router.post("/events", response_model=FollowUpEventResponse)
async def create_follow_up_event(
    payload: FollowUpEventCreateRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> FollowUpEventResponse:
    await ensure_user_exists(session, str(payload.user_id))
    await ensure_follow_up_plan_exists(session, str(payload.follow_up_plan_id))

    service = FollowUpService(session)
    item = await service.create_event(
        follow_up_plan_id=str(payload.follow_up_plan_id),
        user_id=str(payload.user_id),
        event_type=payload.event_type,
        outcome_status=payload.outcome_status,
        notes=payload.notes,
        event_payload_json=payload.event_payload_json,
    )
    return item


@router.get("/events", response_model=list[FollowUpEventResponse])
async def list_follow_up_events(
    follow_up_plan_id: UUID,
    session: AsyncSession = Depends(db_session_dep),
) -> list[FollowUpEventResponse]:
    await ensure_follow_up_plan_exists(session, str(follow_up_plan_id))
    service = FollowUpService(session)
    return await service.list_events_for_plan(follow_up_plan_id=str(follow_up_plan_id))