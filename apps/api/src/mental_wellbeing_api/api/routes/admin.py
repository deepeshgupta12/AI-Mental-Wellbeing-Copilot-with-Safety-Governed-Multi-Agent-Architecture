from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import db_session_dep
from mental_wellbeing_api.models.conversation import ConversationMessage, ConversationSession
from mental_wellbeing_api.models.safety_flag import SafetyFlag
from mental_wellbeing_api.prompts.registry import load_prompt_registry, load_runtime_policy
from mental_wellbeing_api.schemas.admin import (
    AdminAuditItemResponse,
    AdminFlaggedSessionResponse,
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