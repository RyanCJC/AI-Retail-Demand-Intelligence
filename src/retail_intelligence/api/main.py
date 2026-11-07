
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from retail_intelligence.database.session import get_db
from retail_intelligence.inventory.service import InventoryService
from retail_intelligence.api.schemas import (
    InventoryAssessmentRequest,
    InventoryAssessmentResponse,
    ApprovalDecisionRequest,
    ApprovalRecordResponse,
    PendingApprovalResponse,
    InventoryExceptionResponse
)
from retail_intelligence.inventory.risk import (
    NegativeInventoryPositionError,
)

from retail_intelligence.inventory.portfolio import PortfolioService

from retail_intelligence.api.schemas import (
    PortfolioAssessmentRequest,
    PortfolioAssessmentResponse,
)

from retail_intelligence.inventory.approval import (
    ApprovalAlreadyDecidedError,
    ApprovalRecordNotFoundError,
    RecommendationNotFoundError,
    decide_recommendation,
    get_pending_approvals,
)

from retail_intelligence.agent.graph import inventory_graph

from retail_intelligence.api.schemas import (
    InventoryAgentWorkflowResponse,
)

app = FastAPI(
    title="Retail Demand Intelligence API",
    description=(
        "Inventory assessment API powered by probabilistic "
        "demand forecasts and deterministic inventory calculations."
    ),
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}



@app.post(
    "/api/v1/inventory/assess",
    response_model=InventoryAssessmentResponse,
    responses={
        409: {"model": InventoryExceptionResponse},
    },
)
def assess_inventory(
    request: InventoryAssessmentRequest,
    db: Session = Depends(get_db),
):
    service = InventoryService(db)

    try:
        result = service.assess_inventory(
            product_id=request.product_id,
            origin_day_num=request.origin_day_num,
            lead_time=request.lead_time,
            starting_stock_ratio=request.starting_stock_ratio,
        )

        return InventoryAssessmentResponse.model_validate(result)

    except NegativeInventoryPositionError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "error_code": "NEGATIVE_INVENTORY_POSITION",
                "message": str(exc),
                "requires_human_review": True,
            },
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@app.post(
    "/api/v1/inventory/portfolio/assess",
    response_model=PortfolioAssessmentResponse,
)
def assess_portfolio(
    request: PortfolioAssessmentRequest,
    db: Session = Depends(get_db),
):
    service = PortfolioService(db)

    try:
        result = service.assess_portfolio(
            origin_day_num=request.origin_day_num,
            lead_time=request.lead_time,
            starting_stock_ratio=request.starting_stock_ratio,
        )

        return PortfolioAssessmentResponse.model_validate(result)

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/v1/approvals/pending",
    response_model=list[PendingApprovalResponse],
)
def list_pending_approvals(
    db: Session = Depends(get_db),
):
    return get_pending_approvals(db)


@app.post(
    "/api/v1/approvals/{recommendation_id}/approve",
    response_model=ApprovalRecordResponse,
)
def approve_recommendation(
    recommendation_id: int,
    request: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
):
    try:
        return decide_recommendation(
            session=db,
            recommendation_id=recommendation_id,
            reviewer=request.reviewer,
            comments=request.comments,
            decision="APPROVED",
        )

    except RecommendationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    except ApprovalRecordNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    except ApprovalAlreadyDecidedError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post(
    "/api/v1/approvals/{recommendation_id}/reject",
    response_model=ApprovalRecordResponse,
)
def reject_recommendation(
    recommendation_id: int,
    request: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
):
    try:
        return decide_recommendation(
            session=db,
            recommendation_id=recommendation_id,
            reviewer=request.reviewer,
            comments=request.comments,
            decision="REJECTED",
        )

    except RecommendationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    except ApprovalRecordNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    except ApprovalAlreadyDecidedError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

@app.post(
    "/api/v1/agent/inventory/run",
    response_model=InventoryAgentWorkflowResponse,
)
def run_inventory_agent(
    request: PortfolioAssessmentRequest,
):
    try:
        result = inventory_graph.invoke({
            "origin_day_num": request.origin_day_num,
            "lead_time": request.lead_time,
            "starting_stock_ratio": request.starting_stock_ratio,
        })

        if result.get("error"):
            raise HTTPException(
                status_code=422,
                detail=result["error"],
            )

        if result.get("persistence_error"):
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Inventory recommendations could not be persisted.",
                    "persistence_error": result["persistence_error"],
                },
            )

        risk_summary = result.get("risk_summary", {})
        prioritised_items = result.get("prioritised_items", [])

        pending_count = result.get("pending_approval_count", 0)

        return {
            "origin_day_num": request.origin_day_num,
            "lead_time": request.lead_time,
            "starting_stock_ratio": request.starting_stock_ratio,
            "total_products": len(prioritised_items),
            "risk_summary": risk_summary,
            "top_priority_items": prioritised_items[:10],
            "decision_summary": result.get("decision_summary"),
            "llm_error": result.get("llm_error"),
            "persisted_recommendation_ids": (
                result.get("persisted_recommendation_ids", [])
            ),
            "pending_approval_count": pending_count,
            "skipped_recommendation_count": (
                result.get("skipped_recommendation_count", 0)
            ),
            "persistence_error": None,
            "requires_human_review": (
                pending_count > 0
                or risk_summary.get("exception", 0) > 0
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Inventory agent workflow failed: {str(exc)}",
        ) from exc