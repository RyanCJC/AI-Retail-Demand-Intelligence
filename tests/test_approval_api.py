
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from retail_intelligence.api.main import app
from retail_intelligence.database.base import Base
from retail_intelligence.database.session import get_db
from retail_intelligence.database.models import (
    ApprovalRecord,
    InventorySnapshot,
    Product,
    ReplenishmentRecommendation,
)


@pytest.fixture
def approval_environment(tmp_path):
    database_path = tmp_path / "test_approvals.db"

    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    with TestingSessionLocal() as db:
        for number in range(1, 4):
            product = Product(
                id=f"TEST_PRODUCT_{number}",
                demand_class="intermittent",
            )
            db.add(product)
            db.flush()

            snapshot = InventorySnapshot(
                product_id=product.id,
                origin_day_num=1829,
                lead_time=7,
                review_period=7,
                protection_period=14,
                starting_stock_ratio=0.5,
                on_hand=20,
                on_order=5,
                backorders=0,
                inventory_position=25,
                simulation_seed=42,
            )
            db.add(snapshot)
            db.flush()

            recommendation = ReplenishmentRecommendation(
                snapshot_id=snapshot.id,
                inventory_position=25,
                order_up_to_level=40,
                recommended_order_quantity=15,
                risk_level="HIGH",
                explanation="Test recommendation.",
            )
            db.add(recommendation)
            db.flush()

            # Third recommendation deliberately has no approval record.
            if number != 3:
                db.add(
                    ApprovalRecord(
                        recommendation_id=recommendation.id,
                        status="PENDING",
                    )
                )

        db.commit()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client, TestingSessionLocal

    app.dependency_overrides.pop(get_db, None)
    engine.dispose()


def test_list_pending_approvals(approval_environment):
    client, _ = approval_environment

    response = client.get("/api/v1/approvals/pending")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert all(item["approval"]["status"] == "PENDING" for item in data)


def test_approve_recommendation(approval_environment):
    client, session_factory = approval_environment

    response = client.post(
        "/api/v1/approvals/1/approve",
        json={
            "reviewer": "Test Reviewer",
            "comments": "Approved for testing.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["recommendation_id"] == 1
    assert data["status"] == "APPROVED"
    assert data["reviewer"] == "Test Reviewer"
    assert data["comments"] == "Approved for testing."
    assert data["decided_at"] is not None

    with session_factory() as db:
        record = db.query(ApprovalRecord).filter_by(
            recommendation_id=1
        ).one()

        assert record.status == "APPROVED"


def test_reject_recommendation(approval_environment):
    client, session_factory = approval_environment

    response = client.post(
        "/api/v1/approvals/2/reject",
        json={
            "reviewer": "Test Reviewer",
            "comments": "Insufficient stock justification.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "REJECTED"
    assert data["reviewer"] == "Test Reviewer"
    assert data["decided_at"] is not None

    with session_factory() as db:
        record = db.query(ApprovalRecord).filter_by(
            recommendation_id=2
        ).one()

        assert record.status == "REJECTED"


def test_cannot_approve_already_approved_recommendation(
    approval_environment,
):
    client, _ = approval_environment

    payload = {"reviewer": "Test Reviewer"}

    first_response = client.post(
        "/api/v1/approvals/1/approve",
        json=payload,
    )

    second_response = client.post(
        "/api/v1/approvals/1/approve",
        json=payload,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 409


def test_cannot_reject_already_rejected_recommendation(
    approval_environment,
):
    client, _ = approval_environment

    payload = {"reviewer": "Test Reviewer"}

    first_response = client.post(
        "/api/v1/approvals/2/reject",
        json=payload,
    )

    second_response = client.post(
        "/api/v1/approvals/2/reject",
        json=payload,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 409


def test_nonexistent_recommendation_returns_404(
    approval_environment,
):
    client, _ = approval_environment

    response = client.post(
        "/api/v1/approvals/9999/approve",
        json={"reviewer": "Test Reviewer"},
    )

    assert response.status_code == 404


def test_missing_approval_record_returns_404(
    approval_environment,
):
    client, _ = approval_environment

    response = client.post(
        "/api/v1/approvals/3/approve",
        json={"reviewer": "Test Reviewer"},
    )

    assert response.status_code == 404


def test_empty_reviewer_returns_422(approval_environment):
    client, _ = approval_environment

    response = client.post(
        "/api/v1/approvals/1/approve",
        json={"reviewer": ""},
    )

    assert response.status_code == 422


def test_whitespace_reviewer_returns_422(approval_environment):
    client, _ = approval_environment

    response = client.post(
        "/api/v1/approvals/1/approve",
        json={"reviewer": "   "},
    )

    assert response.status_code == 422
