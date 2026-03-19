from __future__ import annotations

import asyncio

from mental_wellbeing_api.temporal.workflows.follow_up_workflow import (
    FollowUpReminderWorkflow,
)
from temporalio.worker import Worker

from mental_wellbeing_api.core.config import get_settings
from mental_wellbeing_api.temporal.activities.follow_up_activities import (
    dispatch_follow_up_activity,
    mark_follow_up_overdue_activity,
)
from mental_wellbeing_api.temporal.client import get_temporal_client


class TemporalWorkerRuntime:
    def __init__(self) -> None:
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        settings = get_settings()
        if not settings.temporal_enabled or not settings.temporal_enable_worker:
            return

        async def _run() -> None:
            client = await get_temporal_client()
            worker = Worker(
                client,
                task_queue=settings.temporal_task_queue,
                workflows=[FollowUpReminderWorkflow],
                activities=[
                    dispatch_follow_up_activity,
                    mark_follow_up_overdue_activity,
                ],
            )
            await worker.run()

        self._task = asyncio.create_task(_run())

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass