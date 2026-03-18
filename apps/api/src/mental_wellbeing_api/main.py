from __future__ import annotations

import time
from contextlib import asynccontextmanager
from uuid import uuid4

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from structlog.contextvars import bind_contextvars, clear_contextvars

from mental_wellbeing_api.api.router import api_router
from mental_wellbeing_api.core.config import get_settings
from mental_wellbeing_api.core.logging import configure_logging
from mental_wellbeing_api.db.session import get_engine
from mental_wellbeing_api.services.redis_client import get_redis_client

logger = structlog.get_logger("mental_wellbeing_api")


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    yield
    await get_engine().dispose()
    await get_redis_client().aclose()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.app_debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_telemetry_middleware(request: Request, call_next):
        clear_contextvars()
        request_id = str(uuid4())
        bind_contextvars(
            request_id=request_id,
            path=request.url.path,
            method=request.method,
        )

        started_at = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
            logger.exception("request_failed", duration_ms=duration_ms)
            raise

        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request_completed",
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        return response

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation failed",
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, __: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    @app.get("/", tags=["meta"])
    async def root() -> dict[str, str]:
        return {
            "message": "AI Mental Wellbeing Copilot API",
            "docs": "/docs",
            "health": f"{settings.api_v1_prefix}/health",
        }

    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()