from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta
from statistics import mean
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mental_wellbeing_api.models.audit_log import AuditLog
from mental_wellbeing_api.models.auth_session import AuthSession
from mental_wellbeing_api.models.enterprise_setting import EnterpriseSetting
from mental_wellbeing_api.models.follow_up_event import FollowUpEvent
from mental_wellbeing_api.models.follow_up_plan import FollowUpPlan
from mental_wellbeing_api.models.intervention_log import InterventionLog
from mental_wellbeing_api.models.organization import Organization, OrganizationMembership, Role
from mental_wellbeing_api.models.safety_event import SafetyEvent
from mental_wellbeing_api.models.safety_review import SafetyReview
from mental_wellbeing_api.models.stored_artifact import StoredArtifact
from mental_wellbeing_api.models.user import User
from mental_wellbeing_api.services.enterprise_settings_service import EnterpriseSettingsService
from mental_wellbeing_api.services.infrastructure_governance_service import (
    InfrastructureGovernanceService,
)


class EnterpriseAdminAnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.enterprise_settings = EnterpriseSettingsService(session)
        self.infrastructure = InfrastructureGovernanceService(session)

    async def _organization_setting_updated_at_map(self) -> dict[str, datetime]:
        rows = (
            await self.session.execute(
                select(EnterpriseSetting.scope_id, EnterpriseSetting.updated_at)
                .where(EnterpriseSetting.scope_type == "organization")
                .order_by(desc(EnterpriseSetting.updated_at))
            )
        ).all()

        mapping: dict[str, datetime] = {}
        for scope_id, updated_at in rows:
            if scope_id and updated_at and scope_id not in mapping:
                mapping[str(scope_id)] = updated_at
        return mapping

    async def _organization_session_snapshot_map(self) -> dict[str, dict[str, Any]]:
        now = datetime.now(UTC)
        rows = (
            await self.session.execute(
                select(
                    AuthSession.organization_id,
                    func.count(AuthSession.id).label("session_count"),
                    func.max(AuthSession.last_seen_at).label("latest_seen_at"),
                )
                .where(
                    AuthSession.organization_id.is_not(None),
                    AuthSession.session_status == "active",
                    AuthSession.revoked_at.is_(None),
                    AuthSession.expires_at > now,
                )
                .group_by(AuthSession.organization_id)
            )
        ).all()

        payload: dict[str, dict[str, Any]] = {}
        for row in rows:
            if row.organization_id:
                payload[str(row.organization_id)] = {
                    "active_session_count": int(row.session_count or 0),
                    "latest_session_at": row.latest_seen_at,
                }
        return payload

    async def _organization_members_map(self) -> dict[str, list[OrganizationMembership]]:
        rows = list(
            (
                await self.session.scalars(
                    select(OrganizationMembership)
                    .options(
                        selectinload(OrganizationMembership.role).selectinload(Role.permissions),
                        selectinload(OrganizationMembership.organization),
                    )
                    .order_by(desc(OrganizationMembership.created_at))
                )
            ).all()
        )
        payload: dict[str, list[OrganizationMembership]] = {}
        for row in rows:
            payload.setdefault(str(row.organization_id), []).append(row)
        return payload

    async def _member_user_ids_for_org(self, organization_id: str) -> list[str]:
        rows = (
            await self.session.execute(
                select(OrganizationMembership.user_id)
                .where(OrganizationMembership.organization_id == organization_id)
                .distinct()
            )
        ).all()
        return [str(row[0]) for row in rows if row[0]]

    async def list_organizations(self, *, limit: int = 100) -> list[dict[str, Any]]:
        setting_updated_map = await self._organization_setting_updated_at_map()
        session_snapshot_map = await self._organization_session_snapshot_map()

        rows = (
            await self.session.execute(
                select(
                    Organization.id,
                    Organization.name,
                    Organization.slug,
                    Organization.status,
                    Organization.is_active,
                    Organization.created_at,
                    Organization.updated_at,
                    func.count(OrganizationMembership.id).label("membership_count"),
                )
                .outerjoin(
                    OrganizationMembership,
                    OrganizationMembership.organization_id == Organization.id,
                )
                .group_by(
                    Organization.id,
                    Organization.name,
                    Organization.slug,
                    Organization.status,
                    Organization.is_active,
                    Organization.created_at,
                    Organization.updated_at,
                )
                .order_by(desc("membership_count"), Organization.created_at.desc())
                .limit(limit)
            )
        ).all()

        payload: list[dict[str, Any]] = []
        for row in rows:
            session_snapshot = session_snapshot_map.get(str(row.id), {})
            payload.append(
                {
                    "id": str(row.id),
                    "name": row.name,
                    "slug": row.slug,
                    "status": row.status,
                    "is_active": bool(row.is_active),
                    "membership_count": int(row.membership_count or 0),
                    "active_session_count": int(
                        session_snapshot.get("active_session_count", 0)
                    ),
                    "latest_session_at": session_snapshot.get("latest_session_at"),
                    "latest_setting_updated_at": setting_updated_map.get(str(row.id)),
                    "created_at": row.created_at,
                    "updated_at": row.updated_at,
                }
            )

        return payload

    async def _recent_sessions_for_org(
        self,
        organization_id: str,
        *,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        rows = list(
            (
                await self.session.scalars(
                    select(AuthSession)
                    .where(AuthSession.organization_id == organization_id)
                    .order_by(desc(AuthSession.created_at))
                    .limit(limit)
                )
            ).all()
        )
        return [
            {
                "id": item.id,
                "user_id": item.user_id,
                "auth_provider": item.auth_provider,
                "session_status": item.session_status,
                "issued_at": item.issued_at,
                "expires_at": item.expires_at,
                "revoked_at": item.revoked_at,
                "last_seen_at": item.last_seen_at,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
            }
            for item in rows
        ]

    async def _membership_breakdown_for_org(self, organization_id: str) -> dict[str, int]:
        rows = (
            await self.session.execute(
                select(Role.name, func.count(OrganizationMembership.id).label("count"))
                .join(OrganizationMembership, OrganizationMembership.role_id == Role.id)
                .where(OrganizationMembership.organization_id == organization_id)
                .group_by(Role.name)
                .order_by(desc("count"))
            )
        ).all()
        return {str(row.name): int(row.count or 0) for row in rows if row.name}

    async def _member_summaries_for_org(
        self,
        organization_id: str,
        *,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        rows = list(
            (
                await self.session.scalars(
                    select(OrganizationMembership)
                    .options(
                        selectinload(OrganizationMembership.role),
                        selectinload(OrganizationMembership.organization),
                    )
                    .where(OrganizationMembership.organization_id == organization_id)
                    .order_by(desc(OrganizationMembership.updated_at))
                    .limit(limit)
                )
            ).all()
        )

        users = (
            await self.session.execute(
                select(User)
                .options(selectinload(User.profile))
                .where(User.id.in_([row.user_id for row in rows]))
            )
        ).scalars().all() if rows else []
        users_by_id = {str(item.id): item for item in users}

        payload: list[dict[str, Any]] = []
        for item in rows:
            user = users_by_id.get(str(item.user_id))
            payload.append(
                {
                    "membership_id": item.id,
                    "user_id": item.user_id,
                    "email": user.email if user else None,
                    "display_name": user.profile.display_name if user and user.profile else None,
                    "role_name": item.role.name if item.role else None,
                    "status": item.status,
                    "is_default": item.is_default,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at,
                }
            )
        return payload

    async def _activity_trend_points(
        self,
        *,
        user_ids: list[str],
        days: int,
    ) -> list[dict[str, Any]]:
        if not user_ids:
            return []

        since = datetime.now(UTC) - timedelta(days=days)
        safety_rows = list(
            (
                await self.session.scalars(
                    select(SafetyEvent)
                    .where(
                        SafetyEvent.user_id.in_(user_ids),
                        SafetyEvent.created_at >= since,
                    )
                    .order_by(SafetyEvent.created_at.asc())
                )
            ).all()
        )
        intervention_rows = list(
            (
                await self.session.scalars(
                    select(InterventionLog)
                    .where(
                        InterventionLog.user_id.in_(user_ids),
                        InterventionLog.created_at >= since,
                    )
                    .order_by(InterventionLog.created_at.asc())
                )
            ).all()
        )
        follow_up_rows = list(
            (
                await self.session.scalars(
                    select(FollowUpEvent)
                    .where(
                        FollowUpEvent.user_id.in_(user_ids),
                        FollowUpEvent.created_at >= since,
                    )
                    .order_by(FollowUpEvent.created_at.asc())
                )
            ).all()
        )

        buckets: dict[str, dict[str, Any]] = {}
        for offset in range(days):
            day = (since + timedelta(days=offset)).date()
            buckets[day.isoformat()] = {
                "date": day.isoformat(),
                "safety_events": 0,
                "interventions": 0,
                "follow_up_events": 0,
            }

        for row in safety_rows:
            day_key = row.created_at.date().isoformat()
            if day_key in buckets:
                buckets[day_key]["safety_events"] += 1
        for row in intervention_rows:
            day_key = row.created_at.date().isoformat()
            if day_key in buckets:
                buckets[day_key]["interventions"] += 1
        for row in follow_up_rows:
            day_key = row.created_at.date().isoformat()
            if day_key in buckets:
                buckets[day_key]["follow_up_events"] += 1

        return list(buckets.values())

    async def _safety_rollup(
        self,
        *,
        user_ids: list[str],
        days: int,
    ) -> dict[str, Any]:
        if not user_ids:
            return {
                "total_events": 0,
                "window_days": days,
                "high_risk_events": 0,
                "critical_events": 0,
                "queue_status_breakdown": {},
                "risk_level_breakdown": {},
                "escalation_status_breakdown": {},
                "review_completion_rate_pct": 0.0,
                "avg_queue_age_hours": 0.0,
            }

        since = datetime.now(UTC) - timedelta(days=days)
        rows = list(
            (
                await self.session.scalars(
                    select(SafetyEvent)
                    .where(
                        SafetyEvent.user_id.in_(user_ids),
                        SafetyEvent.created_at >= since,
                    )
                    .order_by(desc(SafetyEvent.created_at))
                )
            ).all()
        )
        queue_counter = Counter()
        risk_counter = Counter()
        escalation_counter = Counter()
        queue_ages: list[float] = []

        now = datetime.now(UTC)
        high_risk_events = 0
        critical_events = 0
        resolved_events = 0

        for row in rows:
            queue_counter[str(row.queue_status or "unknown")] += 1
            risk_counter[str(row.risk_level or "unknown")] += 1
            escalation_counter[str(row.escalation_status or "unknown")] += 1
            if row.risk_level == "high":
                high_risk_events += 1
            if row.severity == "critical":
                critical_events += 1
            if row.queue_status == "resolved":
                resolved_events += 1
            if row.queue_status in {"queued", "in_review"}:
                queue_ages.append((now - row.created_at).total_seconds() / 3600)

        completion_rate = round((resolved_events / len(rows)) * 100, 2) if rows else 0.0
        avg_queue_age_hours = round(mean(queue_ages), 2) if queue_ages else 0.0

        return {
            "total_events": len(rows),
            "window_days": days,
            "high_risk_events": high_risk_events,
            "critical_events": critical_events,
            "queue_status_breakdown": dict(queue_counter),
            "risk_level_breakdown": dict(risk_counter),
            "escalation_status_breakdown": dict(escalation_counter),
            "review_completion_rate_pct": completion_rate,
            "avg_queue_age_hours": avg_queue_age_hours,
        }

    async def _intervention_rollup(
        self,
        *,
        user_ids: list[str],
        days: int,
    ) -> dict[str, Any]:
        if not user_ids:
            return {
                "total_logs": 0,
                "window_days": days,
                "avg_effectiveness_rating": None,
                "intervention_type_breakdown": {},
                "outcome_status_breakdown": {},
            }

        since = datetime.now(UTC) - timedelta(days=days)
        rows = list(
            (
                await self.session.scalars(
                    select(InterventionLog)
                    .where(
                        InterventionLog.user_id.in_(user_ids),
                        InterventionLog.created_at >= since,
                    )
                    .order_by(desc(InterventionLog.created_at))
                )
            ).all()
        )
        type_counter = Counter()
        outcome_counter = Counter()
        ratings: list[float] = []
        for row in rows:
            type_counter[str(row.intervention_type or "unknown")] += 1
            if row.outcome_status:
                outcome_counter[str(row.outcome_status)] += 1
            if row.effectiveness_rating is not None:
                ratings.append(float(row.effectiveness_rating))

        return {
            "total_logs": len(rows),
            "window_days": days,
            "avg_effectiveness_rating": round(mean(ratings), 2) if ratings else None,
            "intervention_type_breakdown": dict(type_counter),
            "outcome_status_breakdown": dict(outcome_counter),
        }

    async def _reviewer_productivity(
        self,
        *,
        user_ids: list[str],
        days: int,
    ) -> list[dict[str, Any]]:
        if not user_ids:
            return []

        since = datetime.now(UTC) - timedelta(days=days)
        rows = list(
            (
                await self.session.scalars(
                    select(SafetyReview)
                    .where(
                        SafetyReview.user_id.in_(user_ids),
                        SafetyReview.created_at >= since,
                    )
                    .order_by(desc(SafetyReview.created_at))
                )
            ).all()
        )
        if not rows:
            return []

        event_ids = [row.safety_event_id for row in rows if row.safety_event_id]
        events = list(
            (
                await self.session.scalars(
                    select(SafetyEvent).where(SafetyEvent.id.in_(event_ids))
                )
            ).all()
        ) if event_ids else []
        events_by_id = {str(item.id): item for item in events}

        reviewers: dict[str, dict[str, Any]] = {}
        for row in rows:
            reviewer_id = row.reviewer_id or "unassigned"
            bucket = reviewers.setdefault(
                reviewer_id,
                {
                    "reviewer_id": reviewer_id,
                    "review_count": 0,
                    "resolved_count": 0,
                    "escalated_count": 0,
                    "avg_review_lag_hours": [],
                    "avg_resolution_hours": [],
                    "latest_reviewed_at": row.reviewed_at or row.created_at,
                },
            )
            bucket["review_count"] += 1
            if row.review_status in {"resolved", "closed", "completed"}:
                bucket["resolved_count"] += 1
            if row.escalation_required:
                bucket["escalated_count"] += 1

            event = events_by_id.get(str(row.safety_event_id))
            if event is not None and row.reviewed_at is not None:
                bucket["avg_review_lag_hours"].append(
                    max((row.reviewed_at - event.detected_at).total_seconds() / 3600, 0.0)
                )
            if row.reviewed_at is not None and row.resolved_at is not None:
                bucket["avg_resolution_hours"].append(
                    max((row.resolved_at - row.reviewed_at).total_seconds() / 3600, 0.0)
                )
            if row.reviewed_at and row.reviewed_at > bucket["latest_reviewed_at"]:
                bucket["latest_reviewed_at"] = row.reviewed_at

        payload: list[dict[str, Any]] = []
        for item in reviewers.values():
            review_count = int(item["review_count"])
            resolved_count = int(item["resolved_count"])
            payload.append(
                {
                    "reviewer_id": item["reviewer_id"],
                    "review_count": review_count,
                    "resolved_count": resolved_count,
                    "escalated_count": int(item["escalated_count"]),
                    "completion_rate_pct": round((resolved_count / review_count) * 100, 2)
                    if review_count
                    else 0.0,
                    "avg_review_lag_hours": round(mean(item["avg_review_lag_hours"]), 2)
                    if item["avg_review_lag_hours"]
                    else None,
                    "avg_resolution_hours": round(mean(item["avg_resolution_hours"]), 2)
                    if item["avg_resolution_hours"]
                    else None,
                    "latest_reviewed_at": item["latest_reviewed_at"],
                }
            )
        payload.sort(
            key=lambda item: (
                -int(item["review_count"]),
                item["reviewer_id"],
            )
        )
        return payload

    async def _operational_kpis(
        self,
        *,
        organization_id: str,
        user_ids: list[str],
        days: int,
    ) -> dict[str, Any]:
        since = datetime.now(UTC) - timedelta(days=days)
        active_session_count = int(
            (
                await self.session.scalar(
                    select(func.count(AuthSession.id)).where(
                        AuthSession.organization_id == organization_id,
                        AuthSession.session_status == "active",
                        AuthSession.revoked_at.is_(None),
                        AuthSession.expires_at > datetime.now(UTC),
                    )
                )
            )
            or 0
        )
        total_sessions_window = int(
            (
                await self.session.scalar(
                    select(func.count(AuthSession.id)).where(
                        AuthSession.organization_id == organization_id,
                        AuthSession.created_at >= since,
                    )
                )
            )
            or 0
        )
        follow_up_plan_count = int(
            (
                await self.session.scalar(
                    select(func.count(FollowUpPlan.id)).where(
                        FollowUpPlan.user_id.in_(user_ids) if user_ids else False,
                        FollowUpPlan.created_at >= since,
                    )
                )
            )
            or 0
        ) if user_ids else 0
        follow_up_event_count = int(
            (
                await self.session.scalar(
                    select(func.count(FollowUpEvent.id)).where(
                        FollowUpEvent.user_id.in_(user_ids) if user_ids else False,
                        FollowUpEvent.created_at >= since,
                    )
                )
            )
            or 0
        ) if user_ids else 0

        safety_rollup = await self._safety_rollup(user_ids=user_ids, days=days)
        intervention_rollup = await self._intervention_rollup(user_ids=user_ids, days=days)
        reviewer_productivity = await self._reviewer_productivity(user_ids=user_ids, days=days)

        return {
            "window_days": days,
            "member_count": len(user_ids),
            "active_session_count": active_session_count,
            "session_count_window": total_sessions_window,
            "safety_event_count_window": safety_rollup["total_events"],
            "high_risk_safety_event_count_window": safety_rollup["high_risk_events"],
            "intervention_count_window": intervention_rollup["total_logs"],
            "follow_up_plan_count_window": follow_up_plan_count,
            "follow_up_event_count_window": follow_up_event_count,
            "review_completion_rate_pct": safety_rollup["review_completion_rate_pct"],
            "avg_queue_age_hours": safety_rollup["avg_queue_age_hours"],
            "reviewer_count": len(reviewer_productivity),
        }

    async def build_overview(
        self,
        *,
        organization_id: str | None = None,
        days: int = 30,
    ) -> dict[str, Any]:
        now = datetime.now(UTC)

        total_organizations = int(
            (await self.session.scalar(select(func.count(Organization.id)))) or 0
        )
        active_organizations = int(
            (
                await self.session.scalar(
                    select(func.count(Organization.id)).where(
                        Organization.is_active.is_(True)
                    )
                )
            )
            or 0
        )

        total_memberships = int(
            (await self.session.scalar(select(func.count(OrganizationMembership.id)))) or 0
        )

        membership_rows = (
            await self.session.execute(
                select(Role.name, func.count(OrganizationMembership.id).label("count"))
                .join(OrganizationMembership, OrganizationMembership.role_id == Role.id)
                .group_by(Role.name)
                .order_by(desc("count"))
            )
        ).all()
        membership_breakdown_by_role = {
            str(row.name): int(row.count or 0)
            for row in membership_rows
            if row.name
        }

        total_auth_sessions = int(
            (await self.session.scalar(select(func.count(AuthSession.id)))) or 0
        )
        active_auth_sessions = int(
            (
                await self.session.scalar(
                    select(func.count(AuthSession.id)).where(
                        AuthSession.session_status == "active",
                        AuthSession.revoked_at.is_(None),
                        AuthSession.expires_at > now,
                    )
                )
            )
            or 0
        )
        expired_auth_sessions = int(
            (
                await self.session.scalar(
                    select(func.count(AuthSession.id)).where(
                        AuthSession.expires_at <= now,
                    )
                )
            )
            or 0
        )
        revoked_auth_sessions = int(
            (
                await self.session.scalar(
                    select(func.count(AuthSession.id)).where(
                        (AuthSession.revoked_at.is_not(None))
                        | (AuthSession.session_status == "revoked")
                    )
                )
            )
            or 0
        )

        organization_settings_count = int(
            (
                await self.session.scalar(
                    select(func.count(EnterpriseSetting.id)).where(
                        EnterpriseSetting.scope_type == "organization",
                        EnterpriseSetting.is_active.is_(True),
                    )
                )
            )
            or 0
        )
        deployment_settings_count = int(
            (
                await self.session.scalar(
                    select(func.count(EnterpriseSetting.id)).where(
                        EnterpriseSetting.scope_type == "deployment",
                        EnterpriseSetting.is_active.is_(True),
                    )
                )
            )
            or 0
        )

        stored_artifact_count = int(
            (await self.session.scalar(select(func.count(StoredArtifact.id)))) or 0
        )
        artifact_rows = (
            await self.session.execute(
                select(
                    StoredArtifact.storage_provider,
                    func.count(StoredArtifact.id).label("count"),
                )
                .group_by(StoredArtifact.storage_provider)
                .order_by(desc("count"))
            )
        ).all()
        artifact_breakdown_by_provider = {
            str(row.storage_provider): int(row.count or 0)
            for row in artifact_rows
            if row.storage_provider
        }

        immutable_audit_log_count = int(
            (
                await self.session.scalar(
                    select(func.count(AuditLog.id)).where(
                        AuditLog.is_immutable.is_(True)
                    )
                )
            )
            or 0
        )

        total_safety_events = int(
            (await self.session.scalar(select(func.count(SafetyEvent.id)))) or 0
        )
        high_risk_safety_events = int(
            (
                await self.session.scalar(
                    select(func.count(SafetyEvent.id)).where(
                        SafetyEvent.risk_level == "high"
                    )
                )
            )
            or 0
        )

        organizations = await self.list_organizations(limit=25)

        scoped_organization: dict[str, Any] | None = None
        scoped_operational_kpis: dict[str, Any] | None = None
        scoped_safety_rollup: dict[str, Any] | None = None
        scoped_intervention_rollup: dict[str, Any] | None = None
        scoped_reviewer_productivity: list[dict[str, Any]] = []
        scoped_activity_trends: list[dict[str, Any]] = []

        if organization_id:
            scoped_organization = next(
                (item for item in organizations if item["id"] == organization_id),
                None,
            )
            if scoped_organization is None:
                organization = await self.session.get(Organization, organization_id)
                if organization is None:
                    raise ValueError("Organization not found")
                scoped_organization = {
                    "id": str(organization.id),
                    "name": organization.name,
                    "slug": organization.slug,
                    "status": organization.status,
                    "is_active": bool(organization.is_active),
                    "membership_count": 0,
                    "active_session_count": 0,
                    "latest_session_at": None,
                    "latest_setting_updated_at": None,
                    "created_at": organization.created_at,
                    "updated_at": organization.updated_at,
                }
            user_ids = await self._member_user_ids_for_org(organization_id)
            scoped_operational_kpis = await self._operational_kpis(
                organization_id=organization_id,
                user_ids=user_ids,
                days=days,
            )
            scoped_safety_rollup = await self._safety_rollup(user_ids=user_ids, days=days)
            scoped_intervention_rollup = await self._intervention_rollup(
                user_ids=user_ids,
                days=days,
            )
            scoped_reviewer_productivity = await self._reviewer_productivity(
                user_ids=user_ids,
                days=days,
            )
            scoped_activity_trends = await self._activity_trend_points(
                user_ids=user_ids,
                days=min(days, 30),
            )

        return {
            "scope_organization_id": organization_id,
            "window_days": days,
            "total_organizations": total_organizations,
            "active_organizations": active_organizations,
            "total_memberships": total_memberships,
            "membership_breakdown_by_role": membership_breakdown_by_role,
            "total_auth_sessions": total_auth_sessions,
            "active_auth_sessions": active_auth_sessions,
            "expired_auth_sessions": expired_auth_sessions,
            "revoked_auth_sessions": revoked_auth_sessions,
            "organization_settings_count": organization_settings_count,
            "deployment_settings_count": deployment_settings_count,
            "stored_artifact_count": stored_artifact_count,
            "artifact_breakdown_by_provider": artifact_breakdown_by_provider,
            "immutable_audit_log_count": immutable_audit_log_count,
            "total_safety_events": total_safety_events,
            "high_risk_safety_events": high_risk_safety_events,
            "organizations": organizations,
            "scoped_organization": scoped_organization,
            "scoped_operational_kpis": scoped_operational_kpis,
            "scoped_safety_rollup": scoped_safety_rollup,
            "scoped_intervention_rollup": scoped_intervention_rollup,
            "scoped_reviewer_productivity": scoped_reviewer_productivity,
            "scoped_activity_trends": scoped_activity_trends,
        }

    async def _recent_artifacts_for_org(
        self,
        *,
        user_ids: list[str],
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        if not user_ids:
            return []

        safety_events = list(
            (
                await self.session.scalars(
                    select(SafetyEvent.id)
                    .where(SafetyEvent.user_id.in_(user_ids))
                    .order_by(desc(SafetyEvent.created_at))
                    .limit(100)
                )
            ).all()
        )
        safety_reviews = list(
            (
                await self.session.scalars(
                    select(SafetyReview.id)
                    .where(SafetyReview.user_id.in_(user_ids))
                    .order_by(desc(SafetyReview.created_at))
                    .limit(100)
                )
            ).all()
        )
        audit_logs = list(
            (
                await self.session.scalars(
                    select(AuditLog.id)
                    .where(AuditLog.user_id.in_(user_ids))
                    .order_by(desc(AuditLog.created_at))
                    .limit(100)
                )
            ).all()
        )

        conditions = []
        if safety_events:
            conditions.append(
                (StoredArtifact.scope_type == "safety_event")
                & (StoredArtifact.scope_id.in_([str(item) for item in safety_events]))
            )
        if safety_reviews:
            conditions.append(
                (StoredArtifact.scope_type == "safety_review")
                & (StoredArtifact.scope_id.in_([str(item) for item in safety_reviews]))
            )
        if audit_logs:
            conditions.append(
                (StoredArtifact.scope_type == "audit_log")
                & (StoredArtifact.scope_id.in_([str(item) for item in audit_logs]))
            )
        if not conditions:
            return []

        stmt = select(StoredArtifact).order_by(desc(StoredArtifact.created_at)).limit(limit)
        condition = conditions[0]
        for extra in conditions[1:]:
            condition = condition | extra
        rows = list(((await self.session.scalars(stmt.where(condition))).all()))

        return [
            {
                "id": item.id,
                "scope_type": item.scope_type,
                "scope_id": item.scope_id,
                "artifact_kind": item.artifact_kind,
                "file_name": item.file_name,
                "storage_provider": item.storage_provider,
                "storage_uri": item.storage_uri,
                "local_path": item.local_path,
                "byte_size": item.byte_size,
                "checksum_sha256": item.checksum_sha256,
                "created_at": item.created_at,
            }
            for item in rows
        ]

    async def get_organization_detail(self, *, organization_id: str, days: int = 30) -> dict[str, Any]:
        organization = await self.session.get(Organization, organization_id)
        if organization is None:
            raise ValueError("Organization not found")

        organizations = await self.list_organizations(limit=500)
        organization_summary = next(
            (item for item in organizations if item["id"] == organization_id),
            None,
        )
        if organization_summary is None:
            organization_summary = {
                "id": str(organization.id),
                "name": organization.name,
                "slug": organization.slug,
                "status": organization.status,
                "is_active": organization.is_active,
                "membership_count": 0,
                "active_session_count": 0,
                "latest_session_at": None,
                "latest_setting_updated_at": None,
                "created_at": organization.created_at,
                "updated_at": organization.updated_at,
            }

        user_ids = await self._member_user_ids_for_org(organization_id)
        membership_breakdown_by_role = await self._membership_breakdown_for_org(organization_id)
        member_summaries = await self._member_summaries_for_org(organization_id)
        recent_auth_sessions = await self._recent_sessions_for_org(organization_id)

        organization_setting = await self.enterprise_settings.get_organization_settings(
            organization_id
        )
        resolved_settings = await self.enterprise_settings.resolve_settings(
            organization_id=organization_id
        )
        infrastructure_summary = await self.infrastructure.build_runtime_summary(
            organization_id=organization_id
        )

        safety_rollup = await self._safety_rollup(user_ids=user_ids, days=days)
        intervention_rollup = await self._intervention_rollup(user_ids=user_ids, days=days)
        reviewer_productivity = await self._reviewer_productivity(user_ids=user_ids, days=days)
        operational_kpis = await self._operational_kpis(
            organization_id=organization_id,
            user_ids=user_ids,
            days=days,
        )
        activity_trends = await self._activity_trend_points(
            user_ids=user_ids,
            days=min(days, 30),
        )
        recent_artifacts = await self._recent_artifacts_for_org(user_ids=user_ids)

        return {
            "organization": organization_summary,
            "window_days": days,
            "membership_breakdown_by_role": membership_breakdown_by_role,
            "member_summaries": member_summaries,
            "recent_auth_sessions": recent_auth_sessions,
            "safety_rollup": safety_rollup,
            "intervention_rollup": intervention_rollup,
            "reviewer_productivity": reviewer_productivity,
            "operational_kpis": operational_kpis,
            "activity_trends": activity_trends,
            "organization_settings": organization_setting.payload_json,
            "effective_settings": resolved_settings.get("effective_settings", {}),
            "infrastructure_summary": infrastructure_summary,
            "recent_artifacts": recent_artifacts,
        }
