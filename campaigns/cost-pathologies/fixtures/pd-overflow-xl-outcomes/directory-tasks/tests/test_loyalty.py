import pytest
from orders.loyalty import points_for_purchase


def test_tier_multipliers():
    assert points_for_purchase("bronze", 10000) == 100
    assert points_for_purchase("platinum", 10000) == 500


def test_unknown_tier_raises():
    with pytest.raises(ValueError, match="unknown loyalty tier"):
        points_for_purchase("diamond", 10000)
