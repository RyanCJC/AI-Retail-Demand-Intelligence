
from typing import Any, Literal
from datetime import datetime, timezone
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

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



class InventoryExceptionResponse(BaseModel):
    error_code: Literal["NEGATIVE_INVENTORY_POSITION"]
    message: str
    requires_human_review: bool = True


class PortfolioAssessmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    origin_day_num: int = Field(gt=0)
    lead_time: int = Field(gt=0)
    starting_stock_ratio: float = Field(gt=0, le=1)



class PortfolioItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: str
    risk_level: Literal["EXCEPTION", "HIGH", "MEDIUM", "LOW"]
    assessment: InventoryAssessmentResponse | None
    exception_message: str | None


class PortfolioAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    origin_day_num: int
    lead_time: int
    starting_stock_ratio: float

    total_products: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    exception_count: int

    items: list[PortfolioItemResponse]

class ApprovalDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reviewer: str = Field(min_length=1, max_length=100)
    comments: str | None = Field(default=None, max_length=1000)

    @field_validator("reviewer")
    @classmethod
    def validate_reviewer(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Reviewer cannot be empty.")

        return value

class ApprovalRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recommendation_id: int
    status: Literal["PENDING", "APPROVED", "REJECTED"]
    reviewer: str | None
    comments: str | None
    created_at: datetime
    decided_at: datetime | None


class PendingApprovalResponse(BaseModel):
    recommendation_id: int
    product_id: str
    origin_day_num: int
    lead_time: int
    starting_stock_ratio: float
    inventory_position: int
    order_up_to_level: int
    recommended_order_quantity: int
    risk_level: Literal["HIGH", "MEDIUM", "LOW"]
    explanation: str | None
    approval: ApprovalRecordResponse


class InventoryAgentWorkflowResponse(BaseModel):
    origin_day_num: int
    lead_time: int
    starting_stock_ratio: float

    total_products: int
    risk_summary: dict[str, int]

    top_priority_items: list[dict[str, Any]]

    decision_summary: str | None
    llm_error: str | None

    persisted_recommendation_ids: list[int]
    pending_approval_count: int
    skipped_recommendation_count: int
    persistence_error: str | None

    requires_human_review: bool