from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ActionPlanCreateRequest(BaseModel):
    user_id: str
    title: str
    description: str | None = None
    timeframe: str | None = None


class ActionPlanResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: str | None
    timeframe: str | None
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}