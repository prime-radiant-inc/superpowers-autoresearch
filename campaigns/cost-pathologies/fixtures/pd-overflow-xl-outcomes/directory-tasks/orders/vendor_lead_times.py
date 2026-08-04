import datetime

VENDOR_LEAD_TIME_DAYS = {
    "fast": 3,
    "standard": 7,
    "slow": 14,
}


def lead_time_days_for_tier(tier):
    if tier not in VENDOR_LEAD_TIME_DAYS:
        raise ValueError(f"unknown vendor tier: {tier!r}")
    return VENDOR_LEAD_TIME_DAYS[tier]


def expected_restock_date(order_date, tier):
    return order_date + datetime.timedelta(days=lead_time_days_for_tier(tier))
