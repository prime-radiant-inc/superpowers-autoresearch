import pytest
from orders.intake import parse_order, OrderIntakeError


def test_parse_order_ok():
    assert parse_order("O1,C1,GEN-0001,2,500") == {
        "order_id": "O1",
        "customer_id": "C1",
        "sku": "GEN-0001",
        "quantity": 2,
        "unit_price_cents": 500,
        "status": "received",
    }


def test_parse_order_missing_field_raises():
    with pytest.raises(OrderIntakeError, match="unit_price_cents"):
        parse_order("O1,C1,GEN-0001,2,")
