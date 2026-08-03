from orders.settings import RETURN_WINDOW_DAYS

RESTOCKING_FEE_TIERS = [(7, 0), (14, 10), (21, 20), (30, 30)]


def compute_refund(order_total_cents, days_since_delivery):
    if days_since_delivery > RETURN_WINDOW_DAYS:
        raise ValueError(f"return window of {RETURN_WINDOW_DAYS} days has elapsed")
    for upper_bound, fee_percent in RESTOCKING_FEE_TIERS:
        if days_since_delivery <= upper_bound:
            return (order_total_cents * (100 - fee_percent)) // 100
    return order_total_cents


def process_refund(order):
    if order["refund_status"] == "refunded":
        raise ValueError("order has already been refunded")
    refunded = dict(order)
    refunded["refund_status"] = "refunded"
    return refunded
