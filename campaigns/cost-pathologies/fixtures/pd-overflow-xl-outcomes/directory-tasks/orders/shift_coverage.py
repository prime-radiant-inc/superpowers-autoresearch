from orders.settings import WAREHOUSES

SHIFT_COVERAGE_HOURS = {
    "WH-1": (6, 22),
    "WH-2": (8, 20),
    "WH-3": (0, 24),
}


def warehouse_open_hours(warehouse_code):
    if warehouse_code not in WAREHOUSES:
        raise ValueError(f"unknown warehouse code: {warehouse_code!r}")
    return SHIFT_COVERAGE_HOURS[warehouse_code]


def is_warehouse_staffed(warehouse_code, hour):
    if hour < 0 or hour > 23:
        raise ValueError(f"invalid hour: {hour}")
    open_hour, close_hour = warehouse_open_hours(warehouse_code)
    return open_hour <= hour < close_hour
