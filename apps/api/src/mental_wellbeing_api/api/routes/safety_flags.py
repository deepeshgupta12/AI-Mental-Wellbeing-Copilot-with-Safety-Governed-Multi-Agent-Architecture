from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import db_session_dep
from mental_wellbeing_api.api.utils import ensure_user_exists
from mental_wellbeing_api.models.safety_flag import SafetyFlag
from mental_wellbeing_api.schemas.safety_flag import (
    SafetyDashboardCountsResponse,
    SafetyFlagCreateRequest,
    SafetyFlagResponse,
    SafetyFlagUpdateRequest,
    SafetyQueueItemResponse,
)

router = APIRouter(prefix="/safety-flags", tags=["safety-flags"])


@router.post("", response_model=SafetyFlagResponse)
async def create_safety_flag(
    payload: SafetyFlagCreateRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> SafetyFlagResponse:
    await ensure_user_exists(session, str(payload.user_id))

    item = SafetyFlag(**payload.model_dump(mode="json"))
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.get("", response_model=list[SafetyFlagResponse])
async def list_safety_flags(
    user_id: UUID,
    session: AsyncSession = Depends(db_session_dep),
) -> list[SafetyFlagResponse]:
    await ensure_user_exists(session, str(user_id))

    result = await session.scalars(
        select(SafetyFlag)
        .where(SafetyFlag.user_id == str(user_id))
        .order_by(desc(SafetyFlag.created_at))
    )
    return list(result.all())


@router.get("/queue", response_model=list[SafetyQueueItemResponse])
async def get_safety_queue(
    session: AsyncSession = Depends(db_session_dep),
) -> list[SafetyQueueItemResponse]:
    result = await session.scalars(
        select(SafetyFlag)
        .where(SafetyFlag.is_resolved.is_(False))
        .order_by(desc(SafetyFlag.created_at))
    )
    return list(result.all())


@router.get("/dashboard-counts", response_model=SafetyDashboardCountsResponse)
async def get_safety_dashboard_counts(
    session: AsyncSession = Depends(db_session_dep),
) -> SafetyDashboardCountsResponse:
    total_flags = int((await session.scalar(select(func.count(SafetyFlag.id)))) or 0)

    open_flags = int(
        (
            await session.scalar(
                select(func.count(SafetyFlag.id)).where(SafetyFlag.is_resolved.is_(False))
            )
        )
        or 0
    )

    review_needed_flags = int(
        (
            await session.scalar(
                select(func.count(SafetyFlag.id)).where(SafetyFlag.needs_review.is_(True))
            )
        )
        or 0
    )

    resolved_flags = int(
        (
            await session.scalar(
                select(func.count(SafetyFlag.id)).where(SafetyFlag.is_resolved.is_(True))
            )
        )
        or 0
    )

    high_severity_open_flags = int(
        (
            await session.scalar(
                select(func.count(SafetyFlag.id)).where(
                    SafetyFlag.severity == "high",
                    SafetyFlag.is_resolved.is_(False),
                )
            )
        )
        or 0
    )

    return SafetyDashboardCountsResponse(
        total_flags=total_flags,
        open_flags=open_flags,
        review_needed_flags=review_needed_flags,
        resolved_flags=resolved_flags,
        high_severity_open_flags=high_severity_open_flags,
    )


@router.patch("/{flag_id}", response_model=SafetyFlagResponse)
async def update_safety_flag(
    flag_id: UUID,
    payload: SafetyFlagUpdateRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> SafetyFlagResponse:
    item = await session.scalar(select(SafetyFlag).where(SafetyFlag.id == str(flag_id)))
    if not item:
        raise HTTPException(status_code=404, detail="Safety flag not found")

    now = datetime.now(timezone.utc)

    if payload.needs_review is not None:
        item.needs_review = payload.needs_review
        if payload.needs_review is False and item.reviewed_at is None:
            item.reviewed_at = now

    if payload.is_resolved is not None:
        item.is_resolved = payload.is_resolved
        if payload.is_resolved is True and item.resolved_at is None:
            item.resolved_at = now
            item.needs_review = False
            if item.reviewed_at is None:
                item.reviewed_at = now

    if payload.reviewer_note is not None:
        item.reviewer_note = payload.reviewer_note

    await session.commit()
    await session.refresh(item)
    return item