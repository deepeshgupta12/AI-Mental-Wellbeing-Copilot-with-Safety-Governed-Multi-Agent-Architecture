from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from mental_wellbeing_api.core.config import get_settings


class FollowUpContractService:
    DEFAULT_DELAY_HOURS = 24

    def build_contract(
        self,
        *,
        user_id: str,
        source_agent: str,
        plan_type: str,
        title: str,
        description: str | None,
        delivery_channel: str = "in_app",
        timezone_name: str | None = None,
        support_mode: str | None = None,
        support_strategy: str | None = None,
        specialist_agent: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        settings = get_settings()
        scheduled_for = datetime.now(UTC) + timedelta(hours=self.DEFAULT_DELAY_HOURS)

        cadence_json = {
            "kind": "one_time",
            "delay_hours": self.DEFAULT_DELAY_HOURS,
        }

        scheduling_contract_json = {
            "contract_version": "v2-followup-basic",
            "scheduler_backend": settings.scheduler_backend,
            "workflow_family": "follow_up_reminder",
            "future_ready": True,
            "status": "planned_not_enqueued",
            "user_id": user_id,
            "source_agent": source_agent,
            "plan_type": plan_type,
            "support_mode": support_mode,
            "support_strategy": support_strategy,
            "specialist_agent": specialist_agent,
        }

        return {
            "title": title,
            "description": description,
            "delivery_channel": delivery_channel,
            "scheduled_for": scheduled_for,
            "timezone": timezone_name,
            "cadence_json": cadence_json,
            "scheduling_contract_json": scheduling_contract_json,
            "metadata_json": metadata or {},
        }