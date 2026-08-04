import pytest
from orders.discounts import discount_rate_for_subtotal


def test_boundary_tiers():
    assert discount_rate_for_subtotal(5000) == 0
    assert discount_rate_for_subtotal(5001) == 5
    assert discount_rate_for_subtotal(10001) == 10
    assert discount_rate_for_subtotal(50001) == 20


def test_negative_subtotal_raises():
    with pytest.raises(ValueError, match="invalid subtotal"):
        discount_rate_for_subtotal(-1)
