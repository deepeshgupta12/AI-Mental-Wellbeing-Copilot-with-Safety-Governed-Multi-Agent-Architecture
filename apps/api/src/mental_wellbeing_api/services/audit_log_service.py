from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.models.audit_log import AuditLog


class AuditLogService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_log(
        self,
        *,
        event_type: str,
        entity_type: str,
        entity_id: str,
        title: str,
        details: str | None = None,
        actor_type: str = "system",
        actor_id: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        safety_event_id: str | None = None,
        safety_review_id: str | None = None,
        before_json: dict[str, Any] | None = None,
        after_json: dict[str, Any] | None = None,
        event_payload_json: dict[str, Any] | None = None,
    ) -> AuditLog:
        item = AuditLog(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            session_id=session_id,
            safety_event_id=safety_event_id,
            safety_review_id=safety_review_id,
            actor_type=actor_type,
            actor_id=actor_id,
            title=title,
            details=details,
            before_json=before_json,
            after_json=after_json,
            event_payload_json=event_payload_json,
        )
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item