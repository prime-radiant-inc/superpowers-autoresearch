from orders.settings import NOTIFY_MAX_RETRIES

_STATUS_MESSAGES = {
    "received": "order received",
    "picking": "order is being picked",
    "shipped": "order has shipped",
    "cancelled": "order was cancelled",
}

CHANNEL_RETRY_OVERRIDES = {"email": 3, "sms": 5, "push": 2}


def notify_customer(order_status):
    if order_status not in _STATUS_MESSAGES:
        raise ValueError(f"unknown order status: {order_status!r}")
    return _STATUS_MESSAGES[order_status]


def retries_for_channel(channel):
    return CHANNEL_RETRY_OVERRIDES.get(channel, NOTIFY_MAX_RETRIES)
