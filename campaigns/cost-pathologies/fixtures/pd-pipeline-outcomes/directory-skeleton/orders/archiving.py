def should_archive(order_status, age_days):
    return order_status in ("shipped", "cancelled") and age_days >= 30
