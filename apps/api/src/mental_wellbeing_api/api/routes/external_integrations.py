from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import authenticated_context_dep, db_session_dep
from mental_wellbeing_api.schemas.external_integrations import (
    ExternalIntegrationConnectionResponse,
    ExternalIntegrationConnectionUpsertRequest,
    ExternalIntegrationIngestRequest,
    ExternalIntegrationIngestResponse,
    ExternalIntegrationSyncRequest,
    ExternalIntegrationCatalogItemResponse,
    ExternalSignalResponse,
    ExternalSyncJobResponse,
    UserExternalIntegrationStatusResponse,
)
from mental_wellbeing_api.services.auth_service import RequestContext
from mental_wellbeing_api.services.external_integrations_service import (
    ExternalIntegrationsService,
)

router = APIRouter(prefix="/external-integrations", tags=["external-integrations"])


def _require_user_context(context: RequestContext) -> tuple[str, str | None]:
    if not context.user_id:
        raise HTTPException(status_code=401, detail="Authenticated user context is required")
    return context.user_id, context.organization_id


@router.get("/catalog", response_model=list[ExternalIntegrationCatalogItemResponse])
async def get_external_integration_catalog(
    context: RequestContext = Depends(authenticated_context_dep),
    session: AsyncSession = Depends(db_session_dep),
) -> list[ExternalIntegrationCatalogItemResponse]:
    _, organization_id = _require_user_context(context)
    service = ExternalIntegrationsService(session)
    return [
        ExternalIntegrationCatalogItemResponse(**item)
        for item in await service.catalog(organization_id=organization_id)
    ]


@router.get("/me/status", response_model=UserExternalIntegrationStatusResponse)
async def get_my_external_integration_status(
    context: RequestContext = Depends(authenticated_context_dep),
    session: AsyncSession = Depends(db_session_dep),
) -> UserExternalIntegrationStatusResponse:
    user_id, organization_id = _require_user_context(context)
    service = ExternalIntegrationsService(session)
    payload = await service.get_user_status(user_id=user_id, organization_id=organization_id)
    return UserExternalIntegrationStatusResponse(**payload)


@router.get("/me/connections", response_model=list[ExternalIntegrationConnectionResponse])
async def get_my_external_integration_connections(
    context: RequestContext = Depends(authenticated_context_dep),
    session: AsyncSession = Depends(db_session_dep),
) -> list[ExternalIntegrationConnectionResponse]:
    user_id, organization_id = _require_user_context(context)
    service = ExternalIntegrationsService(session)
    rows = await service.list_connections(user_id=user_id, organization_id=organization_id)
    return list(rows)


@router.post("/me/connections", response_model=ExternalIntegrationConnectionResponse)
async def upsert_my_external_integration_connection(
    payload: ExternalIntegrationConnectionUpsertRequest,
    context: RequestContext = Depends(authenticated_context_dep),
    session: AsyncSession = Depends(db_session_dep),
) -> ExternalIntegrationConnectionResponse:
    user_id, organization_id = _require_user_context(context)
    service = ExternalIntegrationsService(session)
    try:
        item = await service.upsert_connection(
            user_id=user_id,
            organization_id=organization_id,
            payload=payload.model_dump(),
            actor=context.user_id or context.auth_subject,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return item


@router.post("/me/connections/{connection_id}/sync", response_model=ExternalSyncJobResponse)
async def queue_my_external_integration_sync(
    connection_id: str,
    payload: ExternalIntegrationSyncRequest,
    context: RequestContext = Depends(authenticated_context_dep),
    session: AsyncSession = Depends(db_session_dep),
) -> ExternalSyncJobResponse:
    user_id, organization_id = _require_user_context(context)
    service = ExternalIntegrationsService(session)
    try:
        job = await service.create_sync_job(
            connection_id=connection_id,
            user_id=user_id,
            organization_id=organization_id,
            job_type=payload.job_type,
            requested_by=context.user_id or context.auth_subject,
            sync_window_days=payload.sync_window_days,
            request_payload_json=payload.request_payload_json,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return job


@router.post(
    "/me/connections/{connection_id}/ingest",
    response_model=ExternalIntegrationIngestResponse,
)
async def ingest_my_external_integration_payload(
    connection_id: str,
    payload: ExternalIntegrationIngestRequest,
    context: RequestContext = Depends(authenticated_context_dep),
    session: AsyncSession = Depends(db_session_dep),
) -> ExternalIntegrationIngestResponse:
    user_id, organization_id = _require_user_context(context)
    service = ExternalIntegrationsService(session)
    try:
        result = await service.ingest_payload(
            connection_id=connection_id,
            user_id=user_id,
            organization_id=organization_id,
            payload_json=payload.payload_json,
            source_label=payload.source_label,
            actor=context.user_id or context.auth_subject,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ExternalIntegrationIngestResponse(**result)


@router.get("/me/signals", response_model=list[ExternalSignalResponse])
async def get_my_external_signals(
    signal_type: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    context: RequestContext = Depends(authenticated_context_dep),
    session: AsyncSession = Depends(db_session_dep),
) -> list[ExternalSignalResponse]:
    user_id, organization_id = _require_user_context(context)
    service = ExternalIntegrationsService(session)
    return await service.list_signals(
        user_id=user_id,
        organization_id=organization_id,
        signal_type=signal_type,
        limit=limit,
    )