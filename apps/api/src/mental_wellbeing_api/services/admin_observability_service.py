from __future__ import annotations

from collections import Counter
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.models.admin_config_version import AdminConfigVersion
from mental_wellbeing_api.models.agent_trace import AgentTrace
from mental_wellbeing_api.models.audit_log import AuditLog
from mental_wellbeing_api.models.conversation import ConversationSession
from mental_wellbeing_api.models.follow_up_event import FollowUpEvent
from mental_wellbeing_api.models.follow_up_plan import FollowUpPlan
from mental_wellbeing_api.models.intervention_log import InterventionLog
from mental_wellbeing_api.models.safety_event import SafetyEvent
from mental_wellbeing_api.models.safety_flag import SafetyFlag


class AdminObservabilityService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_agent_traces(
        self,
        *,
        limit: int = 100,
        trace_name: str | None = None,
        user_id: str | None = None,
        agent_name: str | None = None,
    ) -> list[AgentTrace]:
        stmt = select(AgentTrace).order_by(desc(AgentTrace.created_at)).limit(limit)
        if trace_name:
            stmt = stmt.where(AgentTrace.trace_name == trace_name)
        if user_id:
            stmt = stmt.where(AgentTrace.user_id == user_id)
        if agent_name:
            stmt = stmt.where(AgentTrace.agent_name == agent_name)
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def list_grouped_runtime_executions(self, *, limit: int = 100) -> list[dict[str, Any]]:
        rows = list(
            (
                await self.session.scalars(
                    select(AgentTrace)
                    .order_by(desc(AgentTrace.created_at))
                    .limit(max(limit * 10, 200))
                )
            ).all()
        )

        grouped: dict[str, dict[str, Any]] = {}
        for row in rows:
            bucket = grouped.setdefault(
                row.trace_name,
                {
                    "trace_name": row.trace_name,
                    "user_id": row.user_id,
                    "status": row.status,
                    "started_at": row.created_at,
                    "latest_at": row.created_at,
                    "event_count": 0,
                    "agents": [],
                    "handoff_pairs": [],
                },
            )
            bucket["event_count"] += 1
            bucket["latest_at"] = max(bucket["latest_at"], row.created_at)
            if row.user_id and not bucket["user_id"]:
                bucket["user_id"] = row.user_id
            if row.agent_name not in bucket["agents"]:
                bucket["agents"].append(row.agent_name)
            if row.handoff_from_agent and row.handoff_to_agent:
                pair = f"{row.handoff_from_agent}->{row.handoff_to_agent}"
                if pair not in bucket["handoff_pairs"]:
                    bucket["handoff_pairs"].append(pair)

        items = sorted(grouped.values(), key=lambda item: item["latest_at"], reverse=True)
        return items[:limit]

    async def get_runtime_execution_detail(self, trace_name: str) -> dict[str, Any]:
        traces = await self.list_agent_traces(limit=500, trace_name=trace_name)
        return {
            "trace_name": trace_name,
            "event_count": len(traces),
            "events": traces,
        }

    async def list_intervention_logs(self, *, limit: int = 100) -> list[InterventionLog]:
        result = await self.session.scalars(
            select(InterventionLog).order_by(desc(InterventionLog.created_at)).limit(limit)
        )
        return list(result.all())

    async def get_intervention_overview(self) -> dict[str, Any]:
        rows = await self.list_intervention_logs(limit=200)
        type_counter = Counter()
        outcome_counter = Counter()
        ratings: list[float] = []

        for row in rows:
            type_counter[row.intervention_type] += 1
            if row.outcome_status:
                outcome_counter[row.outcome_status] += 1
            if row.effectiveness_rating is not None:
                ratings.append(float(row.effectiveness_rating))

        return {
            "total_logs": len(rows),
            "avg_effectiveness_rating": round(sum(ratings) / len(ratings), 2) if ratings else None,
            "intervention_type_breakdown": dict(type_counter),
            "outcome_status_breakdown": dict(outcome_counter),
            "recent_logs_count": len(rows[:20]),
        }

    async def get_flagged_session_detail(self, flag_id: str) -> dict[str, Any]:
        flag = await self.session.get(SafetyFlag, flag_id)
        if flag is None:
            raise ValueError("Safety flag not found")

        traces = await self.list_agent_traces(limit=25, user_id=flag.user_id)
        sessions = list(
            (
                await self.session.scalars(
                    select(ConversationSession)
                    .where(ConversationSession.user_id == flag.user_id)
                    .order_by(desc(ConversationSession.updated_at))
                    .limit(10)
                )
            ).all()
        )

        return {
            "flag": flag,
            "related_traces": traces,
            "related_sessions": sessions,
        }

    async def get_safety_flow_overview(self) -> dict[str, Any]:
        total_safety_events = int((await self.session.scalar(select(func.count(SafetyEvent.id)))) or 0)
        queued_safety_events = int(
            (
                await self.session.scalar(
                    select(func.count(SafetyEvent.id)).where(SafetyEvent.queue_status == "queued")
                )
            )
            or 0
        )
        in_review_safety_events = int(
            (
                await self.session.scalar(
                    select(func.count(SafetyEvent.id)).where(SafetyEvent.queue_status == "in_review")
                )
            )
            or 0
        )
        resolved_safety_events = int(
            (
                await self.session.scalar(
                    select(func.count(SafetyEvent.id)).where(SafetyEvent.queue_status == "resolved")
                )
            )
            or 0
        )
        high_risk_safety_events = int(
            (
                await self.session.scalar(
                    select(func.count(SafetyEvent.id)).where(SafetyEvent.risk_level == "high")
                )
            )
            or 0
        )
        critical_safety_events = int(
            (
                await self.session.scalar(
                    select(func.count(SafetyEvent.id)).where(SafetyEvent.severity == "critical")
                )
            )
            or 0
        )
        immutable_audit_log_count = int(
            (
                await self.session.scalar(
                    select(func.count(AuditLog.id)).where(AuditLog.is_immutable.is_(True))
                )
            )
            or 0
        )

        traces = await self.list_agent_traces(limit=500)
        grouped_trace_snapshots: dict[str, dict[str, Any]] = {}

        for trace in traces:
            payload = trace.input_payload_json or {}
            trace_key = trace.trace_name
            bucket = grouped_trace_snapshots.setdefault(
                trace_key,
                {
                    "alertable_safety_trace": False,
                    "decision_path_label": payload.get("decision_path_label"),
                    "review_priority": payload.get("review_priority"),
                    "safety_temporal_contract": payload.get("safety_temporal_contract", {}),
                },
            )

            if bool(payload.get("alertable_safety_trace")):
                bucket["alertable_safety_trace"] = True
            if payload.get("decision_path_label"):
                bucket["decision_path_label"] = payload.get("decision_path_label")
            if payload.get("review_priority"):
                bucket["review_priority"] = payload.get("review_priority")
            if payload.get("safety_temporal_contract"):
                bucket["safety_temporal_contract"] = payload.get("safety_temporal_contract", {})

        alertable_trace_count = 0
        decision_path_counter = Counter()
        review_priority_counter = Counter()
        temporal_safety_contract_status_breakdown = Counter()

        for snapshot in grouped_trace_snapshots.values():
            if not snapshot["alertable_safety_trace"]:
                continue

            alertable_trace_count += 1
            decision_path_counter[str(snapshot.get("decision_path_label") or "unknown")] += 1
            review_priority_counter[str(snapshot.get("review_priority") or "normal")] += 1

            contract = snapshot.get("safety_temporal_contract")
            if isinstance(contract, dict) and contract:
                temporal_safety_contract_status_breakdown[
                    str(contract.get("status") or "unknown")
                ] += 1
            else:
                temporal_safety_contract_status_breakdown["missing"] += 1

        escalation_rows = (
            await self.session.execute(
                select(SafetyEvent.escalation_status, func.count(SafetyEvent.id).label("count"))
                .group_by(SafetyEvent.escalation_status)
                .order_by(desc("count"))
            )
        ).all()

        return {
            "total_safety_events": total_safety_events,
            "queued_safety_events": queued_safety_events,
            "in_review_safety_events": in_review_safety_events,
            "resolved_safety_events": resolved_safety_events,
            "high_risk_safety_events": high_risk_safety_events,
            "critical_safety_events": critical_safety_events,
            "alertable_trace_count": alertable_trace_count,
            "immutable_audit_log_count": immutable_audit_log_count,
            "decision_path_breakdown": dict(decision_path_counter),
            "review_priority_breakdown": dict(review_priority_counter),
            "escalation_status_breakdown": {
                str(row.escalation_status): int(row.count or 0)
                for row in escalation_rows
                if row.escalation_status
            },
            "temporal_safety_contract_status_breakdown": dict(
                temporal_safety_contract_status_breakdown
            ),
        }

    async def get_ops_overview(self) -> dict[str, Any]:
        total_flags = int((await self.session.scalar(select(func.count(SafetyFlag.id)))) or 0)
        unresolved_flags = int(
            (
                await self.session.scalar(
                    select(func.count(SafetyFlag.id)).where(SafetyFlag.is_resolved.is_(False))
                )
            )
            or 0
        )
        total_traces = int((await self.session.scalar(select(func.count(AgentTrace.id)))) or 0)
        total_intervention_logs = int(
            (await self.session.scalar(select(func.count(InterventionLog.id)))) or 0
        )
        total_follow_up_plans = int(
            (await self.session.scalar(select(func.count(FollowUpPlan.id)))) or 0
        )
        total_follow_up_events = int(
            (await self.session.scalar(select(func.count(FollowUpEvent.id)))) or 0
        )
        active_config_versions = int(
            (
                await self.session.scalar(
                    select(func.count(AdminConfigVersion.id)).where(
                        AdminConfigVersion.is_active.is_(True)
                    )
                )
            )
            or 0
        )

        latest_traces = await self.list_grouped_runtime_executions(limit=10)
        intervention_overview = await self.get_intervention_overview()
        safety_flow_overview = await self.get_safety_flow_overview()

        return {
            "total_flags": total_flags,
            "unresolved_flags": unresolved_flags,
            "total_traces": total_traces,
            "total_intervention_logs": total_intervention_logs,
            "total_follow_up_plans": total_follow_up_plans,
            "total_follow_up_events": total_follow_up_events,
            "active_config_versions": active_config_versions,
            "latest_runtime_executions": latest_traces,
            "intervention_overview": intervention_overview,
            "safety_flow_overview": safety_flow_overview,
        }

    async def get_analytics_overview(self) -> dict[str, Any]:
        traces = await self.list_agent_traces(limit=500)
        specialist_counter = Counter()
        strategy_counter = Counter()
        status_counter = Counter()

        for trace in traces:
            status_counter[trace.status] += 1
            payload = trace.input_payload_json or {}
            specialist = payload.get("specialist_agent")
            strategy = payload.get("support_strategy")
            if specialist:
                specialist_counter[str(specialist)] += 1
            if strategy:
                strategy_counter[str(strategy)] += 1

        follow_up_rows = list(
            (
                await self.session.scalars(
                    select(FollowUpPlan).order_by(desc(FollowUpPlan.created_at)).limit(200)
                )
            ).all()
        )
        follow_up_status_breakdown = dict(
            Counter(item.status for item in follow_up_rows if item.status)
        )

        intervention_overview = await self.get_intervention_overview()
        safety_flow_overview = await self.get_safety_flow_overview()

        return {
            "runtime_status_breakdown": dict(status_counter),
            "specialist_agent_breakdown": dict(specialist_counter),
            "support_strategy_breakdown": dict(strategy_counter),
            "follow_up_status_breakdown": follow_up_status_breakdown,
            "intervention_overview": intervention_overview,
            "safety_flow_overview": safety_flow_overview,
        }