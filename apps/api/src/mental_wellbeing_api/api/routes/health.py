from fastapi import APIRouter
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from mental_wellbeing_api.core.config import get_settings
from mental_wellbeing_api.db.session import get_engine
from mental_wellbeing_api.services.redis_client import get_redis_client

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
    }


@router.get("/health/dependencies")
async def health_dependencies() -> dict:
    db_status = "ok"
    redis_status = "ok"
    db_error = None
    redis_error = None

    try:
        engine = get_engine()
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        db_status = "error"
        db_error = str(exc)

    try:
        redis_client = get_redis_client()
        await redis_client.ping()
    except RedisError as exc:
        redis_status = "error"
        redis_error = str(exc)

    overall_status = "ok" if db_status == "ok" and redis_status == "ok" else "degraded"

    return {
        "status": overall_status,
        "dependencies": {
            "postgres": {
                "status": db_status,
                "error": db_error,
            },
            "redis": {
                "status": redis_status,
                "error": redis_error,
            },
        },
    }