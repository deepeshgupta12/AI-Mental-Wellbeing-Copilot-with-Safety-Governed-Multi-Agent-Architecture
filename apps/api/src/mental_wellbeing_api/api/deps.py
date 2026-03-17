from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.db.session import get_db_session


async def db_session_dep() -> AsyncSession:
    async for session in get_db_session():
        yield session