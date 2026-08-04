import pytest

from orders.ledger_sync import ledger_code_for_status


def test_ledger_code_for_known_statuses():
    assert ledger_code_for_status("received") == "AR-PEND"
    assert ledger_code_for_status("shipped") == "AR-REV"
    assert ledger_code_for_status("cancelled") == "AR-VOID"
    assert ledger_code_for_status("refunded") == "AR-CREDIT"


def test_unknown_status_raises():
    with pytest.raises(ValueError, match="no ledger code for order status: 'picking'"):
        ledger_code_for_status("picking")
