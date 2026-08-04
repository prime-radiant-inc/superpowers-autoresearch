from orders.settings import normalize_sku, WAREHOUSE_CODE, WAREHOUSES


def test_normalize_sku_strips_and_uppercases():
    assert normalize_sku("  sku-123  ") == "SKU-123"


def test_warehouse_code_and_warehouses_preexist():
    assert WAREHOUSE_CODE == "WH-1"
    assert WAREHOUSES == ["WH-1", "WH-2", "WH-3"]
