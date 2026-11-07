
from fastapi.testclient import TestClient

from retail_intelligence.api.main import app


client = TestClient(app)


def mock_agent_result(**overrides):
    result = {
        "origin_day_num": 1857,
        "lead_time": 7,
        "starting_stock_ratio": 0.5,
        "risk_summary": {
            "high": 1,
            "medium": 1,
            "low": 0,
            "exception": 0,
        },
        "prioritised_items": [
            {
                "product_id": "FOODS_1_001_CA_1_evaluation",
                "risk_level": "HIGH",
                "assessment": {
                    "recommended_order_quantity": 10,
                },
                "exception_message": None,
            },
            {
                "product_id": "FOODS_1_002_CA_1_evaluation",
                "risk_level": "MEDIUM",
                "assessment": {
                    "recommended_order_quantity": 5,
                },
                "exception_message": None,
            },
        ],
        "decision_summary": "Review the proposed replenishment recommendations.",
        "llm_error": None,
        "persisted_recommendation_ids": [200, 201],
        "pending_approval_count": 2,
        "skipped_recommendation_count": 0,
        "persistence_error": None,
        "error": None,
    }

    result.update(overrides)
    return result


def test_agent_inventory_run_success(monkeypatch):
    from retail_intelligence.api import main

    monkeypatch.setattr(
        main.inventory_graph,
        "invoke",
        lambda state: mock_agent_result(),
    )

    response = client.post(
        "/api/v1/agent/inventory/run",
        json={
            "origin_day_num": 1857,
            "lead_time": 7,
            "starting_stock_ratio": 0.5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_products"] == 2
    assert data["risk_summary"]["high"] == 1
    assert data["risk_summary"]["medium"] == 1
    assert data["persisted_recommendation_ids"] == [200, 201]
    assert data["pending_approval_count"] == 2
    assert data["decision_summary"] is not None
    assert data["llm_error"] is None
    assert data["requires_human_review"] is True


def test_agent_inventory_run_handles_llm_failure(monkeypatch):
    from retail_intelligence.api import main

    monkeypatch.setattr(
        main.inventory_graph,
        "invoke",
        lambda state: mock_agent_result(
            decision_summary=None,
            llm_error="Gemini service unavailable.",
        ),
    )

    response = client.post(
        "/api/v1/agent/inventory/run",
        json={
            "origin_day_num": 1857,
            "lead_time": 7,
            "starting_stock_ratio": 0.5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["llm_error"] == "Gemini service unavailable."
    assert data["persisted_recommendation_ids"] == [200, 201]
    assert data["pending_approval_count"] == 2


def test_agent_inventory_run_handles_assessment_error(monkeypatch):
    from retail_intelligence.api import main

    monkeypatch.setattr(
        main.inventory_graph,
        "invoke",
        lambda state: {
            "error": "No inventory data found for the requested scenario."
        },
    )

    response = client.post(
        "/api/v1/agent/inventory/run",
        json={
            "origin_day_num": 1857,
            "lead_time": 7,
            "starting_stock_ratio": 0.5,
        },
    )

    assert response.status_code == 422


def test_agent_inventory_run_handles_persistence_error(monkeypatch):
    from retail_intelligence.api import main

    monkeypatch.setattr(
        main.inventory_graph,
        "invoke",
        lambda state: mock_agent_result(
            persistence_error="Database write failed."
        ),
    )

    response = client.post(
        "/api/v1/agent/inventory/run",
        json={
            "origin_day_num": 1857,
            "lead_time": 7,
            "starting_stock_ratio": 0.5,
        },
    )

    assert response.status_code == 500
