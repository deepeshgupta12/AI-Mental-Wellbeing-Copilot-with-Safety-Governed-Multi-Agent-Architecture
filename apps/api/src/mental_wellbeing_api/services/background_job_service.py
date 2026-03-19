from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.models.follow_up_event import FollowUpEvent
from mental_wellbeing_api.models.follow_up_plan import FollowUpPlan


class BackgroundJobService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def run_due_follow_up_sweep(self) -> dict:
        now = datetime.now(UTC)

        rows = list(
            (
                await self.session.scalars(
                    select(FollowUpPlan).where(
                        FollowUpPlan.scheduled_for.is_not(None),
                        FollowUpPlan.scheduled_for <= now,
                        FollowUpPlan.status.in_(["planned", "scheduled"]),
                    )
                )
            ).all()
        )

        processed_ids: list[str] = []
        for plan in rows:
            self.session.add(
                FollowUpEvent(
                    follow_up_plan_id=plan.id,
                    user_id=plan.user_id,
                    event_type="triggered",
                    outcome_status="due",
                    notes="Due follow-up picked up by background sweep.",
                    event_payload_json={"swept_at": now.isoformat()},
                )
            )
            processed_ids.append(plan.id)

        await self.session.commit()

        return {
            "processed_count": len(processed_ids),
            "processed_plan_ids": processed_ids,
        }

    async def mark_overdue_follow_ups(self) -> dict:
        now = datetime.now(UTC)

        rows = list(
            (
                await self.session.scalars(
                    select(FollowUpPlan).where(
                        FollowUpPlan.scheduled_for.is_not(None),
                        FollowUpPlan.scheduled_for < now,
                        FollowUpPlan.status == "planned",
                    )
                )
            ).all()
        )

        marked_ids: list[str] = []
        for plan in rows:
            plan.status = "scheduled"
            self.session.add(
                FollowUpEvent(
                    follow_up_plan_id=plan.id,
                    user_id=plan.user_id,
                    event_type="overdue_marked",
                    outcome_status="overdue",
                    notes="Follow-up plan marked overdue by background job.",
                    event_payload_json={"overdue_marked_at": now.isoformat()},
                )
            )
            marked_ids.append(plan.id)

        await self.session.commit()

        return {
            "marked_count": len(marked_ids),
            "marked_plan_ids": marked_ids,
        }