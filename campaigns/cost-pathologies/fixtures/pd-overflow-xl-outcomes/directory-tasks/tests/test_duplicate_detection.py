from orders.duplicate_detection import is_duplicate


def _order(customer_id, skus, submitted_at_minutes):
    return {
        "customer_id": customer_id,
        "line_items": [{"sku": sku} for sku in skus],
        "submitted_at_minutes": submitted_at_minutes,
    }


def test_same_customer_same_skus_within_window_is_duplicate():
    a = _order("C-1", ["GEN-1", "GEN-2"], 100)
    b = _order("C-1", ["GEN-2", "GEN-1"], 110)
    assert is_duplicate(a, b) is True


def test_different_customer_is_not_duplicate():
    a = _order("C-1", ["GEN-1"], 100)
    b = _order("C-2", ["GEN-1"], 100)
    assert is_duplicate(a, b) is False


def test_different_skus_is_not_duplicate():
    a = _order("C-1", ["GEN-1"], 100)
    b = _order("C-1", ["GEN-2"], 100)
    assert is_duplicate(a, b) is False


def test_outside_window_is_not_duplicate():
    a = _order("C-1", ["GEN-1"], 100)
    b = _order("C-1", ["GEN-1"], 120)
    assert is_duplicate(a, b) is False
