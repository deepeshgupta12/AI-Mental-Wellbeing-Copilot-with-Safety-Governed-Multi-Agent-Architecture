from __future__ import annotations

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.models.agent_trace import AgentTrace
from mental_wellbeing_api.models.safety_flag import SafetyFlag
from mental_wellbeing_api.models.user import User
from mental_wellbeing_api.orchestration.graph import build_agent_runtime_graph
from mental_wellbeing_api.schemas.agent_runtime import (
    AgentRuntimeSmokeRequest,
    AgentRuntimeSmokeResponse,
    HandoffEventResponse,
    NodeTraceEventResponse,
    RecalledMemoryItemResponse,
)
from mental_wellbeing_api.schemas.follow_up import FollowUpPlanResponse
from mental_wellbeing_api.services.follow_up_service import FollowUpService
from mental_wellbeing_api.services.memory_service import MemoryRecallItem, MemoryService
from mental_wellbeing_api.services.preference_service import PreferenceService
from mental_wellbeing_api.services.safety_service import (
    SafetyEvaluationResponse,
    SafetyService,
)
from mental_wellbeing_api.services.trend_intelligence_service import TrendIntelligenceService


class AgentRuntimeService:
    def __init__(self, session: AsyncSession) -> None:
        self.graph = build_agent_runtime_graph()
        self.session = session
        self.safety_service = SafetyService()
        self.memory_service = MemoryService(session)
        self.preference_service = PreferenceService(session)
        self.trend_service = TrendIntelligenceService(session)
        self.follow_up_service = FollowUpService(session)

    async def evaluate_safety_only(
        self,
        payload: AgentRuntimeSmokeRequest,
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

    async def _log_execution_trace(
        self,
        *,
        user_id: str | None,
        trace_id: str,
        result: dict,
    ) -> None:
        node_trace = result.get("node_trace", [])
        handoff_history = result.get("handoff_history", [])

        for event in node_trace:
            node_name = event.get("node_name", "unknown")
            matching_handoff = next(
                (
                    item
                    for item in handoff_history
                    if item.get("from_agent") == node_name
                ),
                None,
            )

            trace = AgentTrace(
                user_id=user_id,
                session_id=None,
                message_id=None,
                trace_name=trace_id,
                agent_name=node_name,
                handoff_from_agent=matching_handoff.get("from_agent") if matching_handoff else None,
                handoff_to_agent=matching_handoff.get("to_agent") if matching_handoff else None,
                input_payload_json={
                    "routing_contract": result.get("routing_contract", {}),
                    "intent_label": result.get("intent_label"),
                    "support_strategy": result.get("support_strategy"),
                    "support_mode": result.get("support_mode"),
                    "specialist_agent": result.get("specialist_agent"),
                },
                output_payload_json={
                    "status": event.get("status"),
                    "metadata": event.get("metadata", {}),
                },
                status=event.get("status", "completed"),
                latency_ms=None,
                notes="V2 graph execution trace",
            )
            self.session.add(trace)

        await self.session.commit()

    def _build_follow_up_plan_preview(self, result: dict) -> dict:
        return {
            "plan_type": result.get("follow_up_plan_type"),
            "title": result.get("follow_up_plan_title"),
            "description": result.get("follow_up_plan_description"),
            "scheduled_for": result.get("follow_up_due_at"),
            "delivery_channel": result.get("follow_up_delivery_channel"),
            "status": result.get("follow_up_status"),
        }

    async def run_smoke_flow(
        self,
        payload: AgentRuntimeSmokeRequest,
    ) -> AgentRuntimeSmokeResponse:
        safety_eval = self.safety_service.evaluate_text(payload.user_input)

        trace_id = str(uuid4())
        recalled_memory_items: list[MemoryRecallItem] = []
        preference_signals: dict[str, str] = {}
        what_helped_before: list[str] = []
        trend_bundle: dict = {}
        generated_follow_up_plan = None
        follow_up_event_ids: list[str] = []
        resolved_follow_up_contract: dict = {}
        resolved_temporal_contract: dict = {}
        resolved_scheduler_backend: str | None = None

        if payload.user_id is not None:
            user_id = str(payload.user_id)
            user_exists = await self.session.scalar(select(User.id).where(User.id == user_id))
            if user_exists:
                preference_signals = await self.preference_service.get_preference_signals(user_id)

            recalled_memory_items = await self.memory_service.recall(
                user_id=user_id,
                query=payload.user_input,
                limit=4,
                preference_signals=preference_signals,
            )

            what_helped_before = await self.memory_service.recall_texts(
                user_id=user_id,
                query=payload.user_input,
                limit=2,
                memory_kinds=["helpful_strategy", "preference"],
                preference_signals=preference_signals,
            )

            trend_bundle = await self.trend_service.build_runtime_trend_bundle(user_id=user_id)

            await self._log_memory_trace(
                user_id=user_id,
                trace_name="memory_retrieval",
                recalled_items=recalled_memory_items,
                preference_signals=preference_signals,
            )

        result = self.graph.invoke(
            {
                "trace_id": trace_id,
                "user_id": str(payload.user_id) if payload.user_id else "",
                "user_input": payload.user_input,
                "provider": payload.provider,
                "execution_path": [],
                "node_trace": [],
                "handoff_history": [],
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
                "learned_preferences": {},
                "what_helped_before": what_helped_before,
                "coping_recommendations": [],
                "journaling_insights": [],
                "follow_up_suggestions": [],
                "progress_summary": trend_bundle.get("progress_summary"),
                "support_progress_summary": trend_bundle.get("support_progress_summary"),
                "trend_summary": None,
                "recurring_patterns": trend_bundle.get("recurring_patterns", []),
                "intervention_effectiveness": trend_bundle.get("intervention_effectiveness", {}),
                "trend_visualization": trend_bundle.get("trend_visualization", {}),
                "follow_up_required": False,
                "follow_up_plan_type": None,
                "follow_up_plan_title": None,
                "follow_up_plan_description": None,
                "follow_up_due_at": None,
                "follow_up_delivery_channel": None,
                "follow_up_status": None,
                "follow_up_contract": {},
                "follow_up_plan_id": None,
                "follow_up_event_ids": [],
                "temporal_contract": {},
                "scheduler_backend": None,
                "risk_level": safety_eval.risk_level,
                "safety_flag_type": safety_eval.safety_flag_type,
                "safety_summary": safety_eval.safety_summary,
                "safety_override": safety_eval.safety_override,
            }
        )

        if payload.user_id is not None:
            user_id = str(payload.user_id)

            await self._log_execution_trace(
                user_id=user_id,
                trace_id=trace_id,
                result=result,
            )

            await self.preference_service.persist_learned_preferences(
                user_id=user_id,
                learned_preferences=result.get("learned_preferences"),
            )
            preference_signals = await self.preference_service.get_preference_signals(user_id)

            if bool(result.get("follow_up_required")) and not bool(result.get("safety_override", False)):
                created_plan = await self.follow_up_service.create_plan(
                    user_id=user_id,
                    source_agent=result.get("specialist_agent") or "response_composer",
                    plan_type=result.get("follow_up_plan_type") or "general_follow_up",
                    title=result.get("follow_up_plan_title") or "Continue this support plan",
                    description=result.get("follow_up_plan_description"),
                    session_id=None,
                    action_plan_id=None,
                    delivery_channel=result.get("follow_up_delivery_channel") or "in_app",
                    timezone_name=preference_signals.get("timezone"),
                    support_mode=result.get("support_mode"),
                    support_strategy=result.get("support_strategy"),
                    specialist_agent=result.get("specialist_agent"),
                    metadata={
                        "trace_id": trace_id,
                        "routing_contract": result.get("routing_contract", {}),
                        "follow_up_contract": result.get("follow_up_contract", {}),
                        "temporal_contract": result.get("temporal_contract", {}),
                        "scheduler_backend": result.get("scheduler_backend"),
                        "follow_up_suggestions": result.get("follow_up_suggestions", [])[:3],
                    },
                )
                generated_follow_up_plan = FollowUpPlanResponse.model_validate(created_plan)

                resolved_follow_up_contract = generated_follow_up_plan.scheduling_contract_json or {}
                resolved_temporal_contract = {}
                if isinstance(resolved_follow_up_contract, dict):
                    temporal_payload = resolved_follow_up_contract.get("temporal_contract")
                    if isinstance(temporal_payload, dict):
                        resolved_temporal_contract = temporal_payload
                    scheduler_backend_value = resolved_follow_up_contract.get("scheduler_backend")
                    if isinstance(scheduler_backend_value, str) and scheduler_backend_value.strip():
                        resolved_scheduler_backend = scheduler_backend_value

                created_event = await self.follow_up_service.create_event(
                    follow_up_plan_id=created_plan.id,
                    user_id=user_id,
                    event_type="scheduled",
                    outcome_status="planned",
                    notes="Runtime-generated follow up plan scheduled.",
                    event_payload_json={
                        "scheduler_backend": resolved_scheduler_backend or result.get("scheduler_backend"),
                        "follow_up_due_at": result.get("follow_up_due_at"),
                        "temporal_contract": resolved_temporal_contract or result.get("temporal_contract", {}),
                    },
                )
                follow_up_event_ids = [created_event.id]

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
            specialist_response=result.get("specialist_response"),
            final_response=result.get("final_response", ""),
            risk_level=result.get("risk_level", "low"),
            safety_flag_type=result.get("safety_flag_type"),
            safety_summary=result.get("safety_summary"),
            safety_override=bool(result.get("safety_override", False)),
            tone_label=result.get("tone_label"),
            emotion_label=result.get("emotion_label"),
            emotion_intensity=result.get("emotion_intensity"),
            emotional_signals=result.get("emotional_signals", []),
            intent_label=result.get("intent_label"),
            support_mode=result.get("support_mode"),
            support_strategy=result.get("support_strategy"),
            specialist_agent=result.get("specialist_agent"),
            routing_reason=result.get("routing_reason"),
            routing_contract=result.get("routing_contract", {}),
            session_context=result.get("session_context"),
            preference_signals=preference_signals,
            what_helped_before=what_helped_before,
            coping_recommendations=result.get("coping_recommendations", []),
            journaling_insights=result.get("journaling_insights", []),
            follow_up_suggestions=result.get("follow_up_suggestions", []),
            progress_summary=result.get("progress_summary"),
            support_progress_summary=result.get("support_progress_summary"),
            trend_summary=result.get("trend_summary"),
            recurring_patterns=result.get("recurring_patterns", []),
            intervention_effectiveness=result.get("intervention_effectiveness", {}),
            trend_visualization=result.get("trend_visualization", {}),
            follow_up_required=bool(result.get("follow_up_required", False)),
            follow_up_plan=self._build_follow_up_plan_preview(result),
            follow_up_contract=resolved_follow_up_contract or result.get("follow_up_contract", {}),
            follow_up_plan_id=generated_follow_up_plan.id if generated_follow_up_plan else result.get("follow_up_plan_id"),
            follow_up_event_ids=follow_up_event_ids or result.get("follow_up_event_ids", []),
            temporal_contract=resolved_temporal_contract or result.get("temporal_contract", {}),
            scheduler_backend=resolved_scheduler_backend or result.get("scheduler_backend"),
            generated_follow_up_plan=generated_follow_up_plan,
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
            execution_path=result.get("execution_path", []),
            node_trace=[
                NodeTraceEventResponse(
                    node_name=item.get("node_name", ""),
                    status=item.get("status", "completed"),
                    timestamp=item.get("timestamp"),
                    metadata=item.get("metadata", {}),
                )
                for item in result.get("node_trace", [])
            ],
            handoff_history=[
                HandoffEventResponse(
                    from_agent=item.get("from_agent", ""),
                    to_agent=item.get("to_agent", ""),
                    reason=item.get("reason", ""),
                    timestamp=item.get("timestamp"),
                    contract=item.get("contract", {}),
                )
                for item in result.get("handoff_history", [])
            ],
            execution_summary=result.get("execution_summary"),
        )