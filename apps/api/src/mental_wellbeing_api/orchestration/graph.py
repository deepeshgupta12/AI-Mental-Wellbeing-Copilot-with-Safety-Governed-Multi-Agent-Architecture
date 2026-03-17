from __future__ import annotations

from langgraph.graph import END, StateGraph

from mental_wellbeing_api.agents.input_structuring_agent import run_input_structuring_agent
from mental_wellbeing_api.agents.reflective_agent import run_reflective_agent
from mental_wellbeing_api.agents.response_composer_agent import run_response_composer_agent
from mental_wellbeing_api.orchestration.state import AgentRuntimeState


def build_agent_runtime_graph():
    graph = StateGraph(AgentRuntimeState)

    graph.add_node("input_structuring", run_input_structuring_agent)
    graph.add_node("reflective_support", run_reflective_agent)
    graph.add_node("response_composer", run_response_composer_agent)

    graph.set_entry_point("input_structuring")
    graph.add_edge("input_structuring", "reflective_support")
    graph.add_edge("reflective_support", "response_composer")
    graph.add_edge("response_composer", END)

    return graph.compile()