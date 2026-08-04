import pytest

from orders.shift_coverage import is_warehouse_staffed, warehouse_open_hours


def test_warehouse_open_hours():
    assert warehouse_open_hours("WH-1") == (6, 22)
    assert warehouse_open_hours("WH-3") == (0, 24)


def test_unknown_warehouse_raises():
    with pytest.raises(ValueError, match="unknown warehouse code: 'WH-9'"):
        warehouse_open_hours("WH-9")


def test_is_warehouse_staffed_within_and_outside_hours():
    assert is_warehouse_staffed("WH-2", 8) is True
    assert is_warehouse_staffed("WH-2", 19) is True
    assert is_warehouse_staffed("WH-2", 20) is False
    assert is_warehouse_staffed("WH-2", 5) is False


def test_wh3_staffed_all_day():
    assert is_warehouse_staffed("WH-3", 0) is True
    assert is_warehouse_staffed("WH-3", 23) is True


def test_invalid_hour_raises():
    with pytest.raises(ValueError, match="invalid hour: 24"):
        is_warehouse_staffed("WH-1", 24)
