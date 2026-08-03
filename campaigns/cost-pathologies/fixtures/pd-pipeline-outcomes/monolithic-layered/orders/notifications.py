_MESSAGES = {
    "received": "order received",
    "picking": "order is being picked",
    "shipped": "order has shipped",
    "cancelled": "order was cancelled",
}


def notify_customer(order_status):
    if order_status not in _MESSAGES:
        raise ValueError(f"unknown order status: {order_status!r}")
    return _MESSAGES[order_status]
