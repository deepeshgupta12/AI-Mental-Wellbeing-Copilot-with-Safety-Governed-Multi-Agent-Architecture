from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class MemoryItemResponse(BaseModel):
    source_type: str
    source_id: str
    title: str
    summary: str
    created_at: datetime
    memory_kind: str | None = None
    importance_score: float | None = None


class MemorySummaryResponse(BaseModel):
    user_id: str
    display_name: str | None
    wellbeing_goals: str | None
    recent_memories: list[MemoryItemResponse]
    helpful_before: list[str] = Field(default_factory=list)
    recurring_triggers: list[str] = Field(default_factory=list)
    preference_signals: dict[str, str] = Field(default_factory=dict)


class TrendSummaryResponse(BaseModel):
    user_id: str
    total_check_ins: int
    avg_mood_score: float | None
    avg_stress_score: float | None
    avg_energy_score: float | None
    avg_sleep_hours: float | None
    total_journal_entries: int
    total_conversation_sessions: int
    total_conversation_messages: int
    latest_check_in_at: datetime | None
    latest_journal_entry_at: datetime | None
    latest_conversation_at: datetime | None
    latest_snapshot_window_type: str | None = None
    latest_snapshot_created_at: datetime | None = None