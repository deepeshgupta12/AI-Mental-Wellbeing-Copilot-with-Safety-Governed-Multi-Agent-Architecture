from __future__ import annotations

from datetime import UTC, datetime

from temporalio import activity


@activity.defn
async def dispatch_follow_up_activity(payload: dict) -> dict:
    return {
        "status": "dispatched",
        "executed_at": datetime.now(UTC).isoformat(),
        "payload": payload,
    }


@activity.defn
async def mark_follow_up_overdue_activity(payload: dict) -> dict:
    return {
        "status": "overdue_marked",
        "executed_at": datetime.now(UTC).isoformat(),
        "payload": payload,
    }