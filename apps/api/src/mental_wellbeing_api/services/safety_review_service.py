from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.models.audit_log import AuditLog
from mental_wellbeing_api.models.safety_event import SafetyEvent
from mental_wellbeing_api.models.safety_flag import SafetyFlag
from mental_wellbeing_api.models.safety_review import SafetyReview
from mental_wellbeing_api.services.audit_log_service import AuditLogService
from mental_wellbeing_api.services.storage_service import StorageService


class SafetyReviewService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.audit = AuditLogService(session)
        self.storage = StorageService(session)

    async def create_safety_event(
        self,
        *,
        user_id: str,
        session_id: str | None,
        safety_flag_id: str | None,
        event_type: str,
        severity: str,
        risk_level: str,
        title: str,
        summary: str | None = None,
        evidence_json: dict[str, Any] | None = None,
        event_payload_json: dict[str, Any] | None = None,
        requires_human_review: bool = True,
        escalation_channel: str | None = None,
    ) -> SafetyEvent:
        item = SafetyEvent(
            user_id=user_id,
            session_id=session_id,
            safety_flag_id=safety_flag_id,
            event_type=event_type,
            severity=severity,
            risk_level=risk_level,
            title=title,
            summary=summary,
            evidence_json=evidence_json,
            event_payload_json=event_payload_json,
            requires_human_review=requires_human_review,
            escalation_channel=escalation_channel,
            queue_status="queued" if requires_human_review else "auto_closed",
            escalation_status="pending" if requires_human_review else "not_required",
        )
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)

        await self.audit.create_log(
            event_type="safety_event_created",
            entity_type="safety_event",
            entity_id=item.id,
            title=item.title,
            details=item.summary,
            actor_type="system",
            actor_id="risk_triage",
            user_id=item.user_id,
            session_id=item.session_id,
            safety_event_id=item.id,
            event_payload_json={
                "event_type": item.event_type,
                "severity": item.severity,
                "risk_level": item.risk_level,
                "queue_status": item.queue_status,
            },
        )

        if evidence_json is not None:
            await self.storage.persist_json_artifact(
                scope_type="safety_event",
                scope_id=item.id,
                artifact_kind="evidence_json",
                file_name=f"safety-event-evidence-{item.id}.json",
                payload=evidence_json,
                metadata_json={
                    "risk_level": item.risk_level,
                    "event_type": item.event_type,
                },
            )

        if event_payload_json is not None:
            await self.storage.persist_json_artifact(
                scope_type="safety_event",
                scope_id=item.id,
                artifact_kind="event_payload_json",
                file_name=f"safety-event-payload-{item.id}.json",
                payload=event_payload_json,
                metadata_json={
                    "risk_level": item.risk_level,
                    "event_type": item.event_type,
                },
            )

        return item

    async def list_safety_events(
        self,
        *,
        limit: int = 50,
        queue_status: str | None = None,
        risk_level: str | None = None,
    ) -> list[SafetyEvent]:
        stmt = select(SafetyEvent).order_by(desc(SafetyEvent.detected_at)).limit(limit)
        if queue_status:
            stmt = stmt.where(SafetyEvent.queue_status == queue_status)
        if risk_level:
            stmt = stmt.where(SafetyEvent.risk_level == risk_level)
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def get_safety_event(self, *, safety_event_id: str) -> SafetyEvent | None:
        return await self.session.scalar(
            select(SafetyEvent).where(SafetyEvent.id == safety_event_id)
        )

    async def list_reviews_for_event(self, *, safety_event_id: str) -> list[SafetyReview]:
        result = await self.session.scalars(
            select(SafetyReview)
            .where(SafetyReview.safety_event_id == safety_event_id)
            .order_by(desc(SafetyReview.created_at))
        )
        return list(result.all())

    async def create_review(
        self,
        *,
        safety_event_id: str,
        reviewer_id: str | None,
        review_status: str,
        reviewer_note: str | None,
        human_summary: str | None,
        decision_rationale: str | None,
        resolution_type: str | None,
        escalation_required: bool,
        escalation_status: str | None,
        review_payload_json: dict[str, Any] | None = None,
    ) -> SafetyReview:
        event = await self.session.scalar(
            select(SafetyEvent).where(SafetyEvent.id == safety_event_id)
        )
        if event is None:
            raise ValueError("Safety event not found")

        item = SafetyReview(
            safety_event_id=event.id,
            safety_flag_id=event.safety_flag_id,
            user_id=event.user_id,
            session_id=event.session_id,
            reviewer_id=reviewer_id,
            review_status=review_status,
            reviewer_note=reviewer_note,
            human_summary=human_summary,
            decision_rationale=decision_rationale,
            resolution_type=resolution_type,
            escalation_required=escalation_required,
            escalation_status=escalation_status,
            review_payload_json=review_payload_json or {},
            reviewed_at=datetime.now(timezone.utc),
            resolved_at=datetime.now(timezone.utc)
            if review_status in {"resolved", "closed", "completed"}
            else None,
        )
        self.session.add(item)

        before_event = {
            "queue_status": event.queue_status,
            "escalation_status": event.escalation_status,
            "assigned_at": event.assigned_at.isoformat() if event.assigned_at else None,
            "resolved_at": event.resolved_at.isoformat() if event.resolved_at else None,
        }

        event.queue_status = (
            "resolved"
            if review_status in {"resolved", "closed", "completed"}
            else "in_review"
        )
        event.assigned_at = event.assigned_at or datetime.now(timezone.utc)
        event.escalation_status = escalation_status or (
            "escalated" if escalation_required else "reviewed"
        )
        if review_status in {"resolved", "closed", "completed"}:
            event.resolved_at = datetime.now(timezone.utc)

        if event.safety_flag_id:
            flag = await self.session.scalar(
                select(SafetyFlag).where(SafetyFlag.id == event.safety_flag_id)
            )
            if flag is not None:
                flag.reviewer_note = reviewer_note
                flag.reviewed_at = item.reviewed_at
                if review_status in {"resolved", "closed", "completed"}:
                    flag.is_resolved = True
                    flag.needs_review = False
                    flag.resolved_at = item.resolved_at

        await self.session.commit()
        await self.session.refresh(item)
        await self.session.refresh(event)

        await self.audit.create_log(
            event_type="safety_review_created",
            entity_type="safety_review",
            entity_id=item.id,
            title=f"Safety review for {event.title}",
            details=reviewer_note or human_summary,
            actor_type="reviewer",
            actor_id=reviewer_id,
            user_id=event.user_id,
            session_id=event.session_id,
            safety_event_id=event.id,
            safety_review_id=item.id,
            before_json=before_event,
            after_json={
                "queue_status": event.queue_status,
                "escalation_status": event.escalation_status,
                "review_status": item.review_status,
                "resolution_type": item.resolution_type,
            },
            event_payload_json={
                "escalation_required": escalation_required,
                "review_status": review_status,
            },
        )

        if review_payload_json:
            await self.storage.persist_json_artifact(
                scope_type="safety_review",
                scope_id=item.id,
                artifact_kind="review_payload_json",
                file_name=f"safety-review-payload-{item.id}.json",
                payload=review_payload_json,
                metadata_json={
                    "review_status": item.review_status,
                    "resolution_type": item.resolution_type,
                },
            )

        return item

    async def build_reviewer_dashboard(self) -> dict[str, Any]:
        total_events = int(
            (
                await self.session.execute(
                    select(func.count(SafetyEvent.id))
                )
            ).scalar()
            or 0
        )
        queued_events = int(
            (
                await self.session.execute(
                    select(func.count(SafetyEvent.id)).where(SafetyEvent.queue_status == "queued")
                )
            ).scalar()
            or 0
        )
        in_review_events = int(
            (
                await self.session.execute(
                    select(func.count(SafetyEvent.id)).where(SafetyEvent.queue_status == "in_review")
                )
            ).scalar()
            or 0
        )
        resolved_events = int(
            (
                await self.session.execute(
                    select(func.count(SafetyEvent.id)).where(SafetyEvent.queue_status == "resolved")
                )
            ).scalar()
            or 0
        )

        severity_rows = (
            await self.session.execute(
                select(SafetyEvent.severity, func.count(SafetyEvent.id).label("count"))
                .group_by(SafetyEvent.severity)
                .order_by(desc("count"))
            )
        ).all()

        escalation_rows = (
            await self.session.execute(
                select(SafetyEvent.escalation_status, func.count(SafetyEvent.id).label("count"))
                .group_by(SafetyEvent.escalation_status)
                .order_by(desc("count"))
            )
        ).all()

        recent_reviews = list(
            (
                await self.session.scalars(
                    select(SafetyReview)
                    .order_by(desc(SafetyReview.created_at))
                    .limit(10)
                )
            ).all()
        )

        return {
            "total_events": total_events,
            "queued_events": queued_events,
            "in_review_events": in_review_events,
            "resolved_events": resolved_events,
            "severity_breakdown": {
                str(row.severity): int(row.count or 0)
                for row in severity_rows
                if row.severity
            },
            "escalation_status_breakdown": {
                str(row.escalation_status): int(row.count or 0)
                for row in escalation_rows
                if row.escalation_status
            },
            "recent_reviews": recent_reviews,
        }

    async def build_escalation_analytics(self) -> dict[str, Any]:
        total_events = int(
            (
                await self.session.execute(select(func.count(SafetyEvent.id)))
            ).scalar()
            or 0
        )
        escalated_events = int(
            (
                await self.session.execute(
                    select(func.count(SafetyEvent.id)).where(
                        SafetyEvent.escalation_status.in_(["escalated", "pending", "reviewed"])
                    )
                )
            ).scalar()
            or 0
        )
        high_risk_events = int(
            (
                await self.session.execute(
                    select(func.count(SafetyEvent.id)).where(SafetyEvent.risk_level == "high")
                )
            ).scalar()
            or 0
        )
        critical_events = int(
            (
                await self.session.execute(
                    select(func.count(SafetyEvent.id)).where(SafetyEvent.severity == "critical")
                )
            ).scalar()
            or 0
        )

        event_type_rows = (
            await self.session.execute(
                select(SafetyEvent.event_type, func.count(SafetyEvent.id).label("count"))
                .group_by(SafetyEvent.event_type)
                .order_by(desc("count"))
            )
        ).all()

        return {
            "total_events": total_events,
            "escalated_events": escalated_events,
            "high_risk_events": high_risk_events,
            "critical_events": critical_events,
            "event_type_breakdown": {
                str(row.event_type): int(row.count or 0)
                for row in event_type_rows
                if row.event_type
            },
        }

    async def list_audit_timeline(self, *, limit: int = 100) -> list[AuditLog]:
        result = await self.session.scalars(
            select(AuditLog).order_by(desc(AuditLog.occurred_at)).limit(limit)
        )
        return list(result.all())