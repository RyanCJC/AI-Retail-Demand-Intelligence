
from retail_intelligence.agent.graph import inventory_graph


def test_inventory_graph_success(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    result = inventory_graph.invoke({
        "origin_day_num": 1829,
        "lead_time": 7,
        "starting_stock_ratio": 0.5,
    })

    assert result.get("error") is None
    assert result["portfolio_assessment"]["total_products"] == 200
    assert len(result["prioritised_items"]) == 200
    assert result["llm_error"] is not None


def test_inventory_graph_missing_input():
    result = inventory_graph.invoke({
        "origin_day_num": 1829,
        "lead_time": 7,
    })

    assert "starting_stock_ratio" in result["error"]
    assert "prioritised_items" not in result
