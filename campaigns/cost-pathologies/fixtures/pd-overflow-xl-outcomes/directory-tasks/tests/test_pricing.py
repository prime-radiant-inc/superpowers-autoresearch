import pytest
from orders.pricing import compute_total, MAX_LINE_ITEMS, CURRENCY


def test_compute_total_applies_discount():
    line_items = [{"unit_price_cents": 3000, "quantity": 4}]  # subtotal 12000 -> 10%
    assert compute_total(line_items) == 10800


def test_compute_total_over_cap_raises():
    line_items = [{"unit_price_cents": 100, "quantity": 1} for _ in range(MAX_LINE_ITEMS + 1)]
    with pytest.raises(ValueError, match=f"{MAX_LINE_ITEMS}-line-item limit"):
        compute_total(line_items)


def test_currency_is_usd():
    assert CURRENCY == "USD"
