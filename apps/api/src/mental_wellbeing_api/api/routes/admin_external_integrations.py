from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import db_session_dep, require_permission
from mental_wellbeing_api.schemas.external_integrations import (
    AdminExternalIntegrationOverviewResponse,
    ExternalIntegrationConnectionResponse,
    ExternalSignalResponse,
    ExternalSyncJobResponse,
)
from mental_wellbeing_api.services.external_integrations_service import (
    ExternalIntegrationsService,
)

router = APIRouter(
    prefix="/admin/external-integrations",
    tags=["admin-external-integrations"],
    dependencies=[Depends(require_permission("admin:read"))],
)


@router.get("/overview", response_model=AdminExternalIntegrationOverviewResponse)
async def get_admin_external_integrations_overview(
    organization_id: str | None = Query(default=None),
    session: AsyncSession = Depends(db_session_dep),
) -> AdminExternalIntegrationOverviewResponse:
    service = ExternalIntegrationsService(session)
    payload = await service.build_admin_overview(organization_id=organization_id)
    return AdminExternalIntegrationOverviewResponse(**payload)


@router.get("/connections", response_model=list[ExternalIntegrationConnectionResponse])
async def list_admin_external_integration_connections(
    organization_id: str | None = Query(default=None),
    session: AsyncSession = Depends(db_session_dep),
) -> list[ExternalIntegrationConnectionResponse]:
    service = ExternalIntegrationsService(session)
    return await service.list_connections(organization_id=organization_id)


@router.get("/sync-jobs", response_model=list[ExternalSyncJobResponse])
async def list_admin_external_sync_jobs(
    organization_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    session: AsyncSession = Depends(db_session_dep),
) -> list[ExternalSyncJobResponse]:
    service = ExternalIntegrationsService(session)
    return await service.list_sync_jobs(organization_id=organization_id, limit=limit)


@router.get("/signals", response_model=list[ExternalSignalResponse])
async def list_admin_external_signals(
    organization_id: str | None = Query(default=None),
    signal_type: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(db_session_dep),
) -> list[ExternalSignalResponse]:
    service = ExternalIntegrationsService(session)
    return await service.list_signals(
        organization_id=organization_id,
        signal_type=signal_type,
        limit=limit,
    )