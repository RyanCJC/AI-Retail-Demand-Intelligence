
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from retail_intelligence.database.models import (
    DemandForecast,
    InventoryPolicy,
    InventorySnapshot,
    Product,
)


@dataclass(frozen=True)
class InventoryContext:
    product_id: str
    demand_class: str
    origin_day_num: int
    lead_time: int
    review_period: int
    protection_period: int
    starting_stock_ratio: float

    on_hand: int
    on_order: int
    backorders: int
    inventory_position: int

    cumulative_p50: float
    safety_stock: float
    order_up_to_level: int
    used_pooled_fallback: bool


class InventoryRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_inventory_context(
        self,
        product_id: str,
        origin_day_num: int,
        lead_time: int,
        starting_stock_ratio: float,
    ) -> InventoryContext:

        snapshot_statement = select(InventorySnapshot).where(
            InventorySnapshot.product_id == product_id,
            InventorySnapshot.origin_day_num == origin_day_num,
            InventorySnapshot.lead_time == lead_time,
            InventorySnapshot.starting_stock_ratio == starting_stock_ratio,
        )

        snapshot = self.session.execute(
            snapshot_statement
        ).scalar_one_or_none()

        if snapshot is None:
            raise ValueError(
                "No inventory snapshot matches the requested SKU and scenario."
            )

        protection_period = snapshot.protection_period
        review_period = snapshot.review_period

        product = self.session.get(Product, product_id)

        if product is None:
            raise ValueError(f"Product '{product_id}' does not exist.")

        policy_statement = select(InventoryPolicy).where(
            InventoryPolicy.product_id == product_id,
            InventoryPolicy.origin_day_num == origin_day_num,
            InventoryPolicy.lead_time == lead_time,
            InventoryPolicy.protection_period == protection_period,
        )

        policy = self.session.execute(
            policy_statement
        ).scalar_one_or_none()

        if policy is None:
            raise ValueError(
                "No inventory policy matches the requested SKU and scenario."
            )

        forecast_statement = select(
            func.count(DemandForecast.id),
            func.sum(DemandForecast.p50),
            func.min(DemandForecast.horizon),
            func.max(DemandForecast.horizon),
        ).where(
            DemandForecast.product_id == product_id,
            DemandForecast.origin_day_num == origin_day_num,
            DemandForecast.horizon <= protection_period,
        )

        forecast_result = self.session.execute(
            forecast_statement
        ).one()

        forecast_count, cumulative_p50, min_horizon, max_horizon = forecast_result

        if (
            forecast_count != protection_period
            or min_horizon != 1
            or max_horizon != protection_period
            or cumulative_p50 is None
        ):
            raise ValueError(
                "Insufficient or incomplete forecast data for the protection period."
            )

        expected_inventory_position = (
            snapshot.on_hand
            + snapshot.on_order
            - snapshot.backorders
        )

        if snapshot.inventory_position != expected_inventory_position:
            raise ValueError(
                "Stored inventory position does not match its component quantities."
            )

        return InventoryContext(
            product_id=product_id,
            demand_class=product.demand_class,
            origin_day_num=origin_day_num,
            lead_time=lead_time,
            review_period=review_period,
            protection_period=protection_period,
            starting_stock_ratio=starting_stock_ratio,
            on_hand=snapshot.on_hand,
            on_order=snapshot.on_order,
            backorders=snapshot.backorders,
            inventory_position=snapshot.inventory_position,
            cumulative_p50=float(cumulative_p50),
            safety_stock=float(policy.safety_stock),
            order_up_to_level=policy.order_up_to_level,
            used_pooled_fallback=policy.used_pooled_fallback,
        )
