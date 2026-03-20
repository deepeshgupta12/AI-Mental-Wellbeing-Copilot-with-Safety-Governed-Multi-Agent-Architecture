from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import db_session_dep, require_permission
from mental_wellbeing_api.models.conversation import ConversationMessage, ConversationSession
from mental_wellbeing_api.models.follow_up_event import FollowUpEvent
from mental_wellbeing_api.models.follow_up_plan import FollowUpPlan
from mental_wellbeing_api.models.safety_flag import SafetyFlag
from mental_wellbeing_api.prompts.registry import (
    load_prompt_registry_document,
    load_routing_rules,
    load_runtime_policy,
)
from mental_wellbeing_api.schemas.admin import (
    AdminAnalyticsOverviewResponse,
    AdminAuditItemResponse,
    AdminAuditLogResponse,
    AdminConfigAuditResponse,
    AdminConfigDiffResponse,
    AdminConfigUpdateRequest,
    AdminConfigVersionResponse,
    AdminEscalationAnalyticsResponse,
    AdminFlaggedSessionDetailResponse,
    AdminFlaggedSessionResponse,
    AdminFollowUpEventResponse,
    AdminFollowUpOverviewResponse,
    AdminFollowUpPlanResponse,
    AdminInterventionLogResponse,
    AdminInterventionOverviewResponse,
    AdminOpsOverviewResponse,
    AdminPolicyConfigResponse,
    AdminReviewerDashboardResponse,
    AdminRoutingRulesResponse,
    AdminSafetyEventDetailResponse,
    AdminSafetyEventResponse,
    AdminSafetyReviewCreateRequest,
    AdminSafetyReviewResponse,
    AdminSessionLogResponse,
    AdminTraceExecutionDetailResponse,
    AdminTraceExecutionSummaryResponse,
    AdminTraceItemResponse,
    AdminTrendOverviewResponse,
)
from mental_wellbeing_api.services.admin_observability_service import AdminObservabilityService
from mental_wellbeing_api.services.config_registry_service import ConfigRegistryService
from mental_wellbeing_api.services.safety_review_service import SafetyReviewService
from mental_wellbeing_api.services.trend_intelligence_service import TrendIntelligenceService

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_permission("admin:read"))],
)


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


