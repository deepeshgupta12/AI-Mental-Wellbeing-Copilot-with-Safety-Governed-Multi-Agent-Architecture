from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.api.deps import db_session_dep
from mental_wellbeing_api.schemas.agent_runtime import (
    AgentRuntimeSmokeRequest,
    AgentRuntimeSmokeResponse,
)
from mental_wellbeing_api.services.agent_runtime_service import AgentRuntimeService
from mental_wellbeing_api.services.safety_service import SafetyEvaluationResponse

router = APIRouter(prefix="/agent-runtime", tags=["agent-runtime"])


@router.post("/smoke", response_model=AgentRuntimeSmokeResponse)
async def agent_runtime_smoke(
    payload: AgentRuntimeSmokeRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> AgentRuntimeSmokeResponse:
    service = AgentRuntimeService(session)
    return await service.run_smoke_flow(payload)


@router.post("/safety-evaluate", response_model=SafetyEvaluationResponse)
async def agent_runtime_safety_evaluate(
    payload: AgentRuntimeSmokeRequest,
    session: AsyncSession = Depends(db_session_dep),
) -> SafetyEvaluationResponse:
    service = AgentRuntimeService(session)
    return await service.evaluate_safety_only(payload)