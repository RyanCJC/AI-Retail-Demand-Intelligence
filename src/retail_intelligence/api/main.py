
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from retail_intelligence.database.session import get_db
from retail_intelligence.inventory.service import InventoryService
from retail_intelligence.api.schemas import (
    InventoryAssessmentRequest,
    InventoryAssessmentResponse,
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
