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

    def _should_create_follow_up_plan(
        self,
        *,
        user_id: str | None,
        safety_override: bool,
        follow_up_suggestions: list[str],
    ) -> bool:
        return bool(user_id and not safety_override and follow_up_suggestions)

    def _resolve_follow_up_plan_type(self, result: dict) -> str:
        support_mode = (result.get("support_mode") or "").strip().lower()
        support_strategy = (result.get("support_strategy") or "").strip().lower()

        if support_mode:
            return support_mode
        if support_strategy:
            return support_strategy
        return "general_follow_up"

    def _resolve_follow_up_title(self, result: dict) -> str:
        support_mode = (result.get("support_mode") or "").strip().lower()

        title_map = {
            "plan": "Check in on your plan",
            "recover": "Check in on your recovery",
            "reflect": "Continue this reflection",
            "connect": "Follow up on reaching out",
            "reframe": "Revisit this reframe",
            "activate": "Restart with one small step",
            "stabilize": "Follow up on stabilization",
        }
        return title_map.get(support_mode, "Continue this support plan")

    def _resolve_follow_up_description(self, result: dict) -> str | None:
        follow_up_suggestions = result.get("follow_up_suggestions", [])
        if follow_up_suggestions:
            return str(follow_up_suggestions[0])

        support_strategy = result.get("support_strategy")
        if support_strategy:
            return f"Follow up on the {support_strategy} support plan."
        return "Check in on the next small step from this support session."

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

            follow_up_suggestions = result.get("follow_up_suggestions", [])
            if self._should_create_follow_up_plan(
                user_id=user_id,
                safety_override=bool(result.get("safety_override", False)),
                follow_up_suggestions=follow_up_suggestions,
            ):
                created_plan = await self.follow_up_service.create_plan(
                    user_id=user_id,
                    source_agent=result.get("specialist_agent") or "response_composer",
                    plan_type=self._resolve_follow_up_plan_type(result),
                    title=self._resolve_follow_up_title(result),
                    description=self._resolve_follow_up_description(result),
                    session_id=None,
                    action_plan_id=None,
                    delivery_channel="in_app",
                    timezone_name=preference_signals.get("timezone"),
                    support_mode=result.get("support_mode"),
                    support_strategy=result.get("support_strategy"),
                    specialist_agent=result.get("specialist_agent"),
                    metadata={
                        "trace_id": trace_id,
                        "routing_contract": result.get("routing_contract", {}),
                        "follow_up_suggestions": follow_up_suggestions[:3],
                    },
                )
                generated_follow_up_plan = FollowUpPlanResponse.model_validate(created_plan)

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