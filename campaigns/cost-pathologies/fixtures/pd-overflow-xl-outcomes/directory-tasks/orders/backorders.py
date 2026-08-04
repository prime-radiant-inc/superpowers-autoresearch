BACKORDER_MAX_ATTEMPTS = 3

BACKORDER_RETRY_SCHEDULE_DAYS = {1: 1, 2: 3, 3: 7}


def schedule_backorder_retry(attempt_number):
    if attempt_number >= BACKORDER_MAX_ATTEMPTS:
        raise ValueError(f"backorder exhausted after {BACKORDER_MAX_ATTEMPTS} attempts")
    return BACKORDER_RETRY_SCHEDULE_DAYS[attempt_number]
