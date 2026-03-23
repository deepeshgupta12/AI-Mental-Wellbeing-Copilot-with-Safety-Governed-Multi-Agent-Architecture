from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event
from mental_wellbeing_api.orchestration.state import AgentRuntimeState


def run_execution_finalize_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    execution_path = state.get("execution_path", [])
    handoff_history = state.get("handoff_history", [])
    progress_summary = state.get("progress_summary")
    recurring_patterns = state.get("recurring_patterns", [])

    follow_up_required = bool(state.get("follow_up_required", False))
    scheduler_backend = state.get("scheduler_backend")
    follow_up_plan_created = bool(state.get("follow_up_plan_id"))
    follow_up_contract_available = bool(state.get("follow_up_contract"))
    care_plan_required = bool(state.get("care_plan_required", False))
    care_program_key = state.get("care_program_key")
    language = (
        state.get("preferred_language")
        or state.get("content_language")
        or state.get("preference_signals", {}).get("preferred_language")
        or "en"
    )

    summary = (
        f"Executed {len(execution_path)} nodes with "
        f"{len(handoff_history)} handoffs. Final strategy: "
        f"{state.get('support_strategy', 'unknown')}."
    )

    if progress_summary:
        summary += " Trend summary available."
    if recurring_patterns:
        summary += f" Recurring patterns surfaced: {len(recurring_patterns)}."

    summary += f" Follow-up required: {'yes' if follow_up_required else 'no'}."
    summary += f" Scheduler backend: {scheduler_backend or 'none'}."
    summary += f" Follow-up plan created: {'yes' if follow_up_plan_created else 'no'}."
    summary += (
        f" Follow-up contract available: {'yes' if follow_up_contract_available else 'no'}."
    )
    summary += f" Care plan required: {'yes' if care_plan_required else 'no'}."
    summary += f" Care program key: {care_program_key or 'none'}."
    summary += f" Language: {language}."

    state = append_execution_event(
        state,
        node_name="execution_finalize",
        metadata={
            "execution_path_length": len(execution_path),
            "handoff_count": len(handoff_history),
            "has_progress_summary": bool(progress_summary),
            "recurring_pattern_count": len(recurring_patterns),
            "follow_up_required": follow_up_required,
            "scheduler_backend": scheduler_backend,
            "follow_up_plan_created": follow_up_plan_created,
            "follow_up_contract_available": follow_up_contract_available,
            "care_plan_required": care_plan_required,
            "care_program_key": care_program_key,
            "language": language,
        },
    )

    return {
        **state,
        "execution_summary": summary,
    }