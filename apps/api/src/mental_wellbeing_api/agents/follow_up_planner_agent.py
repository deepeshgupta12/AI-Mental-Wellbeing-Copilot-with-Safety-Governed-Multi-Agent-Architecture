from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.services.follow_up_contract_service import FollowUpContractService
from mental_wellbeing_api.services.localization_service import LocalizationService


def _resolve_follow_up_required(state: AgentRuntimeState) -> bool:
    if state.get("safety_override"):
        return False

    follow_up_suggestions = state.get("follow_up_suggestions", [])
    progress_summary = state.get("progress_summary")
    support_progress_summary = state.get("support_progress_summary")
    support_mode = (state.get("support_mode") or "").strip().lower()

    if follow_up_suggestions:
        return True
    if progress_summary or support_progress_summary:
        return True
    return support_mode in {
        "plan",
        "recover",
        "reflect",
        "connect",
        "reframe",
        "activate",
        "stabilize",
    }


def _resolve_follow_up_plan_type(state: AgentRuntimeState) -> str:
    support_mode = (state.get("support_mode") or "").strip().lower()
    support_strategy = (state.get("support_strategy") or "").strip().lower()

    if support_mode:
        return support_mode
    if support_strategy:
        return support_strategy
    return "general_follow_up"


def _resolve_follow_up_title(state: AgentRuntimeState, language: str) -> str:
    support_mode = (state.get("support_mode") or "").strip().lower()

    title_map = {
        "plan": "Check in on your plan",
        "recover": "Check in on your recovery",
        "reflect": "Continue this reflection",
        "connect": "Follow up on reaching out",
        "reframe": "Revisit this reframe",
        "activate": "Restart with one small step",
        "stabilize": "Follow up on stabilization",
    }
    fallback = title_map.get(support_mode, "Continue this support plan")
    service = LocalizationService(None)  # type: ignore[arg-type]
    if language == "hi":
        hi_map = {
            "plan": "अपने प्लान पर फिर से नज़र डालें",
            "recover": "रिकवरी पर दोबारा चेक-इन करें",
            "reflect": "इस चिंतन को आगे बढ़ाएँ",
            "connect": "किसी से जुड़ने पर फॉलो-अप करें",
            "reframe": "इस सोच को फिर से देखें",
            "activate": "एक छोटे कदम से फिर शुरू करें",
            "stabilize": "स्थिरता पर फॉलो-अप करें",
        }
        return hi_map.get(support_mode, service.localize_text("care_plan_title_default", language, fallback))
    if language == "hinglish":
        hinglish_map = {
            "plan": "Apne plan par check-in karo",
            "recover": "Recovery par dobara check-in karo",
            "reflect": "Is reflection ko aage badhao",
            "connect": "Reach out karne par follow-up karo",
            "reframe": "Is thought ko phir se dekho",
            "activate": "Ek chhote step se phir shuru karo",
            "stabilize": "Stability par follow-up karo",
        }
        return hinglish_map.get(support_mode, fallback)
    return fallback


def _resolve_follow_up_description(state: AgentRuntimeState, language: str) -> str:
    follow_up_suggestions = state.get("follow_up_suggestions", [])
    service = LocalizationService(None)  # type: ignore[arg-type]

    if follow_up_suggestions:
        value = str(follow_up_suggestions[0])
    elif state.get("progress_summary"):
        value = f"Revisit your progress: {state.get('progress_summary')}"
    elif state.get("support_strategy"):
        value = f"Follow up on the {state.get('support_strategy')} support plan."
    else:
        value = "Check in on the next small step from this support session."

    if language == "hi":
        return {
            "Check in on the next small step from this support session.": "इस सपोर्ट सेशन के अगले छोटे कदम पर फिर से चेक-इन करें।",
        }.get(value, value)
    if language == "hinglish":
        return {
            "Check in on the next small step from this support session.": "Is support session ke next small step par check-in karo.",
        }.get(value, value)
    return service.localize_text("care_plan_step_complete", language, value) if value == "Step completed" else value


