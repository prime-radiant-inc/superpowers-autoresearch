import pytest
from orders.backorders import schedule_backorder_retry, BACKORDER_MAX_ATTEMPTS


def test_retry_schedule():
    assert schedule_backorder_retry(1) == 1
    assert schedule_backorder_retry(2) == 3


def test_exhausted_raises():
    with pytest.raises(ValueError, match="backorder exhausted"):
        schedule_backorder_retry(BACKORDER_MAX_ATTEMPTS)
