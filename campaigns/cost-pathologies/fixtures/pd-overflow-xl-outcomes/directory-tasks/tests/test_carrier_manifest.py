import pytest

from orders.carrier_manifest import is_before_cutoff, manifest_cutoff_for_warehouse


def test_manifest_cutoff_for_known_warehouses():
    assert manifest_cutoff_for_warehouse("WH-1") == "15:00"
    assert manifest_cutoff_for_warehouse("WH-2") == "14:00"
    assert manifest_cutoff_for_warehouse("WH-3") == "16:00"


def test_unknown_warehouse_raises():
    with pytest.raises(ValueError, match="unknown warehouse code: 'WH-9'"):
        manifest_cutoff_for_warehouse("WH-9")


def test_is_before_cutoff():
    assert is_before_cutoff("WH-1", "14:59") is True
    assert is_before_cutoff("WH-1", "15:00") is False
    assert is_before_cutoff("WH-1", "16:00") is False
