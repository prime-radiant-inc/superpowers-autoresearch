import pytest
from orders.validation import (
    validate_line_items,
    validate_quantity,
    validate_sku_category,
    validate_customer_id_format,
    MAX_LINE_ITEMS,
)


def test_line_items_at_cap_ok():
    validate_line_items([{"sku": f"GEN-{i:04d}"} for i in range(MAX_LINE_ITEMS)])


def test_line_items_over_cap_raises():
    with pytest.raises(ValueError, match=f"{MAX_LINE_ITEMS}-line-item limit"):
        validate_line_items([{"sku": f"GEN-{i:04d}"} for i in range(MAX_LINE_ITEMS + 1)])


def test_quantity_valid():
    validate_quantity(1)


def test_quantity_invalid_raises():
    with pytest.raises(ValueError, match="invalid quantity: 0"):
        validate_quantity(0)


def test_sku_category_known_prefixes():
    assert validate_sku_category("GEN-1234") == "general"
    assert validate_sku_category("FRZ-1234") == "frozen"
    assert validate_sku_category("HAZ-1234") == "hazardous"


def test_sku_category_unknown_prefix_raises():
    with pytest.raises(ValueError, match="unrecognized SKU category"):
        validate_sku_category("XXX-1234")


def test_customer_id_valid_format():
    validate_customer_id_format("CUST12")


def test_customer_id_invalid_format_raises():
    with pytest.raises(ValueError, match="invalid customer id format"):
        validate_customer_id_format("c!")
