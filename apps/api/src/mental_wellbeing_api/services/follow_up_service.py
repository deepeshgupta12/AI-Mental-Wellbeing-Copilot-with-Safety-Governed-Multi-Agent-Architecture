from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.models.follow_up_event import FollowUpEvent
from mental_wellbeing_api.models.follow_up_plan import FollowUpPlan
from mental_wellbeing_api.services.follow_up_contract_service import FollowUpContractService


class FollowUpService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.contracts = FollowUpContractService()

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
        contract = self.contracts.build_contract(
            user_id=user_id,
            source_agent=source_agent,
            plan_type=plan_type,
            title=title,
            description=description,
            delivery_channel=delivery_channel,
            timezone_name=timezone_name,
            support_mode=support_mode,
            support_strategy=support_strategy,
            specialist_agent=specialist_agent,
            metadata=metadata,
        )

        item = FollowUpPlan(
            user_id=user_id,
            session_id=session_id,
            action_plan_id=action_plan_id,
            source_agent=source_agent,
            plan_type=plan_type,
            title=contract["title"],
            description=contract["description"],
            delivery_channel=contract["delivery_channel"],
            scheduled_for=contract["scheduled_for"],
            timezone=contract["timezone"],
            cadence_json=contract["cadence_json"],
            scheduling_contract_json=contract["scheduling_contract_json"],
            metadata_json=contract["metadata_json"],
        )
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def list_plans_for_user(self, *, user_id: str) -> list[FollowUpPlan]:
        result = await self.session.scalars(
            select(FollowUpPlan)
            .where(FollowUpPlan.user_id == user_id)
            .order_by(desc(FollowUpPlan.created_at))
        )
        return list(result.all())

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