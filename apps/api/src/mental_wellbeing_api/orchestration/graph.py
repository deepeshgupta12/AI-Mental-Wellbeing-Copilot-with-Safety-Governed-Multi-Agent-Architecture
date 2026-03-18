from __future__ import annotations

from langgraph.graph import END, StateGraph

from mental_wellbeing_api.agents.behavioral_activation_agent import run_behavioral_activation_agent
from mental_wellbeing_api.agents.distress_stabilization_agent import (
    run_distress_stabilization_agent,
)
from mental_wellbeing_api.agents.input_structuring_agent import run_input_structuring_agent
from mental_wellbeing_api.agents.policy_guardrail_agent import run_policy_guardrail_agent
from mental_wellbeing_api.agents.reflective_agent import run_reflective_agent
from mental_wellbeing_api.agents.response_composer_agent import run_response_composer_agent
from mental_wellbeing_api.agents.safety_triage_agent import run_safety_triage_agent
from mental_wellbeing_api.agents.session_context_builder_agent import (
    run_session_context_builder_agent,
)
from mental_wellbeing_api.agents.supervisor_agent import run_supervisor_agent
from mental_wellbeing_api.orchestration.state import AgentRuntimeState


def _route_after_safety(state: AgentRuntimeState) -> str:
    if state.get("safety_override"):
        return "response_composer"
    return "session_context_builder"


def _route_after_supervisor(state: AgentRuntimeState) -> str:
    strategy = state.get("support_strategy", "reflective")
    if strategy == "distress_stabilization":
        return "distress_stabilization"
    if strategy == "behavioral_activation":
        return "behavioral_activation"
    return "reflective_support"


def build_agent_runtime_graph():
    graph = StateGraph(AgentRuntimeState)

    graph.add_node("safety_triage", run_safety_triage_agent)
    graph.add_node("session_context_builder", run_session_context_builder_agent)
    graph.add_node("input_structuring", run_input_structuring_agent)
    graph.add_node("supervisor", run_supervisor_agent)
    graph.add_node("reflective_support", run_reflective_agent)
    graph.add_node("distress_stabilization", run_distress_stabilization_agent)
    graph.add_node("behavioral_activation", run_behavioral_activation_agent)
    graph.add_node("response_composer", run_response_composer_agent)
    graph.add_node("policy_guardrail", run_policy_guardrail_agent)

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
    graph.add_edge("input_structuring", "supervisor")

    graph.add_conditional_edges(
        "supervisor",
        _route_after_supervisor,
        {
            "reflective_support": "reflective_support",
            "distress_stabilization": "distress_stabilization",
            "behavioral_activation": "behavioral_activation",
        },
    )

    graph.add_edge("reflective_support", "response_composer")
    graph.add_edge("distress_stabilization", "response_composer")
    graph.add_edge("behavioral_activation", "response_composer")
    graph.add_edge("response_composer", "policy_guardrail")
    graph.add_edge("policy_guardrail", END)

    return graph.compile()