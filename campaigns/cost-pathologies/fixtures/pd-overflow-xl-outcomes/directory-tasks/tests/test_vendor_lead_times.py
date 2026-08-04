import datetime

import pytest

from orders.vendor_lead_times import expected_restock_date, lead_time_days_for_tier


def test_lead_time_for_known_tiers():
    assert lead_time_days_for_tier("fast") == 3
    assert lead_time_days_for_tier("standard") == 7
    assert lead_time_days_for_tier("slow") == 14


def test_unknown_tier_raises():
    with pytest.raises(ValueError, match="unknown vendor tier: 'rush'"):
        lead_time_days_for_tier("rush")


def test_expected_restock_date():
    order_date = datetime.date(2026, 1, 1)
    assert expected_restock_date(order_date, "fast") == datetime.date(2026, 1, 4)
    assert expected_restock_date(order_date, "slow") == datetime.date(2026, 1, 15)
