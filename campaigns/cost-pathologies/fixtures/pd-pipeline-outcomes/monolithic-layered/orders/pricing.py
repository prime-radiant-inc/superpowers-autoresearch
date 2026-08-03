CURRENCY = "USD"
MAX_LINE_ITEMS = 12


def compute_total(line_items):
    if len(line_items) > MAX_LINE_ITEMS:
        raise ValueError(f"order exceeds the {MAX_LINE_ITEMS}-line-item limit")
    return sum(item["unit_price_cents"] * item["quantity"] for item in line_items)
