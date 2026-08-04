RATE_LIMITS_PER_MINUTE = {
    "internal": 600,
    "partner": 120,
    "public": 30,
}


def rate_limit_for_client(client_type):
    if client_type not in RATE_LIMITS_PER_MINUTE:
        raise ValueError(f"unknown client type: {client_type!r}")
    return RATE_LIMITS_PER_MINUTE[client_type]


def is_rate_limited(client_type, requests_in_window):
    return requests_in_window > rate_limit_for_client(client_type)
