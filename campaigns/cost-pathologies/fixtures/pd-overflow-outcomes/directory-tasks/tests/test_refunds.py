import pytest
from orders.refunds import compute_refund, process_refund


def test_fee_tiers():
    assert compute_refund(10000, 3) == 10000
    assert compute_refund(10000, 10) == 9000


def test_past_window_raises():
    with pytest.raises(ValueError, match="return window"):
        compute_refund(10000, 31)


def test_process_refund_marks_status():
    order = {"order_id": "O1", "refund_status": "none"}
    refunded = process_refund(order)
    assert refunded["refund_status"] == "refunded"


def test_duplicate_refund_raises():
    with pytest.raises(ValueError, match="already been refunded"):
        process_refund({"order_id": "O1", "refund_status": "refunded"})
