from langgraph.graph import END, START, StateGraph

from retail_intelligence.agent.approval import (
    persist_pending_recommendations,
)
from retail_intelligence.agent.nodes import (
    assess_inventory_portfolio,
    generate_ai_explanation,
    prioritise_inventory_risks,
)
from retail_intelligence.agent.state import AgentState


def route_after_assessment(state: AgentState) -> str:
    if state.get("error"):
        return "end"

    return "prioritise"


def build_inventory_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node(
        "assess_inventory",
        assess_inventory_portfolio,
    )

    workflow.add_node(
        "prioritise_risks",
        prioritise_inventory_risks,
    )

    workflow.add_node(
        "generate_explanation",
        generate_ai_explanation,
    )

    workflow.add_node(
        "persist_recommendations",
        persist_pending_recommendations,
    )

    workflow.add_edge(START, "assess_inventory")

    workflow.add_conditional_edges(
        "assess_inventory",
        route_after_assessment,
        {
            "prioritise": "prioritise_risks",
            "end": END,
        },
    )

    workflow.add_edge(
        "prioritise_risks",
        "generate_explanation",
    )

    workflow.add_edge(
        "generate_explanation",
        "persist_recommendations",
    )

    workflow.add_edge(
        "persist_recommendations",
        END,
    )

    return workflow.compile()


inventory_graph = build_inventory_graph()