@router.get("/flagged-sessions/{flag_id}", response_model=AdminFlaggedSessionDetailResponse)
async def get_flagged_session_detail(
    flag_id: str,
    session: AsyncSession = Depends(db_session_dep),
) -> AdminFlaggedSessionDetailResponse:
    service = AdminObservabilityService(session)
    try:
        payload = await service.get_flagged_session_detail(flag_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return AdminFlaggedSessionDetailResponse(
        flag=payload["flag"],
        related_traces=[
            {
                "id": item.id,
                "trace_name": item.trace_name,
                "user_id": item.user_id,
                "agent_name": item.agent_name,
                "handoff_from_agent": item.handoff_from_agent,
                "handoff_to_agent": item.handoff_to_agent,
                "input_payload_json": item.input_payload_json,
                "output_payload_json": item.output_payload_json,
                "status": item.status,
                "latency_ms": item.latency_ms,
                "notes": item.notes,
                "created_at": item.created_at,
            }
            for item in payload["related_traces"]
        ],
        related_sessions=[
            {
                "id": item.id,
                "user_id": item.user_id,
                "title": item.title,
                "status": item.status,
                "support_mode": item.support_mode,
                "resolved_mode": item.resolved_mode,
                "session_summary": item.session_summary,
                "started_at": item.started_at,
                "updated_at": item.updated_at,
            }
            for item in payload["related_sessions"]
        ],
    )


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
        prompt_registry=load_prompt_registry_document(),
        routing_rules=load_routing_rules(),
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
    now = datetime.now(UTC)

    total_follow_up_plans = int((await session.scalar(select(func.count(FollowUpPlan.id)))) or 0)

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
                select(func.count(FollowUpEvent.id)).where(FollowUpEvent.event_type == "failed")
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
            scheduler_backend_breakdown[backend] = scheduler_backend_breakdown.get(backend, 0) + 1

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


@router.get("/agent-traces", response_model=list[AdminTraceItemResponse])
async def get_agent_traces(
    limit: int = 100,
    trace_name: str | None = None,
    user_id: str | None = None,
    agent_name: str | None = None,
    session: AsyncSession = Depends(db_session_dep),
) -> list[AdminTraceItemResponse]:
    service = AdminObservabilityService(session)
    return await service.list_agent_traces(
        limit=limit,
        trace_name=trace_name,
        user_id=user_id,
        agent_name=agent_name,
    )


@router.get("/agent-trace-executions", response_model=list[AdminTraceExecutionSummaryResponse])
async def get_agent_trace_executions(
    limit: int = 100,
    session: AsyncSession = Depends(db_session_dep),
) -> list[AdminTraceExecutionSummaryResponse]:
    service = AdminObservabilityService(session)
    payload = await service.list_grouped_runtime_executions(limit=limit)
    return [AdminTraceExecutionSummaryResponse(**item) for item in payload]


@router.get("/agent-trace-executions/{trace_name}", response_model=AdminTraceExecutionDetailResponse)
async def get_agent_trace_execution_detail(
    trace_name: str,
    session: AsyncSession = Depends(db_session_dep),
) -> AdminTraceExecutionDetailResponse:
    service = AdminObservabilityService(session)
    payload = await service.get_runtime_execution_detail(trace_name)
    return AdminTraceExecutionDetailResponse(
        trace_name=payload["trace_name"],
        event_count=payload["event_count"],
        events=payload["events"],
    )


@router.get("/intervention-logs", response_model=list[AdminInterventionLogResponse])
async def get_intervention_logs(
    limit: int = 100,
    session: AsyncSession = Depends(db_session_dep),
) -> list[AdminInterventionLogResponse]:
    service = AdminObservabilityService(session)
    return await service.list_intervention_logs(limit=limit)


@router.get("/intervention-overview", response_model=AdminInterventionOverviewResponse)
async def get_intervention_overview(
    session: AsyncSession = Depends(db_session_dep),
) -> AdminInterventionOverviewResponse:
    service = AdminObservabilityService(session)
    return AdminInterventionOverviewResponse(**(await service.get_intervention_overview()))


@router.get("/routing-rules", response_model=AdminRoutingRulesResponse)
async def get_routing_rules(
    session: AsyncSession = Depends(db_session_dep),
) -> AdminRoutingRulesResponse:
    registry = ConfigRegistryService(session)
    active = await registry.get_active("routing_rules")
    return AdminRoutingRulesResponse(
        active_version=active,
        live_payload=load_routing_rules(),
    )


@router.put(
    "/routing-rules",
    response_model=AdminConfigVersionResponse,
    dependencies=[Depends(require_permission("admin:write"))],
)
async def update_routing_rules(
    payload: AdminConfigUpdateRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> AdminConfigVersionResponse:
    registry = ConfigRegistryService(session)
    return await registry.update_config(
        config_key="routing_rules",
        payload=payload.payload_json,
        change_note=payload.change_note,
        actor=payload.actor,
    )


@router.get("/runtime-policy", response_model=AdminConfigVersionResponse)
async def get_runtime_policy_active_version(
    session: AsyncSession = Depends(db_session_dep),
) -> AdminConfigVersionResponse:
    registry = ConfigRegistryService(session)
    return await registry.get_active("runtime_policy")


@router.get("/runtime-policy/versions", response_model=list[AdminConfigVersionResponse])
async def get_runtime_policy_versions(
    limit: int = 20,
    session: AsyncSession = Depends(db_session_dep),
) -> list[AdminConfigVersionResponse]:
    registry = ConfigRegistryService(session)
    return await registry.list_versions("runtime_policy", limit=limit)


@router.put(
    "/runtime-policy",
    response_model=AdminConfigVersionResponse,
    dependencies=[Depends(require_permission("admin:write"))],
)
async def update_runtime_policy(
    payload: AdminConfigUpdateRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> AdminConfigVersionResponse:
    registry = ConfigRegistryService(session)
    return await registry.update_config(
        config_key="runtime_policy",
        payload=payload.payload_json,
        change_note=payload.change_note,
        actor=payload.actor,
    )


@router.get("/prompt-registry", response_model=AdminConfigVersionResponse)
async def get_prompt_registry_active_version(
    session: AsyncSession = Depends(db_session_dep),
) -> AdminConfigVersionResponse:
    registry = ConfigRegistryService(session)
    return await registry.get_active("prompt_registry")


@router.get("/prompt-registry/versions", response_model=list[AdminConfigVersionResponse])
async def get_prompt_registry_versions(
    limit: int = 20,
    session: AsyncSession = Depends(db_session_dep),
) -> list[AdminConfigVersionResponse]:
    registry = ConfigRegistryService(session)
    return await registry.list_versions("prompt_registry", limit=limit)


@router.put(
    "/prompt-registry",
    response_model=AdminConfigVersionResponse,
    dependencies=[Depends(require_permission("admin:write"))],
)
async def update_prompt_registry(
    payload: AdminConfigUpdateRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> AdminConfigVersionResponse:
    registry = ConfigRegistryService(session)
    return await registry.update_config(
        config_key="prompt_registry",
        payload=payload.payload_json,
        change_note=payload.change_note,
        actor=payload.actor,
    )


@router.get("/config-audit", response_model=list[AdminConfigAuditResponse])
async def get_config_audit(
    config_key: str | None = Query(default=None),
    limit: int = 50,
    session: AsyncSession = Depends(db_session_dep),
) -> list[AdminConfigAuditResponse]:
    registry = ConfigRegistryService(session)
    return await registry.list_audits(config_key=config_key, limit=limit)


@router.get("/config-diff", response_model=AdminConfigDiffResponse)
async def get_config_diff(
    config_key: str,
    from_version_id: str,
    to_version_id: str,
    session: AsyncSession = Depends(db_session_dep),
) -> AdminConfigDiffResponse:
    registry = ConfigRegistryService(session)
    try:
        payload = await registry.get_diff(
            config_key=config_key,
            from_version_id=from_version_id,
            to_version_id=to_version_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return AdminConfigDiffResponse(**payload)


@router.get("/ops-overview", response_model=AdminOpsOverviewResponse)
async def get_ops_overview(
    session: AsyncSession = Depends(db_session_dep),
) -> AdminOpsOverviewResponse:
    service = AdminObservabilityService(session)
    payload = await service.get_ops_overview()
    return AdminOpsOverviewResponse(**payload)


@router.get("/analytics/overview", response_model=AdminAnalyticsOverviewResponse)
async def get_analytics_overview(
    session: AsyncSession = Depends(db_session_dep),
) -> AdminAnalyticsOverviewResponse:
    service = AdminObservabilityService(session)
    payload = await service.get_analytics_overview()
    return AdminAnalyticsOverviewResponse(**payload)


# ---------------------------
# V3 reviewer / safety queue
# ---------------------------


@router.get("/safety-events", response_model=list[AdminSafetyEventResponse])
async def get_safety_events(
    limit: int = 50,
    queue_status: str | None = None,
    risk_level: str | None = None,
    session: AsyncSession = Depends(db_session_dep),
) -> list[AdminSafetyEventResponse]:
    service = SafetyReviewService(session)
    return await service.list_safety_events(
        limit=limit,
        queue_status=queue_status,
        risk_level=risk_level,
    )


@router.get("/safety-events/{safety_event_id}", response_model=AdminSafetyEventDetailResponse)
async def get_safety_event_detail(
    safety_event_id: str,
    session: AsyncSession = Depends(db_session_dep),
) -> AdminSafetyEventDetailResponse:
    service = SafetyReviewService(session)
    event = await service.get_safety_event(safety_event_id=safety_event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Safety event not found")

    reviews = await service.list_reviews_for_event(safety_event_id=safety_event_id)
    return AdminSafetyEventDetailResponse(event=event, reviews=reviews)


@router.get(
    "/safety-events/{safety_event_id}/reviews",
    response_model=list[AdminSafetyReviewResponse],
)
async def get_safety_event_reviews(
    safety_event_id: str,
    session: AsyncSession = Depends(db_session_dep),
) -> list[AdminSafetyReviewResponse]:
    service = SafetyReviewService(session)
    event = await service.get_safety_event(safety_event_id=safety_event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Safety event not found")
    return await service.list_reviews_for_event(safety_event_id=safety_event_id)


@router.post(
    "/safety-events/{safety_event_id}/reviews",
    response_model=AdminSafetyReviewResponse,
    dependencies=[Depends(require_permission("admin:write"))],
)
async def create_safety_event_review(
    safety_event_id: str,
    payload: AdminSafetyReviewCreateRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> AdminSafetyReviewResponse:
    service = SafetyReviewService(session)
    try:
        return await service.create_review(
            safety_event_id=safety_event_id,
            reviewer_id=payload.reviewer_id,
            review_status=payload.review_status,
            reviewer_note=payload.reviewer_note,
            human_summary=payload.human_summary,
            decision_rationale=payload.decision_rationale,
            resolution_type=payload.resolution_type,
            escalation_required=payload.escalation_required,
            escalation_status=payload.escalation_status,
            review_payload_json=payload.review_payload_json,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/reviewer-dashboard", response_model=AdminReviewerDashboardResponse)
async def get_reviewer_dashboard(
    session: AsyncSession = Depends(db_session_dep),
) -> AdminReviewerDashboardResponse:
    service = SafetyReviewService(session)
    payload = await service.build_reviewer_dashboard()
    return AdminReviewerDashboardResponse(**payload)


@router.get("/escalation-analytics", response_model=AdminEscalationAnalyticsResponse)
async def get_escalation_analytics(
    session: AsyncSession = Depends(db_session_dep),
) -> AdminEscalationAnalyticsResponse:
    service = SafetyReviewService(session)
    payload = await service.build_escalation_analytics()
    return AdminEscalationAnalyticsResponse(**payload)


@router.get("/audit-timeline", response_model=list[AdminAuditLogResponse])
async def get_audit_timeline(
    limit: int = 100,
    session: AsyncSession = Depends(db_session_dep),
) -> list[AdminAuditLogResponse]:
    service = SafetyReviewService(session)
    return await service.list_audit_timeline(limit=limit)