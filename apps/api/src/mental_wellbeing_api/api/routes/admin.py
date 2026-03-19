from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import db_session_dep
from mental_wellbeing_api.models.conversation import ConversationMessage, ConversationSession
from mental_wellbeing_api.models.follow_up_event import FollowUpEvent
from mental_wellbeing_api.models.follow_up_plan import FollowUpPlan
from mental_wellbeing_api.models.safety_flag import SafetyFlag
from mental_wellbeing_api.prompts.registry import load_prompt_registry, load_runtime_policy
from mental_wellbeing_api.schemas.admin import (
    AdminAuditItemResponse,
    AdminFlaggedSessionResponse,
    AdminFollowUpEventResponse,
    AdminFollowUpOverviewResponse,
    AdminFollowUpPlanResponse,
    AdminPolicyConfigResponse,
    AdminSessionLogResponse,
    AdminTrendOverviewResponse,
)
from mental_wellbeing_api.services.trend_intelligence_service import TrendIntelligenceService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/flagged-sessions", response_model=list[AdminFlaggedSessionResponse])
async def get_flagged_sessions(
    limit: int = 50,
    session: AsyncSession = Depends(db_session_dep),
) -> list[AdminFlaggedSessionResponse]:
    result = await session.scalars(
        select(SafetyFlag)
        .order_by(
            SafetyFlag.is_resolved.asc(),
            SafetyFlag.needs_review.desc(),
            desc(SafetyFlag.created_at),
        )
        .limit(limit)
    )
    return list(result.all())


@router.get("/session-logs", response_model=list[AdminSessionLogResponse])
async def get_session_logs(
    limit: int = 50,
    session: AsyncSession = Depends(db_session_dep),
) -> list[AdminSessionLogResponse]:
    stmt = (
        select(
            ConversationSession.id,
            ConversationSession.user_id,
            ConversationSession.title,
            ConversationSession.status,
            ConversationSession.started_at,
            ConversationSession.updated_at,
            func.count(ConversationMessage.id).label("message_count"),
            func.max(ConversationMessage.created_at).label("latest_message_at"),
        )
        .outerjoin(
            ConversationMessage,
            ConversationMessage.session_id == ConversationSession.id,
        )
        .group_by(
            ConversationSession.id,
            ConversationSession.user_id,
            ConversationSession.title,
            ConversationSession.status,
            ConversationSession.started_at,
            ConversationSession.updated_at,
        )
        .order_by(desc(ConversationSession.updated_at))
        .limit(limit)
    )

    rows = (await session.execute(stmt)).all()

    return [
        AdminSessionLogResponse(
            session_id=row.id,
            user_id=row.user_id,
            title=row.title,
            status=row.status,
            started_at=row.started_at,
            updated_at=row.updated_at,
            message_count=int(row.message_count or 0),
            latest_message_at=row.latest_message_at,
        )
        for row in rows
    ]


@router.get("/audit-trail", response_model=list[AdminAuditItemResponse])
async def get_audit_trail(
    limit: int = 100,
    session: AsyncSession = Depends(db_session_dep),
) -> list[AdminAuditItemResponse]:
    audit_items: list[AdminAuditItemResponse] = []

    safety_flags = list(
        (
            await session.scalars(
                select(SafetyFlag).order_by(desc(SafetyFlag.created_at)).limit(limit)
            )
        ).all()
    )

    sessions = list(
        (
            await session.scalars(
                select(ConversationSession)
                .order_by(desc(ConversationSession.started_at))
                .limit(limit)
            )
        ).all()
    )

    for flag in safety_flags:
        audit_items.append(
            AdminAuditItemResponse(
                event_type="safety_flag_created",
                entity_type="safety_flag",
                entity_id=flag.id,
                title=f"Safety flag: {flag.flag_type}",
                details=flag.summary or "Safety flag created.",
                user_id=flag.user_id,
                occurred_at=flag.created_at,
            )
        )
        if flag.reviewed_at is not None:
            audit_items.append(
                AdminAuditItemResponse(
                    event_type="safety_flag_reviewed",
                    entity_type="safety_flag",
                    entity_id=flag.id,
                    title=f"Safety review completed: {flag.flag_type}",
                    details=flag.reviewer_note or "Safety flag reviewed.",
                    user_id=flag.user_id,
                    occurred_at=flag.reviewed_at,
                )
            )
        if flag.resolved_at is not None:
            audit_items.append(
                AdminAuditItemResponse(
                    event_type="safety_flag_resolved",
                    entity_type="safety_flag",
                    entity_id=flag.id,
                    title=f"Safety flag resolved: {flag.flag_type}",
                    details=flag.reviewer_note or "Safety flag resolved.",
                    user_id=flag.user_id,
                    occurred_at=flag.resolved_at,
                )
            )

    for item in sessions:
        audit_items.append(
            AdminAuditItemResponse(
                event_type="conversation_session_started",
                entity_type="conversation_session",
                entity_id=item.id,
                title=item.title or "Conversation session",
                details=f"Session started with status: {item.status}",
                user_id=item.user_id,
                occurred_at=item.started_at,
            )
        )

    audit_items.sort(key=lambda x: x.occurred_at, reverse=True)
    return audit_items[:limit]


@router.get("/policy-config", response_model=AdminPolicyConfigResponse)
async def get_policy_config() -> AdminPolicyConfigResponse:
    return AdminPolicyConfigResponse(
        runtime_policy=load_runtime_policy(),
        prompt_registry=load_prompt_registry(),
    )


@router.get("/trend-overview", response_model=AdminTrendOverviewResponse)
async def get_trend_overview(
    session: AsyncSession = Depends(db_session_dep),
) -> AdminTrendOverviewResponse:
    payload = await TrendIntelligenceService(session).build_admin_trend_overview()
    return AdminTrendOverviewResponse(**payload)


