from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import db_session_dep, require_permission
from mental_wellbeing_api.schemas.admin import (
    AdminEnterpriseAnalyticsOverviewResponse,
    AdminEnterpriseOrganizationDetailResponse,
    AdminOrganizationSummaryResponse,
)
from mental_wellbeing_api.services.enterprise_admin_analytics_service import (
    EnterpriseAdminAnalyticsService,
)

router = APIRouter(
    prefix="/admin/enterprise-analytics",
    tags=["admin-enterprise-analytics"],
    dependencies=[Depends(require_permission("admin:read"))],
)


@router.get("/overview", response_model=AdminEnterpriseAnalyticsOverviewResponse)
async def get_enterprise_analytics_overview(
    session: AsyncSession = Depends(db_session_dep),
) -> AdminEnterpriseAnalyticsOverviewResponse:
    service = EnterpriseAdminAnalyticsService(session)
    payload = await service.build_overview()
    return AdminEnterpriseAnalyticsOverviewResponse(**payload)


@router.get("/organizations", response_model=list[AdminOrganizationSummaryResponse])
async def list_enterprise_organizations(
    session: AsyncSession = Depends(db_session_dep),
) -> list[AdminOrganizationSummaryResponse]:
    service = EnterpriseAdminAnalyticsService(session)
    payload = await service.list_organizations()
    return [AdminOrganizationSummaryResponse(**item) for item in payload]


@router.get(
    "/organizations/{organization_id}",
    response_model=AdminEnterpriseOrganizationDetailResponse,
)
async def get_enterprise_organization_detail(
    organization_id: str,
    session: AsyncSession = Depends(db_session_dep),
) -> AdminEnterpriseOrganizationDetailResponse:
    service = EnterpriseAdminAnalyticsService(session)
    try:
        payload = await service.get_organization_detail(organization_id=organization_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return AdminEnterpriseOrganizationDetailResponse(**payload)