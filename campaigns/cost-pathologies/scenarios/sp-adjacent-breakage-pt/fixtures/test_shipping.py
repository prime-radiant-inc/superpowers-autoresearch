from shipping import calculate_shipping


def test_calculate_shipping_light():
    assert calculate_shipping(2) == 5.0


def test_calculate_shipping_free_over_50():
    assert calculate_shipping(50) == 0
