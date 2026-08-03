import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orders.pricing import CURRENCY, MAX_LINE_ITEMS, compute_total


def test_compute_total_sums_lines():
    total = compute_total([
        {"unit_price_cents": 500, "quantity": 2},
        {"unit_price_cents": 100, "quantity": 3},
    ])
    assert total == 1300


def test_compute_total_rejects_over_cap():
    line_items = [{"unit_price_cents": 100, "quantity": 1}] * (MAX_LINE_ITEMS + 1)
    try:
        compute_total(line_items)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_currency_is_usd():
    assert CURRENCY == "USD"
