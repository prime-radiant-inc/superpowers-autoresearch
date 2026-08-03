import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orders.validation import validate_line_items, validate_quantity


def test_validate_line_items_accepts_at_cap():
    validate_line_items([{"sku": f"s{i}"} for i in range(12)])


def test_validate_line_items_rejects_over_cap():
    try:
        validate_line_items([{"sku": f"s{i}"} for i in range(13)])
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_validate_quantity_rejects_zero():
    try:
        validate_quantity(0)
        assert False, "expected ValueError"
    except ValueError:
        pass
