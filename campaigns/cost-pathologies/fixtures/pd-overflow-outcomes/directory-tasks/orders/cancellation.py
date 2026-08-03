_CANCELLABLE_STATUSES = {"received", "picking"}


def cancel_order(order_status):
    if order_status not in _CANCELLABLE_STATUSES:
        raise ValueError(f"cannot cancel an order with status {order_status!r}")
    return "cancelled"
