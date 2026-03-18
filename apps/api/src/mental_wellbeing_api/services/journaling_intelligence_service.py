from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.models.journal_entry import JournalEntry
from mental_wellbeing_api.models.journal_theme import JournalTheme
from mental_wellbeing_api.models.trend_snapshot import TrendSnapshot
from mental_wellbeing_api.models.trigger_cluster import TriggerCluster


@dataclass
class JournalAnalysisResult:
    summary: str
    emotional_tone: str
    structured_insights_json: dict[str, Any]
    themes: list[dict[str, Any]]
    trigger_candidates: list[str]
    helpful_patterns: list[str]


class JournalingIntelligenceService:
    THEME_KEYWORDS: dict[str, list[str]] = {
        "sleep": ["sleep", "insomnia", "night", "awake", "waking up", "rest"],
        "work_stress": ["work", "office", "job", "deadline", "meeting", "manager"],
        "overwhelm": ["overwhelmed", "stress", "stressed", "heavy", "burnout"],
        "loneliness": ["alone", "lonely", "isolated", "disconnected"],
        "self_criticism": ["failure", "worthless", "always", "never", "ruin everything", "should"],
        "routine": ["routine", "habit", "consistency", "self-care", "discipline"],
        "motivation": ["stuck", "motivation", "can't start", "procrastinating", "avoid"],
        "relationships": ["friend", "family", "partner", "relationship", "people"],
        "reflection": ["journal", "reflect", "reflection", "wrote", "writing"],
    }

    EMOTION_HINTS: dict[str, list[str]] = {
        "anxious": ["anxious", "panic", "overwhelmed", "stress", "stressed", "can't breathe"],
        "sad": ["sad", "low", "down", "hopeless", "alone", "lonely"],
        "exhausted": ["tired", "exhausted", "drained", "burnout", "heavy"],
        "frustrated": ["frustrated", "angry", "annoyed", "irritated"],
        "hopeful": ["better", "helped", "improving", "hopeful", "manageable", "reset"],
    }

    HELPFUL_PATTERNS = [
        "helped",
        "felt better",
        "worked",
        "reset",
        "calmed me down",
        "made it easier",
    ]

    TRIGGER_MARKERS = ["after", "before", "during", "when"]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def analyze_entry(
        self,
        *,
        content: str,
        title: str | None = None,
        entry_type: str | None = None,
    ) -> JournalAnalysisResult:
        normalized = " ".join(content.split()).strip()
        sentences = self._split_sentences(normalized)

        summary = self._build_summary(title=title, sentences=sentences)
        emotional_tone = self._detect_emotional_tone(normalized)
        themes = self._extract_themes(normalized, emotional_tone)
        trigger_candidates = self._extract_triggers(normalized)
        helpful_patterns = self._extract_helpful_patterns(sentences)

        structured = {
            "summary": summary,
            "emotional_tone": emotional_tone,
            "entry_type": entry_type,
            "detected_themes": [item["theme_name"] for item in themes],
            "trigger_candidates": trigger_candidates,
            "helpful_patterns": helpful_patterns,
            "sentence_count": len(sentences),
        }

        return JournalAnalysisResult(
            summary=summary,
            emotional_tone=emotional_tone,
            structured_insights_json=structured,
            themes=themes,
            trigger_candidates=trigger_candidates,
            helpful_patterns=helpful_patterns,
        )

    async def persist_journal_derivatives(
        self,
        *,
        user_id: str,
        journal_entry: JournalEntry,
        analysis: JournalAnalysisResult,
    ) -> None:
        for item in analysis.themes:
            self.session.add(
                JournalTheme(
                    journal_entry_id=journal_entry.id,
                    user_id=user_id,
                    theme_name=item["theme_name"],
                    sentiment=item["sentiment"],
                    confidence_score=item["confidence_score"],
                )
            )

        now = datetime.now(timezone.utc)
        for trigger in analysis.trigger_candidates:
            existing = await self.session.scalar(
                select(TriggerCluster).where(
                    TriggerCluster.user_id == user_id,
                    TriggerCluster.cluster_name == trigger,
                )
            )
            if existing:
                existing.frequency += 1
                existing.last_seen_at = now
            else:
                self.session.add(
                    TriggerCluster(
                        user_id=user_id,
                        cluster_name=trigger,
                        trigger_text=trigger,
                        frequency=1,
                        last_seen_at=now,
                    )
                )

        await self.session.commit()

    async def upsert_weekly_reflection_snapshot(self, *, user_id: str) -> None:
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        start_dt = datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc)

        entries = list(
            (
                await self.session.scalars(
                    select(JournalEntry)
                    .where(
                        JournalEntry.user_id == user_id,
                        JournalEntry.created_at >= start_dt,
                    )
                    .order_by(desc(JournalEntry.created_at))
                )
            ).all()
        )

        themes = list(
            (
                await self.session.scalars(
                    select(JournalTheme)
                    .where(
                        JournalTheme.user_id == user_id,
                        JournalTheme.created_at >= start_dt,
                    )
                    .order_by(desc(JournalTheme.created_at))
                )
            ).all()
        )

        triggers = list(
            (
                await self.session.scalars(
                    select(TriggerCluster)
                    .where(TriggerCluster.user_id == user_id)
                    .order_by(desc(TriggerCluster.frequency), desc(TriggerCluster.updated_at))
                    .limit(5)
                )
            ).all()
        )

        summary_json = self._build_weekly_snapshot_payload(
            entries=entries,
            themes=themes,
            triggers=triggers,
        )

        existing = await self.session.scalar(
            select(TrendSnapshot).where(
                TrendSnapshot.user_id == user_id,
                TrendSnapshot.window_type == "weekly_reflection",
                TrendSnapshot.snapshot_start_date == start_date,
                TrendSnapshot.snapshot_end_date == end_date,
            )
        )

        if existing:
            existing.summary_json = summary_json
        else:
            self.session.add(
                TrendSnapshot(
                    user_id=user_id,
                    window_type="weekly_reflection",
                    snapshot_start_date=start_date,
                    snapshot_end_date=end_date,
                    summary_json=summary_json,
                )
            )

        await self.session.commit()

    def _split_sentences(self, text: str) -> list[str]:
        if not text:
            return []
        return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]

    def _build_summary(self, *, title: str | None, sentences: list[str]) -> str:
        parts: list[str] = []
        if title:
            parts.append(title.strip())
        parts.extend(sentences[:2])

        summary = " ".join(parts).strip()
        if len(summary) <= 220:
            return summary
        return summary[:217].rstrip() + "..."

    def _detect_emotional_tone(self, text: str) -> str:
        for tone, hints in self.EMOTION_HINTS.items():
            if any(hint in text.lower() for hint in hints):
                return tone
        return "reflective"

    def _extract_themes(self, text: str, emotional_tone: str) -> list[dict[str, Any]]:
        lowered = text.lower()
        matches: list[dict[str, Any]] = []

        for theme_name, keywords in self.THEME_KEYWORDS.items():
            hit_count = sum(1 for keyword in keywords if keyword in lowered)
            if hit_count > 0:
                confidence = min(0.55 + (0.1 * hit_count), 0.95)
                matches.append(
                    {
                        "theme_name": theme_name,
                        "sentiment": emotional_tone,
                        "confidence_score": round(confidence, 2),
                    }
                )

        if not matches:
            matches.append(
                {
                    "theme_name": "reflection",
                    "sentiment": emotional_tone,
                    "confidence_score": 0.5,
                }
            )

        return matches[:5]

    def _extract_triggers(self, text: str) -> list[str]:
        lowered = text.lower()
        found: list[str] = []

        for marker in self.TRIGGER_MARKERS:
            pattern = rf"\b{marker}\s+([a-z][a-z\s]{{1,30}}?)(?:[.,;!?]|$)"
            for match in re.finditer(pattern, lowered):
                phrase = match.group(1).strip()
                phrase = " ".join(phrase.split()[:4])
                if phrase:
                    found.append(f"{marker} {phrase}")

        special_cases = [
            "after work",
            "at night",
            "before sleep",
            "during meetings",
            "after meetings",
        ]
        for item in special_cases:
            if item in lowered:
                found.append(item)

        deduped: list[str] = []
        seen: set[str] = set()
        for item in found:
            normalized = item.strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                deduped.append(normalized)

        return deduped[:5]

    def _extract_helpful_patterns(self, sentences: list[str]) -> list[str]:
        helpful: list[str] = []
        for sentence in sentences:
            lowered = sentence.lower()
            if any(pattern in lowered for pattern in self.HELPFUL_PATTERNS):
                helpful.append(sentence.strip())
        return helpful[:3]

    def _build_weekly_snapshot_payload(
        self,
        *,
        entries: list[JournalEntry],
        themes: list[JournalTheme],
        triggers: list[TriggerCluster],
    ) -> dict[str, Any]:
        theme_counts = Counter(item.theme_name for item in themes)
        top_themes = [name for name, _ in theme_counts.most_common(3)]
        recurring_triggers = [item.cluster_name for item in triggers[:3]]

        if not entries:
            summary = None
        else:
            summary_parts: list[str] = [
                f"This week includes {len(entries)} journal entr{'y' if len(entries) == 1 else 'ies'}."
            ]
            if top_themes:
                summary_parts.append(f"Common themes: {', '.join(top_themes)}.")
            if recurring_triggers:
                summary_parts.append(
                    f"Recurring trigger patterns: {', '.join(recurring_triggers)}."
                )
            summary = " ".join(summary_parts)

        return {
            "entry_count": len(entries),
            "top_themes": top_themes,
            "recurring_triggers": recurring_triggers,
            "summary": summary,
        }