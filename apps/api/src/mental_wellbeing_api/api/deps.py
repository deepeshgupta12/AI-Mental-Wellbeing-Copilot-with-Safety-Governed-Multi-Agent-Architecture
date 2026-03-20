from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.db.session import get_db_session
from mental_wellbeing_api.services.auth_service import AuthService, RequestContext
from mental_wellbeing_api.services.rbac_service import RBACService

bearer_scheme = HTTPBearer(auto_error=False)


async def db_session_dep() -> AsyncSession:
    async for session in get_db_session():
        yield session


async def request_context_dep(
    request: Request,
    session: AsyncSession = Depends(db_session_dep),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> RequestContext:
    service = AuthService(session)
    bearer_token = credentials.credentials if credentials else None
    return await service.resolve_request_context(
        request=request,
        bearer_token=bearer_token,
    )


async def authenticated_context_dep(
    context: RequestContext = Depends(request_context_dep),
) -> RequestContext:
    if not context.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return context


def require_permission(permission_key: str) -> Callable[..., RequestContext]:
    async def permission_dep(
        context: RequestContext = Depends(request_context_dep),
    ) -> RequestContext:
        if not context.is_authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        if not RBACService.has_permission(permission_key, context.permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission_key}",
            )
        return context

    return permission_dep