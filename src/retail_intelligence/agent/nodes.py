
from dataclasses import asdict

from retail_intelligence.agent.state import AgentState
from retail_intelligence.database.session import SessionLocal
from retail_intelligence.inventory.portfolio import PortfolioService

from retail_intelligence.agent.llm import (
    generate_decision_explanation,
)

def assess_inventory_portfolio(state: AgentState) -> dict:
    """
    Assess the inventory portfolio using existing business logic.
    """

    required_fields = [
        "origin_day_num",
        "lead_time",
        "starting_stock_ratio",
    ]

    missing_fields = [
        field for field in required_fields
        if field not in state
    ]

    if missing_fields:
        return {
            "error": f"Missing required inputs: {missing_fields}"
        }

    session = SessionLocal()

    try:
        service = PortfolioService(session)

        result = service.assess_portfolio(
            origin_day_num=state["origin_day_num"],
            lead_time=state["lead_time"],
            starting_stock_ratio=state["starting_stock_ratio"],
        )

        portfolio_data = asdict(result)

        return {
            "portfolio_assessment": portfolio_data,
            "risk_summary": {
                "high": result.high_risk_count,
                "medium": result.medium_risk_count,
                "low": result.low_risk_count,
                "exception": result.exception_count,
            },
            "error": None,
        }

    except ValueError as exc:
        return {"error": str(exc)}

    finally:
        session.close()



def prioritise_inventory_risks(state: AgentState) -> dict:
    """
    Rank inventory assessment results by operational risk.
    """

    portfolio = state.get("portfolio_assessment")

    if not portfolio:
        return {
            "error": "Portfolio assessment is unavailable."
        }

    items = portfolio.get("items", [])

    priority_order = {
        "EXCEPTION": 0,
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3,
    }

    prioritised_items = sorted(
        items,
        key=lambda item: (
            priority_order.get(item["risk_level"], 4),
            -(
                item["assessment"]["recommended_order_quantity"]
                if item.get("assessment")
                else 0
            ),
        ),
    )

    return {
        "prioritised_items": prioritised_items,
    }


import json


def generate_ai_explanation(state: AgentState) -> dict:
    """
    Generate a business explanation from deterministic
    inventory assessment results.
    """

    if state.get("error"):
        return {
            "llm_error": "Cannot explain an unsuccessful assessment."
        }

    prioritised_items = state.get("prioritised_items", [])

    if not prioritised_items:
        return {
            "llm_error": "No prioritised inventory items are available."
        }

    # Limit detailed product information to the ten highest priorities.
    top_items = []

    for item in prioritised_items[:10]:
        assessment = item.get("assessment") or {}

        top_items.append({
            "product_id": item.get("product_id"),
            "risk_level": (
                item.get("risk_level") or item.get("risk")
            ),
            "demand_class": assessment.get("demand_class"),
            "inventory_position": assessment.get("inventory_position"),
            "cumulative_p50": assessment.get("cumulative_p50"),
            "safety_stock": assessment.get("safety_stock"),
            "order_up_to_level": assessment.get("order_up_to_level"),
            "recommended_order_quantity": (
                assessment.get("recommended_order_quantity")
            ),
            "used_pooled_fallback": (
                assessment.get("used_pooled_fallback")
            ),
            "exception_message": item.get("exception_message"),
        })

    assessment_context = {
        "scenario": {
            "origin_day_num": state.get("origin_day_num"),
            "lead_time": state.get("lead_time"),
            "starting_stock_ratio": state.get(
                "starting_stock_ratio"
            ),
        },
        "risk_summary": state.get("risk_summary", {}),
        "total_products": len(prioritised_items),
        "top_priority_items": top_items,
        "data_context": (
            "Inventory snapshots are simulated. "
            "Forecasts and inventory policies are derived "
            "from the project's development data."
        ),
    }

    try:
        explanation = generate_decision_explanation(
            assessment_context=assessment_context
        )

        return {
            "decision_summary": explanation,
            "llm_error": None,
        }

    except Exception as exc:
        return {
            "llm_error": str(exc),
        }
