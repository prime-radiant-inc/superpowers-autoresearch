import pytest
from orders.shipping import compute_shipping_cost


def test_light_package_to_zone_1():
    assert compute_shipping_cost(1500, "Z1") == 500


def test_medium_package_to_zone_2():
    assert compute_shipping_cost(5000, "Z2") == 1200


def test_heavy_package_to_zone_3():
    assert compute_shipping_cost(20000, "Z3") == 2600


def test_boundary_weight_still_light():
    assert compute_shipping_cost(2000, "Z1") == 500


def test_oversized_package_raises():
    with pytest.raises(ValueError, match="exceeds the maximum supported weight"):
        compute_shipping_cost(25001, "Z1")


def test_unknown_zone_raises():
    with pytest.raises(ValueError, match="unknown shipping zone"):
        compute_shipping_cost(1000, "Z9")
