
from dataclasses import dataclass


@dataclass(frozen=True)
class InventoryRisk:
    risk_level: str
    inventory_position: int
    cumulative_p50: float
    order_up_to_level: int
    risk_reason: str



class NegativeInventoryPositionError(ValueError):
    """Raised when inventory position requires operational review."""
    pass


def classify_inventory_risk(
    inventory_position: int,
    cumulative_p50: float,
    order_up_to_level: int,
) -> InventoryRisk:

    if isinstance(inventory_position, bool) or not isinstance(
        inventory_position, int
    ):
        raise TypeError("inventory_position must be an integer.")

    if inventory_position < 0:
        raise NegativeInventoryPositionError(
            "Negative inventory position requires an exception review."
        )

    if cumulative_p50 < 0:
        raise ValueError("cumulative_p50 cannot be negative.")

    if order_up_to_level < 0:
        raise ValueError("order_up_to_level cannot be negative.")

    if cumulative_p50 > order_up_to_level:
        raise ValueError(
            "Cumulative P50 cannot exceed the order-up-to level."
        )

    if inventory_position < cumulative_p50:
        risk_level = "HIGH"
        reason = (
            "Inventory position is below forecast median demand "
            "over the protection period."
        )

    elif inventory_position < order_up_to_level:
        risk_level = "MEDIUM"
        reason = (
            "Inventory position covers forecast median demand "
            "but is below the order-up-to target."
        )

    else:
        risk_level = "LOW"
        reason = (
            "Inventory position meets or exceeds the order-up-to target."
        )

    return InventoryRisk(
        risk_level=risk_level,
        inventory_position=inventory_position,
        cumulative_p50=cumulative_p50,
        order_up_to_level=order_up_to_level,
        risk_reason=reason,
    )
