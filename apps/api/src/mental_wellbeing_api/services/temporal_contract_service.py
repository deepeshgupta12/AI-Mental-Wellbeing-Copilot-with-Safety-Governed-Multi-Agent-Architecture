from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from mental_wellbeing_api.core.config import get_settings


class TemporalContractService:
    def build_contract(
        self,
        *,
        user_id: str,
        follow_up_plan_id: str,
        scheduled_for: datetime | None,
        plan_type: str,
        source_agent: str,
        support_mode: str | None = None,
        support_strategy: str | None = None,
        specialist_agent: str | None = None,
    ) -> dict[str, Any]:
        settings = get_settings()
        resolved_schedule = scheduled_for or datetime.now(UTC)

        return {
            "contract_version": "v2-temporal-runtime",
            "enabled": settings.temporal_enabled,
            "namespace": settings.temporal_namespace,
            "task_queue": settings.temporal_task_queue,
            "workflow_name": "follow_up_reminder_workflow",
            "workflow_id": f"followup-{follow_up_plan_id}",
            "idempotency_key": f"followup:{follow_up_plan_id}:{resolved_schedule.isoformat()}",
            "scheduled_for": resolved_schedule.isoformat(),
            "user_id": user_id,
            "follow_up_plan_id": follow_up_plan_id,
            "plan_type": plan_type,
            "source_agent": source_agent,
            "support_mode": support_mode,
            "support_strategy": support_strategy,
            "specialist_agent": specialist_agent,
            "retry_policy": {
                "maximum_attempts": 3,
                "backoff_coefficient": 2,
            },
            "status": "ready_for_dispatch" if settings.temporal_enabled else "contract_only_not_enqueued",
        }