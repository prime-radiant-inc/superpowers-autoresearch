LOYALTY_POINT_MULTIPLIERS = {"bronze": 1, "silver": 2, "gold": 3, "platinum": 5}


def points_for_purchase(customer_tier, subtotal_cents):
    if customer_tier not in LOYALTY_POINT_MULTIPLIERS:
        raise ValueError(f"unknown loyalty tier: {customer_tier!r}")
    return (subtotal_cents // 100) * LOYALTY_POINT_MULTIPLIERS[customer_tier]
