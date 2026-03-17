from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.models.safety_flag import SafetyFlag
from mental_wellbeing_api.models.user import User
from mental_wellbeing_api.orchestration.graph import build_agent_runtime_graph
from mental_wellbeing_api.schemas.agent_runtime import (
    AgentRuntimeSmokeRequest,
    AgentRuntimeSmokeResponse,
)
from mental_wellbeing_api.services.safety_service import (
    SafetyEvaluationResponse,
    SafetyService,
)


class AgentRuntimeService:
    def __init__(self, session: AsyncSession) -> None:
        self.graph = build_agent_runtime_graph()
        self.session = session
        self.safety_service = SafetyService()

    async def evaluate_safety_only(
        self, payload: AgentRuntimeSmokeRequest
    ) -> SafetyEvaluationResponse:
        return self.safety_service.evaluate_text(payload.user_input)

    async def run_smoke_flow(
        self, payload: AgentRuntimeSmokeRequest
    ) -> AgentRuntimeSmokeResponse:
        safety_eval = self.safety_service.evaluate_text(payload.user_input)

        result = self.graph.invoke(
            {
                "user_input": payload.user_input,
                "provider": payload.provider,
                "risk_level": safety_eval.risk_level,
                "safety_flag_type": safety_eval.safety_flag_type,
                "safety_summary": safety_eval.safety_summary,
                "safety_override": safety_eval.safety_override,
            }
        )

        if payload.user_id is not None and safety_eval.safety_override and safety_eval.safety_flag_type:
            user_exists = await self.session.scalar(
                select(User.id).where(User.id == str(payload.user_id))
            )
            if user_exists:
                flag = SafetyFlag(
                    user_id=str(payload.user_id),
                    severity=safety_eval.risk_level,
                    flag_type=safety_eval.safety_flag_type,
                    summary=safety_eval.safety_summary,
                    needs_review=True,
                )
                self.session.add(flag)
                await self.session.commit()

        return AgentRuntimeSmokeResponse(
            status="ok",
            provider=payload.provider,
            structured_input=result.get("structured_input", ""),
            reflective_response=result.get("reflective_response", ""),
            final_response=result.get("final_response", ""),
            risk_level=result.get("risk_level", "low"),
            safety_flag_type=result.get("safety_flag_type"),
            safety_summary=result.get("safety_summary"),
            safety_override=bool(result.get("safety_override", False)),
        )