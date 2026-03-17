from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class JournalEntryCreateRequest(BaseModel):
    user_id: UUID
    title: str | None = None
    content: str
    entry_type: str | None = None


class JournalEntryResponse(BaseModel):
    id: str
    user_id: str
    title: str | None
    content: str
    entry_type: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}