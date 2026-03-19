from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.core.config import get_settings
from mental_wellbeing_api.models.follow_up_event import FollowUpEvent
from mental_wellbeing_api.models.follow_up_plan import FollowUpPlan
from mental_wellbeing_api.services.follow_up_contract_service import FollowUpContractService
from mental_wellbeing_api.services.temporal_contract_service import TemporalContractService


class SchedulerService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.follow_up_contracts = FollowUpContractService()
        self.temporal_contracts = TemporalContractService()

    async def schedule_follow_up(
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
        settings = get_settings()

        contract = self.follow_up_contracts.build_contract(
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
            metadata=metadata or {},
        )

        plan = FollowUpPlan(
            user_id=user_id,
            session_id=session_id,
            action_plan_id=action_plan_id,
            source_agent=source_agent,
            plan_type=plan_type,
            title=contract["title"],
            description=contract["description"],
            status="planned",
            delivery_channel=contract["delivery_channel"],
            scheduled_for=contract["scheduled_for"],
            timezone=contract["timezone"],
            cadence_json=contract["cadence_json"],
            scheduling_contract_json=contract["scheduling_contract_json"],
            metadata_json=contract["metadata_json"],
        )
        self.session.add(plan)
        await self.session.commit()
        await self.session.refresh(plan)

        temporal_contract = self.temporal_contracts.build_contract(
            user_id=user_id,
            follow_up_plan_id=plan.id,
            scheduled_for=plan.scheduled_for,
            plan_type=plan.plan_type,
            source_agent=source_agent,
            support_mode=support_mode,
            support_strategy=support_strategy,
            specialist_agent=specialist_agent,
        )

        plan.scheduling_contract_json = {
            **(plan.scheduling_contract_json or {}),
            "scheduler_backend": settings.scheduler_backend,
            "temporal_contract": temporal_contract,
        }
        await self.session.commit()
        await self.session.refresh(plan)

        event = FollowUpEvent(
            follow_up_plan_id=plan.id,
            user_id=user_id,
            event_type="scheduled",
            outcome_status="planned",
            notes="Follow up plan scheduled via scheduler service.",
            event_payload_json={
                "scheduler_backend": settings.scheduler_backend,
                "temporal_contract": temporal_contract,
            },
        )
        self.session.add(event)
        await self.session.commit()

        return plan

    async def cancel_follow_up(
        self,
        *,
        follow_up_plan_id: str,
        notes: str | None = None,
        outcome_status: str | None = "cancelled",
    ) -> FollowUpPlan:
        plan = await self.session.get(FollowUpPlan, follow_up_plan_id)
        if plan is None:
            raise ValueError("Follow up plan not found")

        plan.status = "cancelled"
        self.session.add(
            FollowUpEvent(
                follow_up_plan_id=plan.id,
                user_id=plan.user_id,
                event_type="cancelled",
                outcome_status=outcome_status,
                notes=notes,
                event_payload_json={
                    "scheduler_backend": (plan.scheduling_contract_json or {}).get(
                        "scheduler_backend"
                    )
                },
            )
        )
        await self.session.commit()
        await self.session.refresh(plan)
        return plan

    async def mark_follow_up_completed(
        self,
        *,
        follow_up_plan_id: str,
        notes: str | None = None,
        outcome_status: str | None = "completed",
    ) -> FollowUpPlan:
        plan = await self.session.get(FollowUpPlan, follow_up_plan_id)
        if plan is None:
            raise ValueError("Follow up plan not found")

        plan.status = "completed"
        self.session.add(
            FollowUpEvent(
                follow_up_plan_id=plan.id,
                user_id=plan.user_id,
                event_type="completed",
                outcome_status=outcome_status,
                notes=notes,
                event_payload_json={
                    "scheduler_backend": (plan.scheduling_contract_json or {}).get(
                        "scheduler_backend"
                    )
                },
            )
        )
        await self.session.commit()
        await self.session.refresh(plan)
        return plan