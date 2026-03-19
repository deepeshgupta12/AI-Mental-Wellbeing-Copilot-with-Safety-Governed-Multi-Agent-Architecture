from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.models.follow_up_event import FollowUpEvent
from mental_wellbeing_api.models.follow_up_plan import FollowUpPlan
from mental_wellbeing_api.services.scheduler_service import SchedulerService


class FollowUpService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.scheduler = SchedulerService(session)

    async def create_plan(
        self,
        *,
        user_id: str,
        source_agent: str,
        plan_type: str,
        title: str,
        description: str | None = None,
        session_id: str | None = None,
        action_plan_id: str | None = None,
        delivery_channel: str = "in_app",
        timezone_name: str | None = None,
        support_mode: str | None = None,
        support_strategy: str | None = None,
        specialist_agent: str | None = None,
        metadata: dict | None = None,
    ) -> FollowUpPlan:
        return await self.scheduler.schedule_follow_up(
            user_id=user_id,
            source_agent=source_agent,
            plan_type=plan_type,
            title=title,
            description=description,
            session_id=session_id,
            action_plan_id=action_plan_id,
            delivery_channel=delivery_channel,
            timezone_name=timezone_name,
            support_mode=support_mode,
            support_strategy=support_strategy,
            specialist_agent=specialist_agent,
            metadata=metadata,
        )

    async def get_plan(self, *, follow_up_plan_id: str) -> FollowUpPlan | None:
        return await self.session.get(FollowUpPlan, follow_up_plan_id)

    async def list_plans_for_user(self, *, user_id: str) -> list[FollowUpPlan]:
        result = await self.session.scalars(
            select(FollowUpPlan)
            .where(FollowUpPlan.user_id == user_id)
            .order_by(desc(FollowUpPlan.created_at))
        )
        return list(result.all())

    async def update_plan(
        self,
        *,
        follow_up_plan_id: str,
        status: str | None = None,
        scheduled_for=None,
        timezone_name: str | None = None,
        metadata_json: dict | None = None,
    ) -> FollowUpPlan:
        item = await self.session.get(FollowUpPlan, follow_up_plan_id)
        if item is None:
            raise ValueError("Follow up plan not found")

        if status is not None:
            item.status = status
        if scheduled_for is not None:
            item.scheduled_for = scheduled_for
        if timezone_name is not None:
            item.timezone = timezone_name
        if metadata_json is not None:
            item.metadata_json = metadata_json

        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def create_event(
        self,
        *,
        follow_up_plan_id: str,
        user_id: str,
        event_type: str,
        outcome_status: str | None = None,
        notes: str | None = None,
        event_payload_json: dict | None = None,
    ) -> FollowUpEvent:
        item = FollowUpEvent(
            follow_up_plan_id=follow_up_plan_id,
            user_id=user_id,
            event_type=event_type,
            outcome_status=outcome_status,
            notes=notes,
            event_payload_json=event_payload_json,
        )
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def list_events_for_plan(self, *, follow_up_plan_id: str) -> list[FollowUpEvent]:
        result = await self.session.scalars(
            select(FollowUpEvent)
            .where(FollowUpEvent.follow_up_plan_id == follow_up_plan_id)
            .order_by(desc(FollowUpEvent.created_at))
        )
        return list(result.all())

    async def complete_plan(
        self,
        *,
        follow_up_plan_id: str,
        notes: str | None = None,
        outcome_status: str | None = "completed",
    ) -> FollowUpPlan:
        return await self.scheduler.mark_follow_up_completed(
            follow_up_plan_id=follow_up_plan_id,
            notes=notes,
            outcome_status=outcome_status,
        )

    async def cancel_plan(
        self,
        *,
        follow_up_plan_id: str,
        notes: str | None = None,
        outcome_status: str | None = "cancelled",
    ) -> FollowUpPlan:
        return await self.scheduler.cancel_follow_up(
            follow_up_plan_id=follow_up_plan_id,
            notes=notes,
            outcome_status=outcome_status,
        )