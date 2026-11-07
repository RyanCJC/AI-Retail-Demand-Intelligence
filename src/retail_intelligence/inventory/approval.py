from datetime import datetime, timezone

from sqlalchemy import case, select, update
from sqlalchemy.orm import Session

from retail_intelligence.database.models import (
    ApprovalRecord,
    InventorySnapshot,
    ReplenishmentRecommendation,
)


class RecommendationNotFoundError(Exception):
    pass


class ApprovalRecordNotFoundError(Exception):
    pass


class ApprovalAlreadyDecidedError(Exception):
    pass


def get_pending_approvals(session: Session) -> list[dict]:
    """Retrieve pending recommendations with their inventory context."""

    risk_priority = case(
        (ReplenishmentRecommendation.risk_level == "HIGH", 1),
        (ReplenishmentRecommendation.risk_level == "MEDIUM", 2),
        (ReplenishmentRecommendation.risk_level == "LOW", 3),
        else_=4,
    )

    results = session.execute(
        select(
            ApprovalRecord,
            ReplenishmentRecommendation,
            InventorySnapshot,
        )
        .join(
            ReplenishmentRecommendation,
            ApprovalRecord.recommendation_id
            == ReplenishmentRecommendation.id,
        )
        .join(
            InventorySnapshot,
            ReplenishmentRecommendation.snapshot_id
            == InventorySnapshot.id,
        )
        .where(ApprovalRecord.status == "PENDING")
        .order_by(
            risk_priority,
            ReplenishmentRecommendation.recommended_order_quantity.desc(),
        )
    ).all()

    return [
        {
            "recommendation_id": recommendation.id,
            "product_id": snapshot.product_id,
            "origin_day_num": snapshot.origin_day_num,
            "lead_time": snapshot.lead_time,
            "starting_stock_ratio": snapshot.starting_stock_ratio,
            "inventory_position": recommendation.inventory_position,
            "order_up_to_level": recommendation.order_up_to_level,
            "recommended_order_quantity": (
                recommendation.recommended_order_quantity
            ),
            "risk_level": recommendation.risk_level,
            "explanation": recommendation.explanation,
            "approval": approval,
        }
        for approval, recommendation, snapshot in results
    ]


def decide_recommendation(
    session: Session,
    recommendation_id: int,
    reviewer: str,
    comments: str | None,
    decision: str,
) -> ApprovalRecord:
    """
    Approve or reject a pending recommendation.

    The conditional UPDATE prevents multiple reviewers from deciding
    the same recommendation concurrently.
    """

    if decision not in {"APPROVED", "REJECTED"}:
        raise ValueError("Decision must be APPROVED or REJECTED.")

    reviewer = reviewer.strip()

    if not reviewer:
        raise ValueError("Reviewer cannot be empty.")

    if comments is not None:
        comments = comments.strip() or None

    try:
        result = session.execute(
            update(ApprovalRecord)
            .where(
                ApprovalRecord.recommendation_id == recommendation_id,
                ApprovalRecord.status == "PENDING",
            )
            .values(
                status=decision,
                reviewer=reviewer,
                comments=comments,
                decided_at=datetime.now(timezone.utc),
            )
            .execution_options(synchronize_session=False)
        )

        if result.rowcount == 0:
            approval = session.execute(
                select(ApprovalRecord).where(
                    ApprovalRecord.recommendation_id == recommendation_id
                )
            ).scalar_one_or_none()

            if approval is not None:
                raise ApprovalAlreadyDecidedError(
                    f"Recommendation {recommendation_id} "
                    f"has already been decided."
                )

            recommendation = session.get(
                ReplenishmentRecommendation,
                recommendation_id,
            )

            if recommendation is None:
                raise RecommendationNotFoundError(
                    f"Recommendation {recommendation_id} was not found."
                )

            raise ApprovalRecordNotFoundError(
                f"No approval record exists for recommendation "
                f"{recommendation_id}."
            )

        session.commit()

        return session.execute(
            select(ApprovalRecord)
            .where(
                ApprovalRecord.recommendation_id == recommendation_id
            )
            .execution_options(populate_existing=True)
        ).scalar_one()

    except Exception:
        session.rollback()
        raise