from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import db_session_dep
from mental_wellbeing_api.api.utils import ensure_user_exists
from mental_wellbeing_api.schemas.localization import (
    LocalizationCatalogResponse,
    LocalizationRuntimeCopyResponse,
    UserLanguagePreferenceResponse,
    UserLanguagePreferenceUpdateRequest,
)
from mental_wellbeing_api.services.localization_service import LocalizationService

router = APIRouter(prefix="/localization", tags=["localization"])


@router.get("/catalog", response_model=LocalizationCatalogResponse)
async def get_localization_catalog() -> LocalizationCatalogResponse:
    service = LocalizationService(None)  # type: ignore[arg-type]
    return LocalizationCatalogResponse(**service.catalog())


@router.get("/runtime-copy", response_model=LocalizationRuntimeCopyResponse)
async def get_runtime_copy(
    language: str | None = Query(default=None),
) -> LocalizationRuntimeCopyResponse:
    service = LocalizationService(None)  # type: ignore[arg-type]
    return LocalizationRuntimeCopyResponse(**service.runtime_copy(language))


@router.get("/users/{user_id}/preferences", response_model=UserLanguagePreferenceResponse)
async def get_user_language_preferences(
    user_id: str,
    session: AsyncSession = Depends(db_session_dep),
) -> UserLanguagePreferenceResponse:
    await ensure_user_exists(session, user_id)
    service = LocalizationService(session)
    return UserLanguagePreferenceResponse(**(await service.get_user_language_preference(user_id)))


@router.put("/users/{user_id}/preferences", response_model=UserLanguagePreferenceResponse)
async def update_user_language_preferences(
    user_id: str,
    payload: UserLanguagePreferenceUpdateRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> UserLanguagePreferenceResponse:
    await ensure_user_exists(session, user_id)
    service = LocalizationService(session)
    return UserLanguagePreferenceResponse(
        **(
            await service.upsert_user_language_preference(
                user_id=user_id,
                preferred_language=payload.preferred_language,
                content_language=payload.content_language,
                fallback_language=payload.fallback_language,
            )
        )
    )