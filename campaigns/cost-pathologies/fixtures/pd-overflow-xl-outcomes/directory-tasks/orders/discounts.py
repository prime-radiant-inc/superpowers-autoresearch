DISCOUNT_TIERS = [
    (5000, 0),
    (10000, 5),
    (25000, 10),
    (50000, 15),
]
DISCOUNT_TOP_TIER_RATE = 20


def discount_rate_for_subtotal(subtotal_cents):
    if subtotal_cents < 0:
        raise ValueError(f"invalid subtotal: {subtotal_cents}")
    for upper_bound, rate in DISCOUNT_TIERS:
        if subtotal_cents <= upper_bound:
            return rate
    return DISCOUNT_TOP_TIER_RATE
