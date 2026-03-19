from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState


def run_trend_analyzer_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    progress_summary = state.get("progress_summary")
    recurring_patterns = state.get("recurring_patterns", [])
    intervention_effectiveness = state.get("intervention_effectiveness", {})
    support_progress_summary = state.get("support_progress_summary")

    trend_summary_parts: list[str] = []

    if progress_summary:
        trend_summary_parts.append(progress_summary)

    if support_progress_summary:
        trend_summary_parts.append(support_progress_summary)

    if recurring_patterns:
        trend_summary_parts.append(
            "Recurring patterns noticed: " + ", ".join(recurring_patterns[:3]) + "."
        )

    avg_effectiveness = intervention_effectiveness.get("avg_effectiveness_rating")
    if avg_effectiveness is not None:
        trend_summary_parts.append(
            f"Average intervention effectiveness so far: {avg_effectiveness}."
        )

    trend_summary = " ".join(part.strip() for part in trend_summary_parts if part).strip()

    journaling_insights = list(state.get("journaling_insights", []))
    if recurring_patterns:
        journaling_insights.append(
            f"Recurring patterns worth tracking: {', '.join(recurring_patterns[:2])}."
        )

    follow_up_suggestions = list(state.get("follow_up_suggestions", []))
    if progress_summary:
        follow_up_suggestions.append("I can help unpack what this progress pattern means for next steps.")

    state = {
        **state,
        "trend_summary": trend_summary or None,
        "journaling_insights": journaling_insights[:4],
        "follow_up_suggestions": follow_up_suggestions[:4],
    }
    state = append_execution_event(
        state,
        node_name="trend_analyzer",
        metadata={
            "has_progress_summary": bool(progress_summary),
            "recurring_pattern_count": len(recurring_patterns),
            "has_intervention_effectiveness": bool(intervention_effectiveness),
        },
    )
    state = append_handoff(
        state,
        from_agent="trend_analyzer",
        to_agent="preference_learning",
        reason="trend signals prepared for personalization and response composition",
    )
    return state