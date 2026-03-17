from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ConversationSessionCreateRequest(BaseModel):
    user_id: UUID
    title: str | None = None
    status: str = "active"


class ConversationSessionResponse(BaseModel):
    id: str
    user_id: str
    title: str | None
    status: str
    started_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationMessageCreateRequest(BaseModel):
    session_id: UUID
    role: str
    content: str
    message_type: str = "text"


class ConversationMessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    message_type: str
    created_at: datetime

    model_config = {"from_attributes": True}