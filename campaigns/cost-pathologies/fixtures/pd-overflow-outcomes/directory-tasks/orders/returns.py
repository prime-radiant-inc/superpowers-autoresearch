from orders.settings import RETURN_WINDOW_DAYS

REASON_CODES = {"defective", "wrong_item", "no_longer_needed", "damaged_in_transit"}


def is_within_return_window(shipped_date, request_date):
    return (request_date - shipped_date).days <= RETURN_WINDOW_DAYS


def validate_return_reason(reason):
    if reason not in REASON_CODES:
        raise ValueError(f"unknown return reason: {reason!r}")
