import pytest

from orders.reconciliation import (
    is_discrepant,
    reconciliation_status,
    reconcile_warehouse_count,
)


def test_within_tolerance_not_discrepant():
    assert is_discrepant(10000, 10500) is False


def test_over_tolerance_is_discrepant():
    assert is_discrepant(10000, 10600) is True


def test_reconciliation_status():
    assert reconciliation_status(10000, 10500) == "matched"
    assert reconciliation_status(10000, 10600) == "flagged"


def test_reconcile_warehouse_count():
    assert reconcile_warehouse_count("WH-1", 10000, 10500) == {
        "warehouse": "WH-1",
        "status": "matched",
    }


def test_reconcile_unknown_warehouse_raises():
    with pytest.raises(ValueError, match="unknown warehouse code: 'WH-9'"):
        reconcile_warehouse_count("WH-9", 10000, 10500)
