
from langgraph.graph import END, START, StateGraph

from retail_intelligence.agent.nodes import (
    assess_inventory_portfolio,
    prioritise_inventory_risks,
)
from retail_intelligence.agent.state import AgentState

from retail_intelligence.agent.nodes import (
    assess_inventory_portfolio,
    prioritise_inventory_risks,
    generate_ai_explanation,
)

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

    workflow.add_edge("generate_explanation", END)

    return workflow.compile()


inventory_graph = build_inventory_graph()
