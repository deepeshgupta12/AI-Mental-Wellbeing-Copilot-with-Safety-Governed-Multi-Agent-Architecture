from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class SafetyFlagResponse(BaseModel):
    id: str
    user_id: str
    severity: str
    flag_type: str
    summary: str | None
    needs_review: bool
    created_at: datetime

    model_config = {"from_attributes": True}