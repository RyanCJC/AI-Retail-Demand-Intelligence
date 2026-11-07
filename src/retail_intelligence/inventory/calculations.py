
from dataclasses import dataclass
from math import ceil


@dataclass(frozen=True)
class InventoryCalculation:
    on_hand: int
    on_order: int
    backorders: int
    inventory_position: int
    order_up_to_level: int
    recommended_order_quantity: int


def calculate_inventory_position(
    on_hand: int,
    on_order: int,
    backorders: int,
) -> int:
    """
    Calculate inventory position.

    Inventory position = on-hand + on-order - backorders.
    """

    quantities = {
        "on_hand": on_hand,
        "on_order": on_order,
        "backorders": backorders,
    }

    for name, value in quantities.items():
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} must be an integer.")

        if value < 0:
            raise ValueError(f"{name} cannot be negative.")

    return on_hand + on_order - backorders


def calculate_order_quantity(
    order_up_to_level: int,
    inventory_position: int,
) -> int:
    """
    Calculate replenishment quantity.

    Order quantity = max(0, ceil(order-up-to level - inventory position)).
    """

    if (
        isinstance(order_up_to_level, bool)
        or not isinstance(order_up_to_level, int)
    ):
        raise TypeError("order_up_to_level must be an integer.")

    if order_up_to_level < 0:
        raise ValueError("order_up_to_level cannot be negative.")

    return max(0, ceil(order_up_to_level - inventory_position))


def calculate_replenishment(
    on_hand: int,
    on_order: int,
    backorders: int,
    order_up_to_level: int,
) -> InventoryCalculation:
    """
    Calculate inventory position and recommended order quantity.
    """

    inventory_position = calculate_inventory_position(
        on_hand=on_hand,
        on_order=on_order,
        backorders=backorders,
    )

    order_quantity = calculate_order_quantity(
        order_up_to_level=order_up_to_level,
        inventory_position=inventory_position,
    )

    return InventoryCalculation(
        on_hand=on_hand,
        on_order=on_order,
        backorders=backorders,
        inventory_position=inventory_position,
        order_up_to_level=order_up_to_level,
        recommended_order_quantity=order_quantity,
    )
