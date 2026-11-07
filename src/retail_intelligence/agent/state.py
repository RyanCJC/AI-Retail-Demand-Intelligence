
from typing import Any, Literal, TypedDict


class AgentState(TypedDict, total=False):
    # User request
    origin_day_num: int
    lead_time: int
    starting_stock_ratio: float

    # Inventory assessment
    portfolio_assessment: dict[str, Any]

    # Risk analysis and prioritisation
    prioritised_items: list[dict[str, Any]]
    risk_summary: dict[str, int]

    # AI-generated explanation
    decision_summary: str
    recommendation_explanations: list[dict[str, Any]]

    # Human approval
    approval_status: Literal["PENDING", "APPROVED", "REJECTED"]
    reviewer: str
    approval_comments: str | None

    # Workflow status
    requires_human_review: bool
    error: str | None

    # Error handling
    llm_error: str | None

    # Persistence results
    persisted_recommendation_ids: list[int]
    pending_approval_count: int
    skipped_recommendation_count: int
    persistence_error: str | None
