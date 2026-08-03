import os
import sys

# Self-resolving import (matches this campaign's other fixtures'
# convention): this fixture is also collected standalone by the
# top-level `pytest` sweep, where it is never pip-installed, so it must
# find its sibling package without relying on an editable install.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orders.settings import normalize_sku, WAREHOUSE_CODE, WAREHOUSES


def test_normalize_sku_strips_and_uppercases():
    assert normalize_sku("  sku-123  ") == "SKU-123"


def test_warehouse_code_and_warehouses_preexist():
    assert WAREHOUSE_CODE == "WH-1"
    assert WAREHOUSES == ["WH-1", "WH-2", "WH-3"]
