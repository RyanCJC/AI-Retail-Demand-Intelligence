
import pytest
from fastapi.testclient import TestClient

from retail_intelligence.api.main import app
from retail_intelligence.inventory.risk import (
    NegativeInventoryPositionError,
)


client = TestClient(app)

VALID_REQUEST = {
    "product_id": "FOODS_1_020_WI_2_evaluation",
    "origin_day_num": 1829,
    "lead_time": 7,
    "starting_stock_ratio": 0.50,
}


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_inventory_assessment_success():
    response = client.post(
        "/api/v1/inventory/assess",
        json=VALID_REQUEST,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["inventory_position"] == 27
    assert data["order_up_to_level"] == 45
    assert data["recommended_order_quantity"] == 18
    assert data["risk_level"] == "HIGH"


def test_inventory_assessment_missing_scenario():
    request = {
        **VALID_REQUEST,
        "lead_time": 999,
    }

    response = client.post(
        "/api/v1/inventory/assess",
        json=request,
    )

    assert response.status_code == 422
    assert "No inventory snapshot" in response.json()["detail"]


def test_inventory_assessment_invalid_request():
    request = {
        **VALID_REQUEST,
        "starting_stock_ratio": 1.5,
    }

    response = client.post(
        "/api/v1/inventory/assess",
        json=request,
    )

    assert response.status_code == 422


def test_negative_inventory_returns_exception(monkeypatch):

    class MockInventoryService:

        def __init__(self, session):
            pass

        def assess_inventory(self, **kwargs):
            raise NegativeInventoryPositionError(
                "Negative inventory position requires an exception review."
            )

    monkeypatch.setattr(
        "retail_intelligence.api.main.InventoryService",
        MockInventoryService,
    )

    response = client.post(
        "/api/v1/inventory/assess",
        json=VALID_REQUEST,
    )

    assert response.status_code == 409

    data = response.json()["detail"]

    assert data["error_code"] == "NEGATIVE_INVENTORY_POSITION"
    assert data["requires_human_review"] is True
