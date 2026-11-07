
from dataclasses import dataclass

from sqlalchemy.orm import Session

from retail_intelligence.inventory.calculations import (
    calculate_replenishment,
)
from retail_intelligence.inventory.repository import InventoryRepository
from retail_intelligence.inventory.risk import classify_inventory_risk


@dataclass(frozen=True)
class InventoryAssessment:
    product_id: str
    demand_class: str
    origin_day_num: int
    lead_time: int
    review_period: int
    protection_period: int

    on_hand: int
    on_order: int
    backorders: int
    inventory_position: int

    cumulative_p50: float
    safety_stock: float
    order_up_to_level: int
    recommended_order_quantity: int

    risk_level: str
    risk_reason: str
    used_pooled_fallback: bool


class InventoryService:

    def __init__(self, session: Session):
        self.repository = InventoryRepository(session)

    def assess_inventory(
        self,
        product_id: str,
        origin_day_num: int,
        lead_time: int,
        starting_stock_ratio: float,
    ) -> InventoryAssessment:

        context = self.repository.get_inventory_context(
            product_id=product_id,
            origin_day_num=origin_day_num,
            lead_time=lead_time,
            starting_stock_ratio=starting_stock_ratio,
        )

        calculation = calculate_replenishment(
            on_hand=context.on_hand,
            on_order=context.on_order,
            backorders=context.backorders,
            order_up_to_level=context.order_up_to_level,
        )

        risk = classify_inventory_risk(
            inventory_position=calculation.inventory_position,
            cumulative_p50=context.cumulative_p50,
            order_up_to_level=context.order_up_to_level,
        )

        return InventoryAssessment(
            product_id=context.product_id,
            demand_class=context.demand_class,
            origin_day_num=context.origin_day_num,
            lead_time=context.lead_time,
            review_period=context.review_period,
            protection_period=context.protection_period,
            on_hand=calculation.on_hand,
            on_order=calculation.on_order,
            backorders=calculation.backorders,
            inventory_position=calculation.inventory_position,
            cumulative_p50=context.cumulative_p50,
            safety_stock=context.safety_stock,
            order_up_to_level=context.order_up_to_level,
            recommended_order_quantity=calculation.recommended_order_quantity,
            risk_level=risk.risk_level,
            risk_reason=risk.risk_reason,
            used_pooled_fallback=context.used_pooled_fallback,
        )
