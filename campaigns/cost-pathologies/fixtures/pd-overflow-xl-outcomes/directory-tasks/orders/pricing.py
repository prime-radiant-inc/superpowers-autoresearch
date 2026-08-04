from orders.discounts import discount_rate_for_subtotal

MAX_LINE_ITEMS = 12

CURRENCY = "USD"


def compute_total(line_items):
    if len(line_items) > MAX_LINE_ITEMS:
        raise ValueError(f"order exceeds the {MAX_LINE_ITEMS}-line-item limit")
    subtotal = sum(item["unit_price_cents"] * item["quantity"] for item in line_items)
    rate = discount_rate_for_subtotal(subtotal)
    return (subtotal * (100 - rate)) // 100
