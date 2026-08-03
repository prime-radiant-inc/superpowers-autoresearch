import datetime

import pytest
from orders.returns import is_within_return_window, validate_return_reason


def test_within_window_true():
    assert is_within_return_window(datetime.date(2026, 1, 1), datetime.date(2026, 1, 20)) is True


def test_outside_window_false():
    assert is_within_return_window(datetime.date(2026, 1, 1), datetime.date(2026, 3, 1)) is False


def test_valid_reason_ok():
    validate_return_reason("defective")


def test_invalid_reason_raises():
    with pytest.raises(ValueError, match="unknown return reason"):
        validate_return_reason("changed my mind")
