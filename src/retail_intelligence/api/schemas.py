
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class InventoryAssessmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_id: str = Field(min_length=1)
    origin_day_num: int = Field(gt=0)
    lead_time: int = Field(gt=0)
    starting_stock_ratio: float = Field(gt=0, le=1)


class InventoryAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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

    risk_level: Literal["HIGH", "MEDIUM", "LOW"]
    risk_reason: str

    used_pooled_fallback: bool
