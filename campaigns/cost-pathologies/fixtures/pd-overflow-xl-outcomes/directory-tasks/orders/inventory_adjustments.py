ADJUSTMENT_REASON_CODES = {"damaged", "miscount", "theft", "found_stock"}


def validate_adjustment_reason(reason):
    if reason not in ADJUSTMENT_REASON_CODES:
        raise ValueError(f"unknown adjustment reason: {reason!r}")


def approval_level_for_adjustment(quantity):
    if quantity < 1:
        raise ValueError(f"invalid adjustment quantity: {quantity}")
    if quantity <= 10:
        return "none"
    if quantity <= 50:
        return "supervisor"
    return "admin"
