from orders.settings import WAREHOUSES

MANIFEST_CUTOFFS = {
    "WH-1": "15:00",
    "WH-2": "14:00",
    "WH-3": "16:00",
}


def manifest_cutoff_for_warehouse(warehouse_code):
    if warehouse_code not in WAREHOUSES:
        raise ValueError(f"unknown warehouse code: {warehouse_code!r}")
    return MANIFEST_CUTOFFS[warehouse_code]


def is_before_cutoff(warehouse_code, current_time):
    return current_time < manifest_cutoff_for_warehouse(warehouse_code)
