from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.models.agent_trace import AgentTrace
from mental_wellbeing_api.models.safety_flag import SafetyFlag
from mental_wellbeing_api.models.user import User
from mental_wellbeing_api.orchestration.graph import build_agent_runtime_graph
from mental_wellbeing_api.schemas.agent_runtime import (
    AgentRuntimeSmokeRequest,
    AgentRuntimeSmokeResponse,
    RecalledMemoryItemResponse,
)
from mental_wellbeing_api.services.memory_service import MemoryRecallItem, MemoryService
from mental_wellbeing_api.services.preference_service import PreferenceService
from mental_wellbeing_api.services.safety_service import (
    SafetyEvaluationResponse,
    SafetyService,
)


class AgentRuntimeService:
    def __init__(self, session: AsyncSession) -> None:
        self.graph = build_agent_runtime_graph()
        self.session = session
        self.safety_service = SafetyService()
        self.memory_service = MemoryService(session)
        self.preference_service = PreferenceService(session)

    async def evaluate_safety_only(
        self, payload: AgentRuntimeSmokeRequest
    ) -> SafetyEvaluationResponse:
        return self.safety_service.evaluate_text(payload.user_input)

    async def _log_memory_trace(
        self,
        *,
        user_id: str | None,
        trace_name: str,
        recalled_items: list[MemoryRecallItem],
        preference_signals: dict[str, str],
    ) -> None:
        trace = AgentTrace(
            user_id=user_id,
            session_id=None,
            message_id=None,
            trace_name=trace_name,
            agent_name="memory_service",
            handoff_from_agent=None,
            handoff_to_agent=None,
            input_payload_json={
                "user_id": user_id,
                "preference_keys": list(preference_signals.keys()),
            },
            output_payload_json={
                "memory_hits": [
                    {
                        "source_type": item.source_type,
                        "source_id": item.source_id,
                        "memory_kind": item.memory_kind,
                        "content": item.content,
                        "importance_score": item.importance_score,
                        "relevance_score": item.relevance_score,
                    }
                    for item in recalled_items
                ]
            },
            status="completed",
            latency_ms=None,
            notes="V2 retrieval trace",
        )
        self.session.add(trace)
        await self.session.commit()

    async def run_smoke_flow(
        self, payload: AgentRuntimeSmokeRequest
    ) -> AgentRuntimeSmokeResponse:
        safety_eval = self.safety_service.evaluate_text(payload.user_input)

        recalled_memory_items: list[MemoryRecallItem] = []
        preference_signals: dict[str, str] = {}
        what_helped_before: list[str] = []

        if payload.user_id is not None:
            user_id = str(payload.user_id)
            user_exists = await self.session.scalar(select(User.id).where(User.id == user_id))
            if user_exists:
                preference_signals = await self.preference_service.get_preference_signals(user_id)

                recalled_memory_items = await self.memory_service.recall(
                    user_id=user_id,
                    query=payload.user_input,
                    limit=4,
                )

                what_helped_before = await self.memory_service.recall_texts(
                    user_id=user_id,
                    query=payload.user_input,
                    limit=2,
                    memory_kinds=["helpful_strategy", "preference"],
                )

                await self._log_memory_trace(
                    user_id=user_id,
                    trace_name="memory_retrieval",
                    recalled_items=recalled_memory_items,
                    preference_signals=preference_signals,
                )

        result = self.graph.invoke(
            {
                "user_id": str(payload.user_id) if payload.user_id else "",
                "user_input": payload.user_input,
                "provider": payload.provider,
                "recalled_memories": [item.content for item in recalled_memory_items],
                "recalled_memory_items": [
                    {
                        "source_type": item.source_type,
                        "source_id": item.source_id,
                        "memory_kind": item.memory_kind,
                        "content": item.content,
                        "importance_score": item.importance_score,
                        "relevance_score": item.relevance_score,
                        "created_at": item.created_at.isoformat() if item.created_at else None,
                    }
                    for item in recalled_memory_items
                ],
                "preference_signals": preference_signals,
                "what_helped_before": what_helped_before,
                "risk_level": safety_eval.risk_level,
                "safety_flag_type": safety_eval.safety_flag_type,
                "safety_summary": safety_eval.safety_summary,
                "safety_override": safety_eval.safety_override,
            }
        )

        if (
            payload.user_id is not None
            and safety_eval.safety_override
            and safety_eval.safety_flag_type
        ):
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
            support_strategy=result.get("support_strategy"),
            session_context=result.get("session_context"),
            preference_signals=preference_signals,
            what_helped_before=what_helped_before,
            memory_hits=[
                RecalledMemoryItemResponse(
                    source_type=item.source_type,
                    source_id=item.source_id,
                    memory_kind=item.memory_kind,
                    content=item.content,
                    importance_score=item.importance_score,
                    relevance_score=item.relevance_score,
                    created_at=item.created_at.isoformat() if item.created_at else None,
                )
                for item in recalled_memory_items
            ],
        )