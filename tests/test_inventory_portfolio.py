
from retail_intelligence.database.session import SessionLocal
from retail_intelligence.inventory.portfolio import PortfolioService


def test_portfolio_assessment():

    with SessionLocal() as session:
        service = PortfolioService(session)

        result = service.assess_portfolio(
            origin_day_num=1829,
            lead_time=7,
            starting_stock_ratio=0.50,
        )

    assert result.total_products == 200

    assert (
        result.high_risk_count
        + result.medium_risk_count
        + result.low_risk_count
        + result.exception_count
        == result.total_products
    )

    assert len(result.items) == result.total_products

    priorities = {
        "EXCEPTION": 0,
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3,
    }

    ranks = [priorities[item.risk_level] for item in result.items]

    assert ranks == sorted(ranks)


def test_portfolio_rejects_missing_scenario():

    import pytest

    with SessionLocal() as session:
        service = PortfolioService(session)

        with pytest.raises(ValueError, match="No inventory snapshots"):
            service.assess_portfolio(
                origin_day_num=9999,
                lead_time=7,
                starting_stock_ratio=0.50,
            )
