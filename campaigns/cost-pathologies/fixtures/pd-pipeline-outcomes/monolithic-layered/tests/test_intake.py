import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orders.intake import OrderIntakeError, parse_order


def test_parse_order_normal_line():
    order = parse_order("o1,c1,SKU-1,2,500")
    assert order == {
        "order_id": "o1",
        "customer_id": "c1",
        "sku": "SKU-1",
        "quantity": 2,
        "unit_price_cents": 500,
        "status": "received",
    }


def test_parse_order_missing_field_raises():
    try:
        parse_order("o1,,SKU-1,2,500")
        assert False, "expected OrderIntakeError"
    except OrderIntakeError as exc:
        assert "customer_id" in str(exc)
