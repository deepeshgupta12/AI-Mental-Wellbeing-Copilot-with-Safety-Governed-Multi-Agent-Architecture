from __future__ import annotations

from collections import Counter
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.models.check_in import CheckIn
from mental_wellbeing_api.models.conversation import ConversationSession
from mental_wellbeing_api.models.intervention_log import InterventionLog
from mental_wellbeing_api.models.journal_entry import JournalEntry
from mental_wellbeing_api.models.journal_theme import JournalTheme
from mental_wellbeing_api.models.trend_snapshot import TrendSnapshot
from mental_wellbeing_api.models.trigger_cluster import TriggerCluster


class TrendIntelligenceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def build_runtime_trend_bundle(self, *, user_id: str) -> dict[str, Any]:
        trend_series = await self.build_trend_series(user_id=user_id)
        latest_snapshot = await self.session.scalar(
            select(TrendSnapshot)
            .where(TrendSnapshot.user_id == user_id)
            .order_by(desc(TrendSnapshot.created_at))
            .limit(1)
        )

        latest_weekly_snapshot = await self.session.scalar(
            select(TrendSnapshot)
            .where(
                TrendSnapshot.user_id == user_id,
                TrendSnapshot.window_type == "weekly_reflection",
            )
            .order_by(desc(TrendSnapshot.created_at))
            .limit(1)
        )

        recurring_trigger_rows = list(
            (
                await self.session.scalars(
                    select(TriggerCluster)
                    .where(TriggerCluster.user_id == user_id)
                    .order_by(desc(TriggerCluster.frequency), desc(TriggerCluster.updated_at))
                    .limit(5)
                )
            ).all()
        )

        intervention_rows = list(
            (
                await self.session.scalars(
                    select(InterventionLog)
                    .where(InterventionLog.user_id == user_id)
                    .order_by(desc(InterventionLog.created_at))
                    .limit(10)
                )
            ).all()
        )

        journal_theme_rows = (
            await self.session.execute(
                select(JournalTheme.theme_name, func.count(JournalTheme.id).label("theme_count"))
                .where(JournalTheme.user_id == user_id)
                .group_by(JournalTheme.theme_name)
                .order_by(desc("theme_count"), JournalTheme.theme_name.asc())
                .limit(5)
            )
        ).all()

        counts_row = (
            await self.session.execute(
                select(
                    func.count(CheckIn.id).label("check_in_count"),
                    func.avg(CheckIn.mood_score).label("avg_mood_score"),
                    func.avg(CheckIn.stress_score).label("avg_stress_score"),
                    func.avg(CheckIn.energy_score).label("avg_energy_score"),
                    func.avg(CheckIn.sleep_hours).label("avg_sleep_hours"),
                ).where(CheckIn.user_id == user_id)
            )
        ).one()

        journal_count = int(
            (
                await self.session.execute(
                    select(func.count(JournalEntry.id)).where(JournalEntry.user_id == user_id)
                )
            ).scalar()
            or 0
        )

        session_count = int(
            (
                await self.session.execute(
                    select(func.count(ConversationSession.id)).where(
                        ConversationSession.user_id == user_id
                    )
                )
            ).scalar()
            or 0
        )

        recurring_patterns = [
            item.cluster_name
            for item in recurring_trigger_rows
            if item.cluster_name
        ][:3]

        top_themes = [row.theme_name for row in journal_theme_rows][:3]

        support_progress_summary = self._build_support_progress_summary(
            journal_count=journal_count,
            session_count=session_count,
            top_themes=top_themes,
            recurring_patterns=recurring_patterns,
        )

        progress_summary = self._build_progress_summary(
            latest_snapshot=latest_snapshot.summary_json if latest_snapshot else None,
            latest_weekly_snapshot=(
                latest_weekly_snapshot.summary_json if latest_weekly_snapshot else None
            ),
            top_themes=top_themes,
            recurring_patterns=recurring_patterns,
        )

        intervention_effectiveness = self._build_intervention_effectiveness(intervention_rows)

        trend_visualization = {
            "total_check_ins": int(counts_row.check_in_count or 0),
            "avg_mood_score": self._rounded(counts_row.avg_mood_score),
            "avg_stress_score": self._rounded(counts_row.avg_stress_score),
            "avg_energy_score": self._rounded(counts_row.avg_energy_score),
            "avg_sleep_hours": self._rounded(counts_row.avg_sleep_hours),
            "total_journal_entries": journal_count,
            "total_conversation_sessions": session_count,
        }

        return {
            "progress_summary": progress_summary,
            "support_progress_summary": support_progress_summary,
            "recurring_patterns": recurring_patterns,
            "intervention_effectiveness": intervention_effectiveness,
            "trend_visualization": trend_visualization,
            "trend_series": trend_series,
            "latest_snapshot_window_type": latest_snapshot.window_type if latest_snapshot else None,
            "latest_snapshot_created_at": latest_snapshot.created_at if latest_snapshot else None,
        }

    async def build_admin_trend_overview(self) -> dict[str, Any]:
        recent_snapshots = list(
            (
                await self.session.scalars(
                    select(TrendSnapshot)
                    .order_by(desc(TrendSnapshot.created_at))
                    .limit(50)
                )
            ).all()
        )

        recent_triggers = list(
            (
                await self.session.scalars(
                    select(TriggerCluster)
                    .order_by(desc(TriggerCluster.frequency), desc(TriggerCluster.updated_at))
                    .limit(20)
                )
            ).all()
        )

        recent_interventions = list(
            (
                await self.session.scalars(
                    select(InterventionLog)
                    .order_by(desc(InterventionLog.created_at))
                    .limit(50)
                )
            ).all()
        )

        snapshot_user_count = int(
            len({item.user_id for item in recent_snapshots if item.user_id})
        )
        weekly_snapshot_count = sum(
            1 for item in recent_snapshots if item.window_type == "weekly_reflection"
        )

        trigger_counter = Counter(item.cluster_name for item in recent_triggers if item.cluster_name)
        top_recurring_patterns = [name for name, _ in trigger_counter.most_common(5)]

        recent_support_progress_summaries: list[str] = []
        for item in recent_snapshots:
            if isinstance(item.summary_json, dict):
                summary = item.summary_json.get("summary")
                if isinstance(summary, str) and summary.strip():
                    recent_support_progress_summaries.append(summary.strip())
            if len(recent_support_progress_summaries) >= 5:
                break

        return {
            "total_users_with_snapshots": snapshot_user_count,
            "recent_snapshot_count": len(recent_snapshots),
            "weekly_reflection_snapshot_count": weekly_snapshot_count,
            "top_recurring_patterns": top_recurring_patterns,
            "intervention_effectiveness_summary": self._build_intervention_effectiveness(
                recent_interventions
            ),
            "recent_support_progress_summaries": recent_support_progress_summaries,
        }

    def _build_progress_summary(
        self,
        *,
        latest_snapshot: dict[str, Any] | None,
        latest_weekly_snapshot: dict[str, Any] | None,
        top_themes: list[str],
        recurring_patterns: list[str],
    ) -> str | None:
        snapshot_summary = None
        if isinstance(latest_weekly_snapshot, dict):
            snapshot_summary = latest_weekly_snapshot.get("summary")
        if not snapshot_summary and isinstance(latest_snapshot, dict):
            snapshot_summary = latest_snapshot.get("summary")

        if isinstance(snapshot_summary, str) and snapshot_summary.strip():
            return snapshot_summary.strip()

        parts: list[str] = []
        if top_themes:
            parts.append(f"Recent themes include {', '.join(top_themes)}.")
        if recurring_patterns:
            parts.append(f"Recurring patterns show up around {', '.join(recurring_patterns)}.")

        if parts:
            return " ".join(parts)

        return None

    def _build_support_progress_summary(
        self,
        *,
        journal_count: int,
        session_count: int,
        top_themes: list[str],
        recurring_patterns: list[str],
    ) -> str:
        parts = [
            f"{journal_count} journal entr{'y' if journal_count == 1 else 'ies'} tracked",
            f"{session_count} support session{'s' if session_count != 1 else ''}",
        ]
        if top_themes:
            parts.append(f"themes: {', '.join(top_themes)}")
        if recurring_patterns:
            parts.append(f"patterns: {', '.join(recurring_patterns)}")
        return " | ".join(parts)

    def _build_intervention_effectiveness(
        self,
        intervention_rows: list[InterventionLog],
    ) -> dict[str, Any]:
        if not intervention_rows:
            return {
                "logged_count": 0,
                "avg_effectiveness_rating": None,
                "successful_outcomes": 0,
                "latest_outcome_status": None,
            }

        ratings = [
            float(item.effectiveness_rating)
            for item in intervention_rows
            if item.effectiveness_rating is not None
        ]
        successful_outcomes = sum(
            1
            for item in intervention_rows
            if (item.outcome_status or "").lower() in {"helpful", "improved", "completed", "successful"}
        )

        return {
            "logged_count": len(intervention_rows),
            "avg_effectiveness_rating": self._rounded(
                (sum(ratings) / len(ratings)) if ratings else None
            ),
            "successful_outcomes": successful_outcomes,
            "latest_outcome_status": intervention_rows[0].outcome_status,
        }

    def _rounded(self, value: Any) -> float | None:
        if value is None:
            return None
        return round(float(value), 2)
    
    async def build_trend_series(self, *, user_id: str) -> dict[str, Any]:
        recent_check_ins = list(
            (
                await self.session.scalars(
                    select(CheckIn)
                    .where(CheckIn.user_id == user_id)
                    .order_by(CheckIn.created_at.asc())
                    .limit(12)
                )
            ).all()
        )

        mood_series = [
            {
                "timestamp": item.created_at.isoformat(),
                "mood_score": item.mood_score,
                "stress_score": item.stress_score,
                "energy_score": item.energy_score,
                "sleep_hours": item.sleep_hours,
            }
            for item in recent_check_ins
        ]

        recurring_trigger_rows = list(
            (
                await self.session.scalars(
                    select(TriggerCluster)
                    .where(TriggerCluster.user_id == user_id)
                    .order_by(desc(TriggerCluster.frequency), desc(TriggerCluster.updated_at))
                    .limit(8)
                )
            ).all()
        )

        trigger_frequency = [
            {
                "trigger": item.cluster_name,
                "frequency": item.frequency,
            }
            for item in recurring_trigger_rows
            if item.cluster_name
        ]

        return {
            "mood_series": mood_series,
            "trigger_frequency": trigger_frequency,
        }