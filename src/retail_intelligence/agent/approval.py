from sqlalchemy import select, func
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from retail_intelligence.database.session import SessionLocal
from retail_intelligence.database.models import (
    ApprovalRecord,
    InventorySnapshot,
    ReplenishmentRecommendation,
)


def persist_pending_recommendations(state: dict) -> dict:
    """
    Persist eligible replenishment recommendations for human approval.

    Persistence is idempotent:
    - Existing recommendations are not duplicated.
    - Existing approval decisions are preserved.
    - Missing approval records are created as PENDING.
    - Exception items and zero-quantity recommendations are skipped.
    """

    if state.get("error"):
        return {
            "persistence_error": "Inventory assessment contains an error."
        }

    items = state.get("prioritised_items", [])

    if not items:
        return {
            "persistence_error": "No prioritised items are available."
        }

    session = SessionLocal()
    persisted_ids = set()
    skipped_count = 0

    try:
        for item in items:
            assessment = item.get("assessment")
            risk_level = item.get("risk_level")

            if not assessment or risk_level == "EXCEPTION":
                skipped_count += 1
                continue

            quantity = assessment.get("recommended_order_quantity")

            if (
                not isinstance(quantity, int)
                or isinstance(quantity, bool)
                or quantity <= 0
            ):
                skipped_count += 1
                continue

            snapshot = session.execute(
                select(InventorySnapshot).where(
                    InventorySnapshot.product_id == item["product_id"],
                    InventorySnapshot.origin_day_num == state["origin_day_num"],
                    InventorySnapshot.lead_time == state["lead_time"],
                    InventorySnapshot.starting_stock_ratio
                    == state["starting_stock_ratio"],
                )
            ).scalar_one_or_none()

            if snapshot is None:
                raise ValueError(
                    f"Inventory snapshot not found for {item['product_id']}."
                )

            recommendation_values = {
                "snapshot_id": snapshot.id,
                "inventory_position": assessment["inventory_position"],
                "order_up_to_level": assessment["order_up_to_level"],
                "recommended_order_quantity": quantity,
                "risk_level": risk_level,
                "explanation": state.get("decision_summary"),
            }

            session.execute(
                sqlite_insert(ReplenishmentRecommendation)
                .values(**recommendation_values)
                .on_conflict_do_nothing(
                    index_elements=["snapshot_id"]
                )
            )

            recommendation = session.execute(
                select(ReplenishmentRecommendation).where(
                    ReplenishmentRecommendation.snapshot_id == snapshot.id
                )
            ).scalar_one()

            persisted_ids.add(recommendation.id)

            session.execute(
                sqlite_insert(ApprovalRecord)
                .values(
                    recommendation_id=recommendation.id,
                    status="PENDING",
                )
                .on_conflict_do_nothing(
                    index_elements=["recommendation_id"]
                )
            )

        session.commit()

        pending_count = session.execute(
            select(func.count(ApprovalRecord.id)).where(
                ApprovalRecord.recommendation_id.in_(persisted_ids),
                ApprovalRecord.status == "PENDING",
            )
        ).scalar_one() if persisted_ids else 0

        return {
            "persisted_recommendation_ids": sorted(persisted_ids),
            "pending_approval_count": pending_count,
            "skipped_recommendation_count": skipped_count,
            "persistence_error": None,
        }

    except Exception as exc:
        session.rollback()

        return {
            "persisted_recommendation_ids": [],
            "pending_approval_count": 0,
            "skipped_recommendation_count": 0,
            "persistence_error": str(exc),
        }

    finally:
        session.close()