@router.get("/follow-up-overview", response_model=AdminFollowUpOverviewResponse)
async def get_follow_up_overview(
    session: AsyncSession = Depends(db_session_dep),
) -> AdminFollowUpOverviewResponse:
    now = datetime.now(timezone.utc)

    total_follow_up_plans = int(
        (
            await session.execute(
                select(func.count(FollowUpPlan.id))
            )
        ).scalar()
        or 0
    )

    active_scheduled_plans = int(
        (
            await session.execute(
                select(func.count(FollowUpPlan.id)).where(
                    FollowUpPlan.status.in_(["planned", "scheduled"])
                )
            )
        ).scalar()
        or 0
    )

    completed_plans = int(
        (
            await session.execute(
                select(func.count(FollowUpPlan.id)).where(FollowUpPlan.status == "completed")
            )
        ).scalar()
        or 0
    )

    cancelled_plans = int(
        (
            await session.execute(
                select(func.count(FollowUpPlan.id)).where(FollowUpPlan.status == "cancelled")
            )
        ).scalar()
        or 0
    )

    overdue_plans = int(
        (
            await session.execute(
                select(func.count(FollowUpPlan.id)).where(
                    FollowUpPlan.scheduled_for.is_not(None),
                    FollowUpPlan.scheduled_for < now,
                    FollowUpPlan.status.in_(["planned", "scheduled"]),
                )
            )
        ).scalar()
        or 0
    )

    failed_follow_up_events = int(
        (
            await session.execute(
                select(func.count(FollowUpEvent.id)).where(
                    FollowUpEvent.event_type == "failed"
                )
            )
        ).scalar()
        or 0
    )

    delivery_rows = (
        await session.execute(
            select(
                FollowUpPlan.delivery_channel,
                func.count(FollowUpPlan.id).label("plan_count"),
            )
            .group_by(FollowUpPlan.delivery_channel)
            .order_by(desc("plan_count"))
        )
    ).all()
    delivery_channel_breakdown = {
        str(row.delivery_channel): int(row.plan_count or 0)
        for row in delivery_rows
        if row.delivery_channel
    }

    scheduler_rows = (
        await session.execute(
            select(FollowUpPlan.scheduling_contract_json)
            .order_by(desc(FollowUpPlan.created_at))
            .limit(200)
        )
    ).all()
    scheduler_backend_breakdown: dict[str, int] = {}
    for row in scheduler_rows:
        contract = row.scheduling_contract_json
        if isinstance(contract, dict):
            backend = str(contract.get("scheduler_backend") or "unknown")
            scheduler_backend_breakdown[backend] = (
                scheduler_backend_breakdown.get(backend, 0) + 1
            )

    upcoming_rows = list(
        (
            await session.scalars(
                select(FollowUpPlan)
                .where(
                    FollowUpPlan.scheduled_for.is_not(None),
                    FollowUpPlan.scheduled_for >= now,
                    FollowUpPlan.status.in_(["planned", "scheduled"]),
                )
                .order_by(FollowUpPlan.scheduled_for.asc())
                .limit(5)
            )
        ).all()
    )
    upcoming_due_follow_ups = [
        {
            "id": item.id,
            "user_id": item.user_id,
            "title": item.title,
            "plan_type": item.plan_type,
            "status": item.status,
            "delivery_channel": item.delivery_channel,
            "scheduled_for": item.scheduled_for.isoformat() if item.scheduled_for else None,
        }
        for item in upcoming_rows
    ]

    recent_event_rows = list(
        (
            await session.scalars(
                select(FollowUpEvent)
                .where(FollowUpEvent.outcome_status.is_not(None))
                .order_by(desc(FollowUpEvent.created_at))
                .limit(10)
            )
        ).all()
    )
    recent_completion_outcomes = [
        {
            "id": item.id,
            "follow_up_plan_id": item.follow_up_plan_id,
            "user_id": item.user_id,
            "event_type": item.event_type,
            "outcome_status": item.outcome_status,
            "created_at": item.created_at.isoformat(),
        }
        for item in recent_event_rows
    ]

    return AdminFollowUpOverviewResponse(
        total_follow_up_plans=total_follow_up_plans,
        active_scheduled_plans=active_scheduled_plans,
        completed_plans=completed_plans,
        cancelled_plans=cancelled_plans,
        overdue_plans=overdue_plans,
        failed_follow_up_events=failed_follow_up_events,
        delivery_channel_breakdown=delivery_channel_breakdown,
        scheduler_backend_breakdown=scheduler_backend_breakdown,
        upcoming_due_follow_ups=upcoming_due_follow_ups,
        recent_completion_outcomes=recent_completion_outcomes,
    )


@router.get("/follow-up-plans", response_model=list[AdminFollowUpPlanResponse])
async def get_follow_up_plans(
    limit: int = 50,
    session: AsyncSession = Depends(db_session_dep),
) -> list[AdminFollowUpPlanResponse]:
    result = await session.scalars(
        select(FollowUpPlan)
        .order_by(desc(FollowUpPlan.created_at))
        .limit(limit)
    )
    return list(result.all())


@router.get("/follow-up-events", response_model=list[AdminFollowUpEventResponse])
async def get_follow_up_events(
    limit: int = 100,
    session: AsyncSession = Depends(db_session_dep),
) -> list[AdminFollowUpEventResponse]:
    result = await session.scalars(
        select(FollowUpEvent)
        .order_by(desc(FollowUpEvent.created_at))
        .limit(limit)
    )
    return list(result.all())