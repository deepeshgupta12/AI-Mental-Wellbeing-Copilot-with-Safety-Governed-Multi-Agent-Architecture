from __future__ import annotations

from langgraph.graph import END, StateGraph

from mental_wellbeing_api.agents.input_structuring_agent import run_input_structuring_agent
from mental_wellbeing_api.agents.reflective_agent import run_reflective_agent
from mental_wellbeing_api.agents.response_composer_agent import run_response_composer_agent
from mental_wellbeing_api.agents.safety_triage_agent import run_safety_triage_agent
from mental_wellbeing_api.orchestration.state import AgentRuntimeState


def _route_after_safety(state: AgentRuntimeState) -> str:
    if state.get("safety_override"):
        return "response_composer"
    return "input_structuring"


def build_agent_runtime_graph():
    graph = StateGraph(AgentRuntimeState)

    graph.add_node("safety_triage", run_safety_triage_agent)
    graph.add_node("input_structuring", run_input_structuring_agent)
    graph.add_node("reflective_support", run_reflective_agent)
    graph.add_node("response_composer", run_response_composer_agent)

    graph.set_entry_point("safety_triage")
    graph.add_conditional_edges(
        "safety_triage",
        _route_after_safety,
        {
            "input_structuring": "input_structuring",
            "response_composer": "response_composer",
        },
    )
    graph.add_edge("input_structuring", "reflective_support")
    graph.add_edge("reflective_support", "response_composer")
    graph.add_edge("response_composer", END)

    return graph.compile()