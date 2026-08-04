import pytest
from orders.fulfillment import build_pick_list, flag_backorder_items, MAX_LINE_ITEMS


def test_build_pick_list_preserves_order():
    order = {"line_items": [{"sku": "GEN-0001", "quantity": 2}, {"sku": "GEN-0002", "quantity": 1}]}
    assert build_pick_list(order) == [
        {"sku": "GEN-0001", "quantity": 2},
        {"sku": "GEN-0002", "quantity": 1},
    ]


def test_build_pick_list_over_cap_raises():
    order = {"line_items": [{"sku": f"GEN-{i:04d}", "quantity": 1} for i in range(MAX_LINE_ITEMS + 1)]}
    with pytest.raises(ValueError, match=f"{MAX_LINE_ITEMS}-line-item limit"):
        build_pick_list(order)


def test_flag_backorder_items_finds_shortfall():
    pick_list = [{"sku": "GEN-0001", "quantity": 5}, {"sku": "GEN-0002", "quantity": 1}]
    available_stock = {"GEN-0001": 2, "GEN-0002": 3}
    assert flag_backorder_items(pick_list, available_stock) == [{"sku": "GEN-0001", "quantity": 5}]
