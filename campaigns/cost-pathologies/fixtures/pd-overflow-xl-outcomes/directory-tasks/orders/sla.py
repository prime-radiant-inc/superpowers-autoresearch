PROMISED_DELIVERY_DAYS = {
    "standard": {"Z1": 5, "Z2": 7, "Z3": 10},
    "express": {"Z1": 2, "Z2": 3, "Z3": 4},
}


def promised_delivery_days(speed, zone):
    if speed not in PROMISED_DELIVERY_DAYS:
        raise ValueError(f"unknown shipping speed: {speed!r}")
    return PROMISED_DELIVERY_DAYS[speed][zone]
