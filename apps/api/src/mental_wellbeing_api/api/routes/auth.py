from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import authenticated_context_dep, db_session_dep
from mental_wellbeing_api.core.config import get_settings
from mental_wellbeing_api.schemas.auth import (
    AuthBootstrapResponse,
    DevSessionCreateRequest,
    LogoutResponse,
    RequestContextResponse,
)
from mental_wellbeing_api.services.auth_service import AuthService, RequestContext

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/dev-session", response_model=AuthBootstrapResponse)
async def create_dev_session(
    payload: DevSessionCreateRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> AuthBootstrapResponse:
    settings = get_settings()
    if settings.is_production_like and not settings.auth_allow_dev_bootstrap:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dev session bootstrap is disabled in this deployment",
        )

    service = AuthService(session)
    access_token, auth_session, user, organization, membership, permissions = await service.create_dev_session(
        email=payload.email,
        display_name=payload.display_name,
        organization_name=payload.organization_name,
        organization_slug=payload.organization_slug,
        role_name=payload.role_name,
        auth_provider=payload.auth_provider,
    )

    return AuthBootstrapResponse(
        access_token=access_token,
        expires_at=auth_session.expires_at,
        user=user,
        organization=organization,
        membership=membership,
        session=auth_session,
        permissions=permissions,
    )


@router.get("/me", response_model=RequestContextResponse)
async def get_me(
    context: RequestContext = Depends(authenticated_context_dep),
) -> RequestContextResponse:
    return context.to_response()


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    context: RequestContext = Depends(authenticated_context_dep),
    session: AsyncSession = Depends(db_session_dep),
) -> LogoutResponse:
    if context.session is None:
        return LogoutResponse(status="ok", session_id=None)

    service = AuthService(session)
    await service.revoke_session(
        session_id=context.session.id,
        reason="user_logout",
    )
    return LogoutResponse(status="ok", session_id=context.session.id)