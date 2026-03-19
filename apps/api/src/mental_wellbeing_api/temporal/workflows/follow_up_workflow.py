from __future__ import annotations

from datetime import UTC, datetime

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from mental_wellbeing_api.temporal.activities.follow_up_activities import (
        dispatch_follow_up_activity,
    )


@workflow.defn
class FollowUpReminderWorkflow:
    @workflow.run
    async def run(self, payload: dict) -> dict:
        scheduled_for_raw = payload.get("scheduled_for")
        if isinstance(scheduled_for_raw, str):
            try:
                scheduled_for = datetime.fromisoformat(scheduled_for_raw.replace("Z", "+00:00"))
            except Exception:
                scheduled_for = datetime.now(UTC)
        else:
            scheduled_for = datetime.now(UTC)

        now = datetime.now(UTC)
        delay_seconds = max((scheduled_for - now).total_seconds(), 0.0)
        if delay_seconds > 0:
            await workflow.sleep(delay_seconds)

        result = await workflow.execute_activity(
            dispatch_follow_up_activity,
            payload,
            start_to_close_timeout=workflow.timedelta(minutes=2),
        )
        return result