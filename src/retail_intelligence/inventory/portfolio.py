
from dataclasses import dataclass

from sqlalchemy.orm import Session

from retail_intelligence.inventory.repository import InventoryRepository
from retail_intelligence.inventory.service import (
    InventoryAssessment,
    InventoryService,
)
from retail_intelligence.inventory.risk import (
    NegativeInventoryPositionError,
)


@dataclass(frozen=True)
class PortfolioItem:
    product_id: str
    risk_level: str
    assessment: InventoryAssessment | None
    exception_message: str | None


@dataclass(frozen=True)
class PortfolioAssessment:
    origin_day_num: int
    lead_time: int
    starting_stock_ratio: float
    total_products: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    exception_count: int
    items: list[PortfolioItem]


class PortfolioService:

    def __init__(self, session: Session):
        self.session = session
        self.repository = InventoryRepository(session)
        self.inventory_service = InventoryService(session)

    def assess_portfolio(
        self,
        origin_day_num: int,
        lead_time: int,
        starting_stock_ratio: float,
    ) -> PortfolioAssessment:

        product_ids = self.repository.get_portfolio_product_ids(
            origin_day_num=origin_day_num,
            lead_time=lead_time,
            starting_stock_ratio=starting_stock_ratio,
        )

        if not product_ids:
            raise ValueError(
                "No inventory snapshots found for the requested portfolio scenario."
            )

        items = []

        for product_id in product_ids:
            try:
                assessment = self.inventory_service.assess_inventory(
                    product_id=product_id,
                    origin_day_num=origin_day_num,
                    lead_time=lead_time,
                    starting_stock_ratio=starting_stock_ratio,
                )

                items.append(
                    PortfolioItem(
                        product_id=product_id,
                        risk_level=assessment.risk_level,
                        assessment=assessment,
                        exception_message=None,
                    )
                )

            except NegativeInventoryPositionError as exc:
                items.append(
                    PortfolioItem(
                        product_id=product_id,
                        risk_level="EXCEPTION",
                        assessment=None,
                        exception_message=str(exc),
                    )
                )

            except ValueError as exc:
                items.append(
                    PortfolioItem(
                        product_id=product_id,
                        risk_level="EXCEPTION",
                        assessment=None,
                        exception_message=str(exc),
                    )
                )

        priority = {
            "EXCEPTION": 0,
            "HIGH": 1,
            "MEDIUM": 2,
            "LOW": 3,
        }

        items.sort(
            key=lambda item: (
                priority[item.risk_level],
                item.product_id,
            )
        )

        return PortfolioAssessment(
            origin_day_num=origin_day_num,
            lead_time=lead_time,
            starting_stock_ratio=starting_stock_ratio,
            total_products=len(items),
            high_risk_count=sum(
                item.risk_level == "HIGH" for item in items
            ),
            medium_risk_count=sum(
                item.risk_level == "MEDIUM" for item in items
            ),
            low_risk_count=sum(
                item.risk_level == "LOW" for item in items
            ),
            exception_count=sum(
                item.risk_level == "EXCEPTION" for item in items
            ),
            items=items,
        )
