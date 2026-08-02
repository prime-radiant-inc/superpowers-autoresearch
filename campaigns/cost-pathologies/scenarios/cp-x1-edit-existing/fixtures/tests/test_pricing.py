from decimal import Decimal

from billing.pricing import compute_charge, prorate


def test_compute_charge_full_cycle():
    tier = {"rate_per_unit": Decimal("0.05")}
    assert compute_charge(Decimal("100"), tier) == Decimal("5.00")


def test_prorate_half_cycle():
    assert prorate(Decimal("30.00"), 15, 30) == Decimal("15.00")
