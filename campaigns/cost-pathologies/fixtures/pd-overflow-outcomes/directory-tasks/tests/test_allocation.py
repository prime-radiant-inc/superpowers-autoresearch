import pytest
from orders.allocation import allocate_warehouse, MAX_LINE_ITEMS


def test_preferred_warehouse_when_capable():
    assert allocate_warehouse("Z2", ["general", "frozen"]) == "WH-2"


def test_falls_back_when_preferred_lacks_capability():
    assert allocate_warehouse("Z3", ["hazardous"]) == "WH-1"


def test_unknown_zone_raises():
    with pytest.raises(ValueError, match="unknown shipping zone"):
        allocate_warehouse("Z9", ["general"])


def test_over_cap_raises():
    with pytest.raises(ValueError, match=f"{MAX_LINE_ITEMS}-line-item limit"):
        allocate_warehouse("Z1", ["general"] * (MAX_LINE_ITEMS + 1))
