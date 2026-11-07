
import pytest

from retail_intelligence.database.session import SessionLocal
from retail_intelligence.inventory.repository import InventoryRepository
from retail_intelligence.inventory.service import InventoryService


PRODUCT_ID = "FOODS_1_020_WI_2_evaluation"
ORIGIN_DAY = 1829
LEAD_TIME = 7
STOCK_RATIO = 0.50


def test_repository_retrieves_inventory_context():
    with SessionLocal() as session:
        repository = InventoryRepository(session)

        context = repository.get_inventory_context(
            product_id=PRODUCT_ID,
            origin_day_num=ORIGIN_DAY,
            lead_time=LEAD_TIME,
            starting_stock_ratio=STOCK_RATIO,
        )

    assert context.product_id == PRODUCT_ID
    assert context.demand_class == "intermittent"
    assert context.protection_period == 14
    assert context.inventory_position == 27
    assert context.cumulative_p50 == pytest.approx(32.5900769234)
    assert context.safety_stock == pytest.approx(12.0093392804)
    assert context.order_up_to_level == 45
    assert context.used_pooled_fallback is False


def test_repository_rejects_missing_snapshot():
    with SessionLocal() as session:
        repository = InventoryRepository(session)

        with pytest.raises(ValueError, match="No inventory snapshot"):
            repository.get_inventory_context(
                product_id=PRODUCT_ID,
                origin_day_num=ORIGIN_DAY,
                lead_time=999,
                starting_stock_ratio=STOCK_RATIO,
            )


def test_service_generates_correct_recommendation():
    with SessionLocal() as session:
        service = InventoryService(session)

        result = service.assess_inventory(
            product_id=PRODUCT_ID,
            origin_day_num=ORIGIN_DAY,
            lead_time=LEAD_TIME,
            starting_stock_ratio=STOCK_RATIO,
        )

    assert result.inventory_position == 27
    assert result.order_up_to_level == 45
    assert result.recommended_order_quantity == 18
    assert result.risk_level == "HIGH"


def test_service_rejects_missing_scenario():
    with SessionLocal() as session:
        service = InventoryService(session)

        with pytest.raises(ValueError, match="No inventory snapshot"):
            service.assess_inventory(
                product_id=PRODUCT_ID,
                origin_day_num=ORIGIN_DAY,
                lead_time=999,
                starting_stock_ratio=STOCK_RATIO,
            )
