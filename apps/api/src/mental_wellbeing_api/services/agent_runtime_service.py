from __future__ import annotations

from mental_wellbeing_api.orchestration.graph import build_agent_runtime_graph
from mental_wellbeing_api.schemas.agent_runtime import (
    AgentRuntimeSmokeRequest,
    AgentRuntimeSmokeResponse,
)


class AgentRuntimeService:
    def __init__(self) -> None:
        self.graph = build_agent_runtime_graph()

    def run_smoke_flow(
        self, payload: AgentRuntimeSmokeRequest
    ) -> AgentRuntimeSmokeResponse:
        result = self.graph.invoke(
            {
                "user_input": payload.user_input,
                "provider": payload.provider,
            }
        )

        return AgentRuntimeSmokeResponse(
            status="ok",
            provider=payload.provider,
            structured_input=result.get("structured_input", ""),
            reflective_response=result.get("reflective_response", ""),
            final_response=result.get("final_response", ""),
        )