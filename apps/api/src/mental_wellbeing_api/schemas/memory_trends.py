from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class MemoryItemResponse(BaseModel):
    source_type: str
    source_id: str
    title: str
    summary: str
    created_at: datetime


class MemorySummaryResponse(BaseModel):
    user_id: str
    display_name: str | None
    wellbeing_goals: str | None
    recent_memories: list[MemoryItemResponse]


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