import pytest
from orders.cancellation import cancel_order


def test_cancel_from_received():
    assert cancel_order("received") == "cancelled"


def test_cancel_from_picking():
    assert cancel_order("picking") == "cancelled"


def test_cancel_after_shipped_raises():
    with pytest.raises(ValueError, match="cannot cancel an order"):
        cancel_order("shipped")