def _build_temporal_contract(
    *,
    state: AgentRuntimeState,
    plan_type: str,
    delivery_channel: str,
    scheduled_for_iso: str | None,
) -> dict[str, Any]:
    trace_id = state.get("trace_id", "")
    user_id = state.get("user_id", "")
    support_mode = state.get("support_mode")
    specialist_agent = state.get("specialist_agent")

    return {
        "enabled": False,
        "workflow_name": "follow_up_reminder_workflow",
        "task_queue": "mental_wellbeing_followups",
        "namespace": "default",
        "future_ready": True,
        "user_id": user_id,
        "trace_id": trace_id,
        "plan_type": plan_type,
        "delivery_channel": delivery_channel,
        "support_mode": support_mode,
        "specialist_agent": specialist_agent,
        "scheduled_for": scheduled_for_iso,
        "idempotency_key": f"followup:{user_id}:{trace_id}:{plan_type}",
    }


def run_follow_up_planner_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    follow_up_required = _resolve_follow_up_required(state)
    language = (
        state.get("preferred_language")
        or state.get("content_language")
        or state.get("preference_signals", {}).get("preferred_language")
        or "en"
    )

    if not follow_up_required:
        state = {
            **state,
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
        }
        state = append_execution_event(
            state,
            node_name="follow_up_planner",
            metadata={
                "follow_up_required": False,
                "reason": "no continuity trigger detected",
                "language": language,
            },
        )
        state = append_handoff(
            state,
            from_agent="follow_up_planner",
            to_agent="response_composer",
            reason="no follow up plan required",
        )
        return state

    contracts = FollowUpContractService()

    plan_type = _resolve_follow_up_plan_type(state)
    title = _resolve_follow_up_title(state, language)
    description = _resolve_follow_up_description(state, language)
    delivery_channel = "in_app"
    timezone_name = state.get("preference_signals", {}).get("timezone")

    contract = contracts.build_contract(
        user_id=state.get("user_id", ""),
        source_agent=state.get("specialist_agent") or "response_composer",
        plan_type=plan_type,
        title=title,
        description=description,
        delivery_channel=delivery_channel,
        timezone_name=timezone_name,
        support_mode=state.get("support_mode"),
        support_strategy=state.get("support_strategy"),
        specialist_agent=state.get("specialist_agent"),
        metadata={
            "trace_id": state.get("trace_id"),
            "routing_contract": state.get("routing_contract", {}),
            "follow_up_suggestions": state.get("follow_up_suggestions", [])[:3],
            "generated_at": datetime.now(UTC).isoformat(),
            "language": language,
        },
    )

    scheduled_for = contract.get("scheduled_for")
    scheduled_for_iso = scheduled_for.isoformat() if scheduled_for else None

    scheduler_backend = "local-contract"
    scheduling_contract_json = dict(contract.get("scheduling_contract_json", {}))
    scheduling_contract_json["scheduler_backend"] = scheduler_backend

    follow_up_contract = {
        "plan_type": plan_type,
        "title": title,
        "description": description,
        "delivery_channel": delivery_channel,
        "scheduled_for": scheduled_for_iso,
        "timezone": contract.get("timezone"),
        "cadence_json": contract.get("cadence_json", {}),
        "scheduling_contract_json": scheduling_contract_json,
        "metadata_json": contract.get("metadata_json", {}),
        "language": language,
    }

    temporal_contract = _build_temporal_contract(
        state=state,
        plan_type=plan_type,
        delivery_channel=delivery_channel,
        scheduled_for_iso=scheduled_for_iso,
    )

    state = {
        **state,
        "follow_up_required": True,
        "follow_up_plan_type": plan_type,
        "follow_up_plan_title": title,
        "follow_up_plan_description": description,
        "follow_up_due_at": scheduled_for_iso,
        "follow_up_delivery_channel": delivery_channel,
        "follow_up_status": "planned",
        "follow_up_contract": follow_up_contract,
        "follow_up_plan_id": None,
        "follow_up_event_ids": [],
        "temporal_contract": temporal_contract,
        "scheduler_backend": scheduler_backend,
        "care_plan_required": True,
        "care_program_key": f"{plan_type}_program",
        "care_plan_language": language,
    }
    state = append_execution_event(
        state,
        node_name="follow_up_planner",
        metadata={
            "follow_up_required": True,
            "plan_type": plan_type,
            "delivery_channel": delivery_channel,
            "scheduler_backend": scheduler_backend,
            "language": language,
        },
    )
    state = append_handoff(
        state,
        from_agent="follow_up_planner",
        to_agent="response_composer",
        reason="follow up continuity contract prepared",
    )
    return state