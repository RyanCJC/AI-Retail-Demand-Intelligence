
from fastapi.testclient import TestClient

from retail_intelligence.api.main import app


client = TestClient(app)

VALID_REQUEST = {
    "origin_day_num": 1829,
    "lead_time": 7,
    "starting_stock_ratio": 0.50,
}


def test_portfolio_assessment_success():
    response = client.post(
        "/api/v1/inventory/portfolio/assess",
        json=VALID_REQUEST,
    )

    print("HTTP status:", response.status_code)
    print("Response body:", response.json())

    assert response.status_code == 200


def test_portfolio_items_are_ranked():
    response = client.post(
        "/api/v1/inventory/portfolio/assess",
        json=VALID_REQUEST,
    )

    assert response.status_code == 200

    priorities = {
        "EXCEPTION": 0,
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3,
    }

    items = response.json()["items"]
    ranks = [priorities[item["risk_level"]] for item in items]

    assert ranks == sorted(ranks)


def test_portfolio_missing_scenario():
    request = {
        **VALID_REQUEST,
        "origin_day_num": 9999,
    }

    response = client.post(
        "/api/v1/inventory/portfolio/assess",
        json=request,
    )

    assert response.status_code == 422


def test_portfolio_invalid_request():
    request = {
        **VALID_REQUEST,
        "starting_stock_ratio": 1.5,
    }

    response = client.post(
        "/api/v1/inventory/portfolio/assess",
        json=request,
    )

    assert response.status_code == 422
