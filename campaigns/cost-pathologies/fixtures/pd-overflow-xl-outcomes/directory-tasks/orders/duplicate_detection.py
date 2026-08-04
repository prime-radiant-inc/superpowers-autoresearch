DUPLICATE_WINDOW_MINUTES = 15


def is_duplicate(order_a, order_b):
    if order_a["customer_id"] != order_b["customer_id"]:
        return False
    skus_a = {item["sku"] for item in order_a["line_items"]}
    skus_b = {item["sku"] for item in order_b["line_items"]}
    if skus_a != skus_b:
        return False
    delta = abs(order_a["submitted_at_minutes"] - order_b["submitted_at_minutes"])
    return delta <= DUPLICATE_WINDOW_MINUTES
