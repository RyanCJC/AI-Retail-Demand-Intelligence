
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from retail_intelligence.database.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    demand_class: Mapped[str] = mapped_column(String, nullable=False)

    forecasts = relationship("DemandForecast", back_populates="product")
    inventory_snapshots = relationship(
        "InventorySnapshot", back_populates="product"
    )


class DemandForecast(Base):
    __tablename__ = "demand_forecasts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id"), nullable=False
    )
    origin_day_num: Mapped[int] = mapped_column(Integer, nullable=False)
    target_day_num: Mapped[int] = mapped_column(Integer, nullable=False)
    horizon: Mapped[int] = mapped_column(Integer, nullable=False)

    p10: Mapped[float] = mapped_column(Float, nullable=False)
    p50: Mapped[float] = mapped_column(Float, nullable=False)
    p90: Mapped[float] = mapped_column(Float, nullable=False)

    product = relationship("Product", back_populates="forecasts")

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "origin_day_num",
            "target_day_num",
            name="uq_forecast_product_origin_target",
        ),
    )


class InventorySnapshot(Base):
    __tablename__ = "inventory_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id"), nullable=False
    )

    origin_day_num: Mapped[int] = mapped_column(Integer, nullable=False)
    lead_time: Mapped[int] = mapped_column(Integer, nullable=False)
    review_period: Mapped[int] = mapped_column(Integer, nullable=False)
    protection_period: Mapped[int] = mapped_column(Integer, nullable=False)

    starting_stock_ratio: Mapped[float] = mapped_column(
        Float, nullable=False
    )
    on_hand: Mapped[int] = mapped_column(Integer, nullable=False)
    on_order: Mapped[int] = mapped_column(Integer, nullable=False)
    backorders: Mapped[int] = mapped_column(Integer, nullable=False)
    inventory_position: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    simulation_seed: Mapped[int] = mapped_column(Integer, nullable=False)

    product = relationship("Product", back_populates="inventory_snapshots")

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "origin_day_num",
            "lead_time",
            "starting_stock_ratio",
            name="uq_inventory_scenario",
        ),
    )


class InventoryPolicy(Base):
    __tablename__ = "inventory_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id"), nullable=False
    )

    lead_time: Mapped[int] = mapped_column(Integer, nullable=False)
    review_period: Mapped[int] = mapped_column(Integer, nullable=False)
    protection_period: Mapped[int] = mapped_column(Integer, nullable=False)

    safety_stock: Mapped[float] = mapped_column(Float, nullable=False)
    order_up_to_level: Mapped[int] = mapped_column(Integer, nullable=False)
    used_pooled_fallback: Mapped[bool] = mapped_column(
        Boolean, nullable=False
    )

    origin_day_num: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "origin_day_num",
            "protection_period",
            name="uq_inventory_policy",
        ),
    )


class ReplenishmentRecommendation(Base):
    __tablename__ = "replenishment_recommendations"

    __table_args__ = (
        Index(
            "uq_replenishment_recommendations_snapshot_id",
            "snapshot_id",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    snapshot_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_snapshots.id"), nullable=False
    )

    inventory_position: Mapped[int] = mapped_column(Integer, nullable=False)
    order_up_to_level: Mapped[int] = mapped_column(Integer, nullable=False)
    recommended_order_quantity: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    risk_level: Mapped[str] = mapped_column(String, nullable=False)

    explanation: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )


class ApprovalRecord(Base):
    __tablename__ = "approval_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recommendation_id: Mapped[int] = mapped_column(
        ForeignKey("replenishment_recommendations.id"),
        nullable=False,
        unique=True,
    )

    status: Mapped[str] = mapped_column(String, nullable=False)
    reviewer: Mapped[str | None] = mapped_column(String, nullable=True)
    comments: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
