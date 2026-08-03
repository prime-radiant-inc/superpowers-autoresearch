import pytest
from orders.sla import promised_delivery_days


def test_standard_and_express():
    assert promised_delivery_days("standard", "Z1") == 5
    assert promised_delivery_days("express", "Z1") == 2


def test_unknown_speed_raises():
    with pytest.raises(ValueError, match="unknown shipping speed"):
        promised_delivery_days("overnight", "Z1")
