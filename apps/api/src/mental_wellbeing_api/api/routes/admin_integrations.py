from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import db_session_dep, require_permission
from mental_wellbeing_api.schemas.admin import (
    AdminIntegrationOverviewResponse,
    AdminIntegrationRuntimeFeedResponse,
)
from mental_wellbeing_api.services.integration_registry_service import (
    IntegrationRegistryService,
)

router = APIRouter(
    prefix="/admin/integrations",
    tags=["admin-integrations"],
    dependencies=[Depends(require_permission("admin:read"))],
)


@router.get("/overview", response_model=AdminIntegrationOverviewResponse)
async def get_integration_overview(
    organization_id: str | None = Query(default=None),
    session: AsyncSession = Depends(db_session_dep),
) -> AdminIntegrationOverviewResponse:
    service = IntegrationRegistryService(session)
    payload = await service.build_overview(organization_id=organization_id)
    return AdminIntegrationOverviewResponse(**payload)


@router.get("/runtime-feed", response_model=AdminIntegrationRuntimeFeedResponse)
async def get_integration_runtime_feed(
    organization_id: str | None = Query(default=None),
    session: AsyncSession = Depends(db_session_dep),
) -> AdminIntegrationRuntimeFeedResponse:
    service = IntegrationRegistryService(session)
    payload = await service.build_runtime_feed(organization_id=organization_id)
    return AdminIntegrationRuntimeFeedResponse(**payload)