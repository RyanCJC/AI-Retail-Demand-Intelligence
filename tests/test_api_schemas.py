
import pytest
from pydantic import ValidationError

from retail_intelligence.api.schemas import (
    InventoryAssessmentRequest,
    InventoryAssessmentResponse,
)


def test_valid_inventory_request():
    request = InventoryAssessmentRequest(
        product_id="FOODS_1_020_WI_2_evaluation",
        origin_day_num=1829,
        lead_time=7,
        starting_stock_ratio=0.50,
    )

    assert request.lead_time == 7
    assert request.starting_stock_ratio == 0.50


def test_reject_invalid_stock_ratio():
    with pytest.raises(ValidationError):
        InventoryAssessmentRequest(
            product_id="FOODS_1_020_WI_2_evaluation",
            origin_day_num=1829,
            lead_time=7,
            starting_stock_ratio=1.5,
        )


def test_reject_unexpected_request_field():
    with pytest.raises(ValidationError):
        InventoryAssessmentRequest(
            product_id="FOODS_1_020_WI_2_evaluation",
            origin_day_num=1829,
            lead_time=7,
            starting_stock_ratio=0.50,
            inventory_position=100,
        )


def test_valid_inventory_response():
    response = InventoryAssessmentResponse(
        product_id="FOODS_1_020_WI_2_evaluation",
        demand_class="intermittent",
        origin_day_num=1829,
        lead_time=7,
        review_period=7,
        protection_period=14,
        on_hand=23,
        on_order=6,
        backorders=2,
        inventory_position=27,
        cumulative_p50=32.59,
        safety_stock=12.01,
        order_up_to_level=45,
        recommended_order_quantity=18,
        risk_level="HIGH",
        risk_reason="Inventory position is below forecast median demand.",
        used_pooled_fallback=False,
    )

    assert response.recommended_order_quantity == 18


def test_reject_invalid_risk_level():
    with pytest.raises(ValidationError):
        InventoryAssessmentResponse(
            product_id="SKU001",
            demand_class="intermittent",
            origin_day_num=1829,
            lead_time=7,
            review_period=7,
            protection_period=14,
            on_hand=23,
            on_order=6,
            backorders=2,
            inventory_position=27,
            cumulative_p50=32.59,
            safety_stock=12.01,
            order_up_to_level=45,
            recommended_order_quantity=18,
            risk_level="CRITICAL",
            risk_reason="Test",
            used_pooled_fallback=False,
        )
