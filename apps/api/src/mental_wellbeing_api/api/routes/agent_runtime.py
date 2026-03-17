from __future__ import annotations

from fastapi import APIRouter

from mental_wellbeing_api.schemas.agent_runtime import (
    AgentRuntimeSmokeRequest,
    AgentRuntimeSmokeResponse,
)
from mental_wellbeing_api.services.agent_runtime_service import AgentRuntimeService

router = APIRouter(prefix="/agent-runtime", tags=["agent-runtime"])


@router.post("/smoke", response_model=AgentRuntimeSmokeResponse)
async def agent_runtime_smoke(
    payload: AgentRuntimeSmokeRequest,
) -> AgentRuntimeSmokeResponse:
    service = AgentRuntimeService()
    return service.run_smoke_flow(payload)