
import pytest

from retail_intelligence.inventory.calculations import (
    calculate_inventory_position,
    calculate_order_quantity,
    calculate_replenishment,
)


@pytest.mark.parametrize(
    "on_hand,on_order,backorders,expected",
    [
        (23, 6, 2, 27),
        (50, 0, 0, 50),
        (5, 0, 10, -5),
        (0, 20, 5, 15),
    ],
)
def test_inventory_position(
    on_hand, on_order, backorders, expected
):
    assert calculate_inventory_position(
        on_hand, on_order, backorders
    ) == expected


@pytest.mark.parametrize(
    "target,position,expected",
    [
        (45, 27, 18),
        (45, 50, 0),
        (45, -5, 50),
        (0, 0, 0),
    ],
)
def test_order_quantity(target, position, expected):
    assert calculate_order_quantity(target, position) == expected


def test_replenishment_calculation():
    result = calculate_replenishment(
        on_hand=23,
        on_order=6,
        backorders=2,
        order_up_to_level=45,
    )

    assert result.inventory_position == 27
    assert result.recommended_order_quantity == 18


@pytest.mark.parametrize(
    "on_hand,on_order,backorders",
    [
        (-1, 0, 0),
        (0, -1, 0),
        (0, 0, -1),
        (True, 0, 0),
        (1.5, 0, 0),
    ],
)
def test_invalid_inventory_quantities(
    on_hand, on_order, backorders
):
    with pytest.raises((TypeError, ValueError)):
        calculate_inventory_position(
            on_hand, on_order, backorders
        )


def test_invalid_order_up_to_level():
    with pytest.raises((TypeError, ValueError)):
        calculate_order_quantity(-1, 10)
