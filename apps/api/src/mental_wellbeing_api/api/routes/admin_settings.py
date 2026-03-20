from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import db_session_dep, request_context_dep, require_permission
from mental_wellbeing_api.models.organization import Organization
from mental_wellbeing_api.schemas.governance import (
    EnterpriseSettingResponse,
    EnterpriseSettingUpdateRequest,
    ResolvedEnterpriseSettingsResponse,
)
from mental_wellbeing_api.schemas.infrastructure import (
    InfrastructureRuntimeSummaryResponse,
    StoredArtifactResponse,
)
from mental_wellbeing_api.services.auth_service import RequestContext
from mental_wellbeing_api.services.enterprise_settings_service import EnterpriseSettingsService
from mental_wellbeing_api.services.infrastructure_governance_service import (
    InfrastructureGovernanceService,
)

router = APIRouter(
    prefix="/admin/settings",
    tags=["admin-settings"],
    dependencies=[Depends(require_permission("admin:read"))],
)


def _resolve_actor(context: RequestContext) -> str:
    return context.user_id or context.auth_subject or "admin"


@router.get("/deployment/current", response_model=EnterpriseSettingResponse)
async def get_current_deployment_settings(
    session: AsyncSession = Depends(db_session_dep),
) -> EnterpriseSettingResponse:
    service = EnterpriseSettingsService(session)
    return await service.get_deployment_settings()


@router.put(
    "/deployment/current",
    response_model=EnterpriseSettingResponse,
    dependencies=[Depends(require_permission("admin:write"))],
)
async def update_current_deployment_settings(
    payload: EnterpriseSettingUpdateRequest,
    context: RequestContext = Depends(request_context_dep),
    session: AsyncSession = Depends(db_session_dep),
) -> EnterpriseSettingResponse:
    service = EnterpriseSettingsService(session)
    return await service.update_deployment_settings(
        payload=payload.payload_json,
        actor=_resolve_actor(context),
        change_note=payload.change_note,
    )


@router.get("/organizations/{organization_id}", response_model=EnterpriseSettingResponse)
async def get_organization_settings(
    organization_id: str,
    session: AsyncSession = Depends(db_session_dep),
) -> EnterpriseSettingResponse:
    organization = await session.scalar(
        select(Organization).where(Organization.id == organization_id)
    )
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    service = EnterpriseSettingsService(session)
    return await service.get_organization_settings(organization_id)


@router.put(
    "/organizations/{organization_id}",
    response_model=EnterpriseSettingResponse,
    dependencies=[Depends(require_permission("admin:write"))],
)
async def update_organization_settings(
    organization_id: str,
    payload: EnterpriseSettingUpdateRequest,
    context: RequestContext = Depends(request_context_dep),
    session: AsyncSession = Depends(db_session_dep),
) -> EnterpriseSettingResponse:
    organization = await session.scalar(
        select(Organization).where(Organization.id == organization_id)
    )
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    service = EnterpriseSettingsService(session)
    return await service.update_organization_settings(
        organization_id=organization_id,
        payload=payload.payload_json,
        actor=_resolve_actor(context),
        change_note=payload.change_note,
    )


@router.get("/resolved", response_model=ResolvedEnterpriseSettingsResponse)
async def get_resolved_enterprise_settings(
    organization_id: str | None = Query(default=None),
    session: AsyncSession = Depends(db_session_dep),
) -> ResolvedEnterpriseSettingsResponse:
    service = EnterpriseSettingsService(session)
    payload = await service.resolve_settings(organization_id=organization_id)
    return ResolvedEnterpriseSettingsResponse(**payload)


@router.get("/infrastructure/summary", response_model=InfrastructureRuntimeSummaryResponse)
async def get_infrastructure_runtime_summary(
    organization_id: str | None = Query(default=None),
    session: AsyncSession = Depends(db_session_dep),
) -> InfrastructureRuntimeSummaryResponse:
    service = InfrastructureGovernanceService(session)
    payload = await service.build_runtime_summary(organization_id=organization_id)
    return InfrastructureRuntimeSummaryResponse(**payload)


@router.get("/infrastructure/artifacts", response_model=list[StoredArtifactResponse])
async def list_recent_infrastructure_artifacts(
    limit: int = Query(default=50, ge=1, le=200),
    scope_type: str | None = Query(default=None),
    scope_id: str | None = Query(default=None),
    artifact_kind: str | None = Query(default=None),
    session: AsyncSession = Depends(db_session_dep),
) -> list[StoredArtifactResponse]:
    service = InfrastructureGovernanceService(session)
    return await service.list_recent_artifacts(
        limit=limit,
        scope_type=scope_type,
        scope_id=scope_id,
        artifact_kind=artifact_kind,
    )