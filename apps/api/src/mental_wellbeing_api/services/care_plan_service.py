from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta
from statistics import mean
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.db.base import Base
from mental_wellbeing_api.models.care_plan import CarePlan
from mental_wellbeing_api.models.care_plan_event import CarePlanEvent
from mental_wellbeing_api.services.audit_log_service import AuditLogService
from mental_wellbeing_api.services.localization_service import LocalizationService


class CarePlanService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.audit = AuditLogService(session)
        self.localization = LocalizationService(session)

    async def ensure_tables(self) -> None:
        conn = await self.session.connection()
        await conn.run_sync(
            lambda sync_conn: Base.metadata.create_all(
                bind=sync_conn,
                tables=[
                    CarePlan.__table__,
                    CarePlanEvent.__table__,
                ],
                checkfirst=True,
            )
        )

    async def _reload_care_plan(self, care_plan_id: str) -> CarePlan:
        row = await self.session.get(CarePlan, care_plan_id)
        if row is None:
            raise ValueError("Care plan not found")
        await self.session.refresh(row)
        return row

    def _first_step_key(self, sequence_json: dict[str, Any] | None) -> str | None:
        steps = (sequence_json or {}).get("steps") or []
        if not steps:
            return None
        return steps[0].get("key")

    def _resolve_next_check_in_at(
        self,
        *,
        start_at: datetime | None,
        cadence_json: dict[str, Any] | None,
    ) -> datetime | None:
        cadence = cadence_json or {}
        every_n_days = int(cadence.get("every_n_days", 7))
        anchor = start_at or datetime.now(UTC)
        return anchor + timedelta(days=max(every_n_days, 1))

    def _sync_schedule_contract(self, care_plan: CarePlan) -> dict[str, Any]:
        return {
            **(care_plan.schedule_contract_json or {}),
            "orchestration": "care_plan_scheduler_v1",
            "schedule_aware": True,
            "next_check_in_at": care_plan.next_check_in_at.isoformat()
            if care_plan.next_check_in_at
            else None,
        }

    def _is_overdue(self, care_plan: CarePlan, now: datetime | None = None) -> bool:
        effective_now = now or datetime.now(UTC)
        return (
            care_plan.status == "active"
            and care_plan.next_check_in_at is not None
            and care_plan.next_check_in_at < effective_now
        )

    def _is_at_risk(self, care_plan: CarePlan, now: datetime | None = None) -> bool:
        effective_now = now or datetime.now(UTC)
        adherence_json = care_plan.adherence_json or {}
        avg_score = adherence_json.get("avg_score")
        check_in_count = int(adherence_json.get("check_in_count") or 0)

        if care_plan.status != "active":
            return False

        if self._is_overdue(care_plan, effective_now):
            return True

        if isinstance(avg_score, (int, float)) and float(avg_score) < 0.6:
            return True

        if (
            check_in_count == 0
            and care_plan.created_at is not None
            and care_plan.created_at < effective_now - timedelta(days=7)
        ):
            return True

        return False

    def _default_sequence(self, program_key: str, language: str) -> dict[str, Any]:
        title = self.localization.localize_text(
            "care_plan_title_default",
            language,
            "Continue your care plan",
        )
        return {
            "program_key": program_key,
            "steps": [
                {
                    "key": "stabilize",
                    "title": title,
                    "order": 1,
                    "goal": "Establish a small repeatable baseline.",
                },
                {
                    "key": "practice",
                    "title": "Practice consistently",
                    "order": 2,
                    "goal": "Repeat the helpful step often enough to make it easier.",
                },
                {
                    "key": "review",
                    "title": "Review and adapt",
                    "order": 3,
                    "goal": "Check what is helping and adjust gently.",
                },
            ],
        }

    async def create_care_plan(
        self,
        *,
        payload: dict[str, Any],
    ) -> CarePlan:
        await self.ensure_tables()

        preferred_language = self.localization.normalize_language(
            payload.get("preferred_language")
        )
        start_at = payload.get("start_at")
        cadence_json = payload.get("cadence_json") or {"every_n_days": 7}
        sequence_json = payload.get("sequence_json") or self._default_sequence(
            str(payload["program_key"]),
            preferred_language,
        )
        steps = sequence_json.get("steps") or []
        first_step_key = self._first_step_key(sequence_json)
        next_check_in_at = self._resolve_next_check_in_at(
            start_at=start_at,
            cadence_json=cadence_json,
        )

        row = CarePlan(
            user_id=str(payload["user_id"]),
            organization_id=str(payload["organization_id"])
            if payload.get("organization_id")
            else None,
            session_id=str(payload["session_id"]) if payload.get("session_id") else None,
            action_plan_id=str(payload["action_plan_id"])
            if payload.get("action_plan_id")
            else None,
            source_agent=str(payload["source_agent"]),
            program_key=str(payload["program_key"]),
            title=str(payload["title"]),
            description=payload.get("description"),
            preferred_language=preferred_language,
            timezone=payload.get("timezone"),
            start_at=start_at,
            next_check_in_at=next_check_in_at,
            current_step_key=first_step_key,
            cadence_json=cadence_json,
            sequence_json=sequence_json,
            progress_json={
                "completed_step_count": 0,
                "total_step_count": len(steps),
                "completion_pct": 0.0,
            },
            adherence_json={
                "latest_score": None,
                "avg_score": None,
                "check_in_count": 0,
            },
            schedule_contract_json={
                "orchestration": "care_plan_scheduler_v1",
                "schedule_aware": True,
                "next_check_in_at": next_check_in_at.isoformat()
                if next_check_in_at
                else None,
            },
            metadata_json=payload.get("metadata_json"),
        )
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)

        await self.record_event(
            care_plan_id=row.id,
            user_id=row.user_id,
            event_type="created",
            event_status=row.status,
            step_key=row.current_step_key,
            adherence_score=None,
            notes="Care plan created.",
            event_payload_json={
                "program_key": row.program_key,
                "preferred_language": row.preferred_language,
            },
            create_audit=False,
        )

        await self.audit.create_log(
            event_type="care_plan_created",
            entity_type="care_plan",
            entity_id=row.id,
            title=f"Care plan created: {row.program_key}",
            details=row.title,
            actor_type="system",
            user_id=row.user_id,
            event_payload_json={
                "organization_id": row.organization_id,
                "program_key": row.program_key,
                "preferred_language": row.preferred_language,
                "status": row.status,
            },
        )

        return await self._reload_care_plan(row.id)

    async def get_care_plan(self, care_plan_id: str) -> CarePlan | None:
        await self.ensure_tables()
        return await self.session.get(CarePlan, care_plan_id)

    async def list_care_plans(
        self,
        *,
        user_id: str | None = None,
        organization_id: str | None = None,
        status: str | None = None,
        preferred_language: str | None = None,
        program_key: str | None = None,
        attention_state: str | None = None,
        limit: int = 100,
    ) -> list[CarePlan]:
        await self.ensure_tables()

        stmt = select(CarePlan)

        if user_id:
            stmt = stmt.where(CarePlan.user_id == user_id)
        if organization_id:
            stmt = stmt.where(CarePlan.organization_id == organization_id)
        if status:
            stmt = stmt.where(CarePlan.status == status)
        if preferred_language:
            stmt = stmt.where(
                CarePlan.preferred_language
                == self.localization.normalize_language(preferred_language)
            )
        if program_key:
            stmt = stmt.where(CarePlan.program_key == program_key)

        fetch_limit = 1000 if attention_state else limit
        rows = await self.session.scalars(
            stmt.order_by(desc(CarePlan.updated_at)).limit(fetch_limit)
        )
        items = list(rows.all())

        if attention_state:
            now = datetime.now(UTC)
            if attention_state == "overdue":
                items = [item for item in items if self._is_overdue(item, now)]
            elif attention_state == "at_risk":
                items = [item for item in items if self._is_at_risk(item, now)]
            elif attention_state == "on_track":
                items = [
                    item
                    for item in items
                    if item.status == "active" and not self._is_at_risk(item, now)
                ]
            items = items[:limit]

        return items

    async def update_care_plan(
        self,
        *,
        care_plan_id: str,
        payload: dict[str, Any],
    ) -> CarePlan:
        await self.ensure_tables()
        row = await self.session.get(CarePlan, care_plan_id)
        if row is None:
            raise ValueError("Care plan not found")

        cadence_changed = False
        sequence_changed = False

        if payload.get("title") is not None:
            row.title = str(payload["title"])
        if payload.get("description") is not None:
            row.description = payload.get("description")
        if payload.get("status") is not None:
            row.status = str(payload["status"])
            if row.status == "completed":
                row.last_completed_at = datetime.now(UTC)
        if payload.get("current_step_key") is not None:
            row.current_step_key = str(payload["current_step_key"])
        if payload.get("preferred_language") is not None:
            row.preferred_language = self.localization.normalize_language(
                payload["preferred_language"]
            )
        if payload.get("timezone") is not None:
            row.timezone = payload["timezone"]
        if payload.get("cadence_json") is not None:
            row.cadence_json = payload["cadence_json"]
            cadence_changed = True
        if payload.get("sequence_json") is not None:
            row.sequence_json = payload["sequence_json"]
            sequence_changed = True
        if payload.get("next_check_in_at") is not None:
            row.next_check_in_at = payload["next_check_in_at"]
        elif cadence_changed:
            row.next_check_in_at = self._resolve_next_check_in_at(
                start_at=datetime.now(UTC),
                cadence_json=row.cadence_json,
            )
        if payload.get("metadata_json") is not None:
            row.metadata_json = payload["metadata_json"]
        if payload.get("progress_json") is not None:
            row.progress_json = payload["progress_json"]
        if payload.get("adherence_json") is not None:
            row.adherence_json = payload["adherence_json"]

        if sequence_changed:
            first_step_key = self._first_step_key(row.sequence_json)
            step_keys = {
                item.get("key")
                for item in ((row.sequence_json or {}).get("steps") or [])
                if item.get("key")
            }
            if row.current_step_key not in step_keys:
                row.current_step_key = first_step_key

            if row.progress_json is not None:
                row.progress_json = {
                    **row.progress_json,
                    "total_step_count": len((row.sequence_json or {}).get("steps") or []),
                }

        row.schedule_contract_json = self._sync_schedule_contract(row)

        await self.session.commit()
        return await self._reload_care_plan(care_plan_id)

    async def transition_lifecycle(
        self,
        *,
        care_plan_id: str,
        action: str,
        notes: str | None,
        reset_history: bool = True,
    ) -> CarePlan:
        care_plan = await self.get_care_plan(care_plan_id)
        if care_plan is None:
            raise ValueError("Care plan not found")

        if action == "pause":
            care_plan.status = "paused"
        elif action == "resume":
            care_plan.status = "active"
            care_plan.next_check_in_at = self._resolve_next_check_in_at(
                start_at=datetime.now(UTC),
                cadence_json=care_plan.cadence_json,
            )
        elif action == "restart":
            care_plan.status = "active"
            care_plan.current_step_key = self._first_step_key(care_plan.sequence_json)
            care_plan.last_completed_at = None
            care_plan.next_check_in_at = self._resolve_next_check_in_at(
                start_at=datetime.now(UTC),
                cadence_json=care_plan.cadence_json,
            )
            care_plan.progress_json = {
                "completed_step_count": 0,
                "total_step_count": len((care_plan.sequence_json or {}).get("steps") or []),
                "completion_pct": 0.0,
            }
            if reset_history:
                care_plan.adherence_json = {
                    "latest_score": None,
                    "avg_score": None,
                    "check_in_count": 0,
                }
        else:
            raise ValueError("Unsupported lifecycle action")

        care_plan.schedule_contract_json = self._sync_schedule_contract(care_plan)

        await self.session.commit()
        await self.session.refresh(care_plan)

        await self.record_event(
            care_plan_id=care_plan.id,
            user_id=care_plan.user_id,
            event_type=f"program_{action}",
            event_status=care_plan.status,
            step_key=care_plan.current_step_key,
            adherence_score=None,
            notes=notes or f"Program {action} requested.",
            event_payload_json={
                "action": action,
                "reset_history": reset_history,
            },
        )

        return await self._reload_care_plan(care_plan.id)

    async def record_event(
        self,
        *,
        care_plan_id: str,
        user_id: str,
        event_type: str,
        event_status: str | None,
        step_key: str | None,
        adherence_score: float | None,
        notes: str | None,
        event_payload_json: dict[str, Any] | None,
        create_audit: bool = True,
    ) -> CarePlanEvent:
        await self.ensure_tables()
        care_plan = await self.session.get(CarePlan, care_plan_id)
        if care_plan is None:
            raise ValueError("Care plan not found")

        row = CarePlanEvent(
            care_plan_id=care_plan_id,
            user_id=user_id,
            event_type=event_type,
            event_status=event_status,
            step_key=step_key,
            adherence_score=adherence_score,
            notes=notes,
            event_payload_json=event_payload_json,
        )
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)

        await self._refresh_rollups(care_plan_id)

        if create_audit:
            await self.audit.create_log(
                event_type="care_plan_event_recorded",
                entity_type="care_plan_event",
                entity_id=row.id,
                title=f"Care plan event: {event_type}",
                details=notes,
                actor_type="system",
                user_id=user_id,
                event_payload_json={
                    "care_plan_id": care_plan_id,
                    "event_status": event_status,
                    "step_key": step_key,
                    "adherence_score": adherence_score,
                },
            )
        return row

    async def list_events(
        self,
        *,
        care_plan_id: str,
        limit: int = 200,
    ) -> list[CarePlanEvent]:
        await self.ensure_tables()
        rows = await self.session.scalars(
            select(CarePlanEvent)
            .where(CarePlanEvent.care_plan_id == care_plan_id)
            .order_by(desc(CarePlanEvent.created_at))
            .limit(limit)
        )
        return list(rows.all())

    async def advance_step(
        self,
        *,
        care_plan_id: str,
        next_step_key: str | None,
        notes: str | None,
    ) -> CarePlan:
        care_plan = await self.get_care_plan(care_plan_id)
        if care_plan is None:
            raise ValueError("Care plan not found")

        sequence = care_plan.sequence_json or {}
        steps = sequence.get("steps") or []
        current_key = care_plan.current_step_key

        resolved_next = next_step_key
        if resolved_next is None and steps:
            current_index = 0
            for idx, item in enumerate(steps):
                if item.get("key") == current_key:
                    current_index = idx
                    break

            if current_index + 1 < len(steps):
                resolved_next = steps[current_index + 1].get("key")
            else:
                resolved_next = current_key
                care_plan.status = "completed"
                care_plan.last_completed_at = datetime.now(UTC)

        care_plan.current_step_key = resolved_next
        care_plan.next_check_in_at = self._resolve_next_check_in_at(
            start_at=datetime.now(UTC),
            cadence_json=care_plan.cadence_json,
        )
        care_plan.schedule_contract_json = self._sync_schedule_contract(care_plan)

        await self.session.commit()
        await self.session.refresh(care_plan)

        await self.record_event(
            care_plan_id=care_plan.id,
            user_id=care_plan.user_id,
            event_type="step_advanced",
            event_status=care_plan.status,
            step_key=resolved_next,
            adherence_score=None,
            notes=notes,
            event_payload_json={
                "previous_step_key": current_key,
                "next_step_key": resolved_next,
            },
        )

        return await self._reload_care_plan(care_plan.id)

    async def _refresh_rollups(self, care_plan_id: str) -> None:
        care_plan = await self.session.get(CarePlan, care_plan_id)
        if care_plan is None:
            return

        events = await self.list_events(care_plan_id=care_plan_id, limit=500)
        adherence_scores = [
            float(item.adherence_score)
            for item in events
            if item.adherence_score is not None
        ]
        completed_steps = len(
            [item for item in events if item.event_type in {"step_advanced", "completed"}]
        )
        total_steps = len((care_plan.sequence_json or {}).get("steps") or [])

        latest_adherence_score = None
        for item in events:
            if item.adherence_score is not None:
                latest_adherence_score = float(item.adherence_score)
                break

        care_plan.progress_json = {
            "completed_step_count": completed_steps,
            "total_step_count": total_steps,
            "completion_pct": round((completed_steps / total_steps) * 100, 2)
            if total_steps
            else 0.0,
        }
        care_plan.adherence_json = {
            "latest_score": latest_adherence_score,
            "avg_score": round(mean(adherence_scores), 2) if adherence_scores else None,
            "check_in_count": len(adherence_scores),
        }
        care_plan.schedule_contract_json = self._sync_schedule_contract(care_plan)

        await self.session.commit()
        await self.session.refresh(care_plan)

    async def build_user_summary(self, *, user_id: str) -> dict[str, Any]:
        items = await self.list_care_plans(user_id=user_id, limit=200)
        now = datetime.now(UTC)
        adherence_scores = [
            float((item.adherence_json or {}).get("avg_score"))
            for item in items
            if (item.adherence_json or {}).get("avg_score") is not None
        ]
        by_program = Counter(item.program_key for item in items if item.program_key)
        return {
            "user_id": user_id,
            "total_care_plans": len(items),
            "active_care_plans": len([item for item in items if item.status == "active"]),
            "completed_care_plans": len(
                [item for item in items if item.status == "completed"]
            ),
            "avg_adherence_score": round(mean(adherence_scores), 2)
            if adherence_scores
            else None,
            "due_today_count": len(
                [
                    item
                    for item in items
                    if item.next_check_in_at is not None and item.next_check_in_at <= now
                ]
            ),
            "by_program_key": dict(by_program),
        }

    async def build_admin_overview(
        self,
        *,
        organization_id: str | None = None,
    ) -> dict[str, Any]:
        items = await self.list_care_plans(organization_id=organization_id, limit=1000)
        status_counter = Counter(item.status for item in items if item.status)
        program_counter = Counter(item.program_key for item in items if item.program_key)
        language_counter = Counter(
            self.localization.normalize_language(item.preferred_language) for item in items
        )

        adherence_scores = [
            float((item.adherence_json or {}).get("avg_score"))
            for item in items
            if (item.adherence_json or {}).get("avg_score") is not None
        ]
        now = datetime.now(UTC)
        overdue = len([item for item in items if self._is_overdue(item, now)])
        at_risk = len([item for item in items if self._is_at_risk(item, now)])
        upcoming_24h = len(
            [
                item
                for item in items
                if item.status == "active"
                and item.next_check_in_at is not None
                and now <= item.next_check_in_at <= now + timedelta(hours=24)
            ]
        )
        needs_attention = len(
            [
                item
                for item in items
                if self._is_overdue(item, now)
                or self._is_at_risk(item, now)
                or item.status == "paused"
            ]
        )

        event_stmt = select(CarePlanEvent).order_by(desc(CarePlanEvent.created_at)).limit(20)
        if organization_id:
            care_plan_ids = [item.id for item in items]
            if care_plan_ids:
                event_stmt = event_stmt.where(CarePlanEvent.care_plan_id.in_(care_plan_ids))
            else:
                return {
                    "total_care_plans": 0,
                    "active_care_plans": 0,
                    "completed_care_plans": 0,
                    "paused_care_plans": 0,
                    "overdue_check_ins": 0,
                    "at_risk_care_plans": 0,
                    "upcoming_check_ins_24h": 0,
                    "needs_attention_count": 0,
                    "avg_adherence_score": None,
                    "status_breakdown": {},
                    "program_breakdown": {},
                    "language_breakdown": {},
                    "recent_events": [],
                }

        recent_events = list((await self.session.scalars(event_stmt)).all())

        return {
            "total_care_plans": len(items),
            "active_care_plans": status_counter.get("active", 0),
            "completed_care_plans": status_counter.get("completed", 0),
            "paused_care_plans": status_counter.get("paused", 0),
            "overdue_check_ins": overdue,
            "at_risk_care_plans": at_risk,
            "upcoming_check_ins_24h": upcoming_24h,
            "needs_attention_count": needs_attention,
            "avg_adherence_score": round(mean(adherence_scores), 2)
            if adherence_scores
            else None,
            "status_breakdown": dict(status_counter),
            "program_breakdown": dict(program_counter),
            "language_breakdown": dict(language_counter),
            "recent_events": recent_events,
        }