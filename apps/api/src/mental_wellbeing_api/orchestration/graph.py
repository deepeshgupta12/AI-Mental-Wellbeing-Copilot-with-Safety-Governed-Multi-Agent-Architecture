from __future__ import annotations

from langgraph.graph import END, StateGraph
from mental_wellbeing_api.agents.cbt_reframing_agent import run_cbt_reframing_agent
from mental_wellbeing_api.agents.habit_care_plan_agent import run_habit_care_plan_agent
from mental_wellbeing_api.agents.journaling_insight_agent import (
    run_journaling_insight_agent,
)
from mental_wellbeing_api.agents.sleep_recovery_agent import run_sleep_recovery_agent
from mental_wellbeing_api.agents.social_support_agent import run_social_support_agent
from mental_wellbeing_api.agents.tone_emotion_analyzer_agent import (
    run_tone_emotion_analyzer_agent,
)

from mental_wellbeing_api.agents.behavioral_activation_agent import (
    run_behavioral_activation_agent,
)
from mental_wellbeing_api.agents.distress_stabilization_agent import (
    run_distress_stabilization_agent,
)
from mental_wellbeing_api.agents.execution_finalize_agent import (
    run_execution_finalize_agent,
)
from mental_wellbeing_api.agents.input_structuring_agent import (
    run_input_structuring_agent,
)
from mental_wellbeing_api.agents.intent_router_agent import run_intent_router_agent
from mental_wellbeing_api.agents.policy_guardrail_agent import (
    run_policy_guardrail_agent,
)
from mental_wellbeing_api.agents.reflective_agent import run_reflective_agent
from mental_wellbeing_api.agents.response_composer_agent import (
    run_response_composer_agent,
)
from mental_wellbeing_api.agents.safety_triage_agent import run_safety_triage_agent
from mental_wellbeing_api.agents.session_context_builder_agent import (
    run_session_context_builder_agent,
)
from mental_wellbeing_api.agents.support_mode_router_agent import (
    run_support_mode_router_agent,
)
from mental_wellbeing_api.orchestration.state import AgentRuntimeState


def _route_after_safety(state: AgentRuntimeState) -> str:
    if state.get("safety_override"):
        return "response_composer"
    return "session_context_builder"


def _route_after_support_mode(state: AgentRuntimeState) -> str:
    specialist_agent = state.get("specialist_agent", "reflective_support")

    if specialist_agent == "distress_stabilization":
        return "distress_stabilization"
    if specialist_agent == "behavioral_activation":
        return "behavioral_activation"
    if specialist_agent == "cbt_reframing":
        return "cbt_reframing"
    if specialist_agent == "sleep_recovery":
        return "sleep_recovery"
    if specialist_agent == "social_support":
        return "social_support"
    if specialist_agent == "journaling_insight":
        return "journaling_insight"
    if specialist_agent == "habit_care_plan":
        return "habit_care_plan"

    return "reflective_support"


def build_agent_runtime_graph():
    graph = StateGraph(AgentRuntimeState)

    graph.add_node("safety_triage", run_safety_triage_agent)
    graph.add_node("session_context_builder", run_session_context_builder_agent)
    graph.add_node("input_structuring", run_input_structuring_agent)
    graph.add_node("tone_emotion_analyzer", run_tone_emotion_analyzer_agent)
    graph.add_node("intent_router", run_intent_router_agent)
    graph.add_node("support_mode_router", run_support_mode_router_agent)

    graph.add_node("reflective_support", run_reflective_agent)
    graph.add_node("distress_stabilization", run_distress_stabilization_agent)
    graph.add_node("behavioral_activation", run_behavioral_activation_agent)
    graph.add_node("cbt_reframing", run_cbt_reframing_agent)
    graph.add_node("sleep_recovery", run_sleep_recovery_agent)
    graph.add_node("social_support", run_social_support_agent)
    graph.add_node("journaling_insight", run_journaling_insight_agent)
    graph.add_node("habit_care_plan", run_habit_care_plan_agent)

    graph.add_node("response_composer", run_response_composer_agent)
    graph.add_node("policy_guardrail", run_policy_guardrail_agent)
    graph.add_node("execution_finalize", run_execution_finalize_agent)

    graph.set_entry_point("safety_triage")

    graph.add_conditional_edges(
        "safety_triage",
        _route_after_safety,
        {
            "session_context_builder": "session_context_builder",
            "response_composer": "response_composer",
        },
    )

    graph.add_edge("session_context_builder", "input_structuring")
    graph.add_edge("input_structuring", "tone_emotion_analyzer")
    graph.add_edge("tone_emotion_analyzer", "intent_router")
    graph.add_edge("intent_router", "support_mode_router")

    graph.add_conditional_edges(
        "support_mode_router",
        _route_after_support_mode,
        {
            "reflective_support": "reflective_support",
            "distress_stabilization": "distress_stabilization",
            "behavioral_activation": "behavioral_activation",
            "cbt_reframing": "cbt_reframing",
            "sleep_recovery": "sleep_recovery",
            "social_support": "social_support",
            "journaling_insight": "journaling_insight",
            "habit_care_plan": "habit_care_plan",
        },
    )

    graph.add_edge("reflective_support", "response_composer")
    graph.add_edge("distress_stabilization", "response_composer")
    graph.add_edge("behavioral_activation", "response_composer")
    graph.add_edge("cbt_reframing", "response_composer")
    graph.add_edge("sleep_recovery", "response_composer")
    graph.add_edge("social_support", "response_composer")
    graph.add_edge("journaling_insight", "response_composer")
    graph.add_edge("habit_care_plan", "response_composer")

    graph.add_edge("response_composer", "policy_guardrail")
    graph.add_edge("policy_guardrail", "execution_finalize")
    graph.add_edge("execution_finalize", END)

    return graph.compile()