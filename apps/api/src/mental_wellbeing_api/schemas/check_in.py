from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CheckInCreateRequest(BaseModel):
    user_id: str
    mood_score: int | None = None
    stress_score: int | None = None
    energy_score: int | None = None
    sleep_hours: int | None = None
    notes: str | None = None


class CheckInResponse(BaseModel):
    id: str
    user_id: str
    mood_score: int | None
    stress_score: int | None
    energy_score: int | None
    sleep_hours: int | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}