import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orders.fulfillment import MAX_LINE_ITEMS, build_pick_list


def test_build_pick_list_preserves_order():
    order = {"line_items": [{"sku": "A", "quantity": 1}, {"sku": "B", "quantity": 2}]}
    assert build_pick_list(order) == [
        {"sku": "A", "quantity": 1},
        {"sku": "B", "quantity": 2},
    ]


def test_build_pick_list_rejects_over_cap():
    order = {"line_items": [{"sku": "A", "quantity": 1}] * (MAX_LINE_ITEMS + 1)}
    try:
        build_pick_list(order)
        assert False, "expected ValueError"
    except ValueError:
        pass
