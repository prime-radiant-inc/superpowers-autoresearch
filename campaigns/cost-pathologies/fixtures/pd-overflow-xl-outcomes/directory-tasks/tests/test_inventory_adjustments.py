import pytest

from orders.inventory_adjustments import (
    approval_level_for_adjustment,
    validate_adjustment_reason,
)


def test_valid_reasons_pass():
    for reason in ("damaged", "miscount", "theft", "found_stock"):
        validate_adjustment_reason(reason)


def test_invalid_reason_raises():
    with pytest.raises(ValueError, match="unknown adjustment reason: 'lost'"):
        validate_adjustment_reason("lost")


def test_approval_tiers():
    assert approval_level_for_adjustment(1) == "none"
    assert approval_level_for_adjustment(10) == "none"
    assert approval_level_for_adjustment(11) == "supervisor"
    assert approval_level_for_adjustment(50) == "supervisor"
    assert approval_level_for_adjustment(51) == "admin"


def test_invalid_quantity_raises():
    with pytest.raises(ValueError, match="invalid adjustment quantity: 0"):
        approval_level_for_adjustment(0)
