from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mental_wellbeing_api.api.deps import db_session_dep, request_context_dep, require_permission
from mental_wellbeing_api.models.organization import Organization, OrganizationMembership, Role
from mental_wellbeing_api.schemas.auth import RequestContextResponse
from mental_wellbeing_api.schemas.enterprise import (
    OrganizationMembershipResponse,
    OrganizationResponse,
)
from mental_wellbeing_api.schemas.governance import (
    EnterpriseSettingResponse,
    ResolvedEnterpriseSettingsResponse,
)
from mental_wellbeing_api.services.auth_service import RequestContext
from mental_wellbeing_api.services.enterprise_settings_service import EnterpriseSettingsService

router = APIRouter(
    prefix="/enterprise",
    tags=["enterprise"],
    dependencies=[Depends(require_permission("enterprise:read"))],
)


@router.get("/context", response_model=RequestContextResponse)
async def get_enterprise_context(
    context: RequestContext = Depends(request_context_dep),
) -> RequestContextResponse:
    return context.to_response()


@router.get("/settings/resolved", response_model=ResolvedEnterpriseSettingsResponse)
async def get_resolved_settings_for_context(
    context: RequestContext = Depends(request_context_dep),
    session: AsyncSession = Depends(db_session_dep),
) -> ResolvedEnterpriseSettingsResponse:
    service = EnterpriseSettingsService(session)
    payload = await service.resolve_settings(organization_id=context.organization_id)
    return ResolvedEnterpriseSettingsResponse(**payload)


@router.get("/settings/organization/current", response_model=EnterpriseSettingResponse)
async def get_current_organization_settings(
    context: RequestContext = Depends(request_context_dep),
    session: AsyncSession = Depends(db_session_dep),
) -> EnterpriseSettingResponse:
    if not context.organization_id:
        raise HTTPException(status_code=404, detail="No organization in current context")

    service = EnterpriseSettingsService(session)
    return await service.get_organization_settings(context.organization_id)


@router.get("/organizations/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: str,
    session: AsyncSession = Depends(db_session_dep),
) -> OrganizationResponse:
    organization = await session.scalar(
        select(Organization).where(Organization.id == organization_id)
    )
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization


@router.get(
    "/organizations/{organization_id}/memberships",
    response_model=list[OrganizationMembershipResponse],
)
async def list_organization_memberships(
    organization_id: str,
    session: AsyncSession = Depends(db_session_dep),
) -> list[OrganizationMembershipResponse]:
    rows = list(
        (
            await session.scalars(
                select(OrganizationMembership)
                .options(
                    selectinload(OrganizationMembership.organization),
                    selectinload(OrganizationMembership.role).selectinload(Role.permissions),
                )
                .where(OrganizationMembership.organization_id == organization_id)
            )
        ).all()
    )
    return rows