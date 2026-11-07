
from retail_intelligence.agent.nodes import generate_ai_explanation


def test_generate_ai_explanation(monkeypatch):
    def mock_explanation(assessment_context):
        assert assessment_context["total_products"] == 1
        assert len(assessment_context["top_priority_items"]) == 1
        return "The portfolio contains one high-risk product."

    monkeypatch.setattr(
        "retail_intelligence.agent.nodes.generate_decision_explanation",
        mock_explanation,
    )

    state = {
        "origin_day_num": 1829,
        "lead_time": 7,
        "starting_stock_ratio": 0.5,
        "risk_summary": {
            "high": 1,
            "medium": 0,
            "low": 0,
            "exception": 0,
        },
        "prioritised_items": [
            {
                "product_id": "SKU_HIGH",
                "risk_level": "HIGH",
                "assessment": {
                    "demand_class": "intermittent",
                    "inventory_position": 20,
                    "cumulative_p50": 30,
                    "safety_stock": 10,
                    "order_up_to_level": 40,
                    "recommended_order_quantity": 20,
                    "used_pooled_fallback": False,
                },
            }
        ],
    }

    result = generate_ai_explanation(state)

    assert result["decision_summary"] == (
        "The portfolio contains one high-risk product."
    )
    assert result["llm_error"] is None


def test_generate_ai_explanation_without_prioritised_items():
    result = generate_ai_explanation({
        "prioritised_items": [],
    })

    assert result["llm_error"] is not None
    assert "No prioritised inventory items" in result["llm_error"]
