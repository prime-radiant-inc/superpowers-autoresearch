MAX_LINE_ITEMS = 12

WAREHOUSE_CAPABILITIES = {
    "WH-1": {"general", "frozen", "hazardous"},
    "WH-2": {"general", "frozen"},
    "WH-3": {"general"},
}

ZONE_WAREHOUSE = {
    "Z1": "WH-1",
    "Z2": "WH-2",
    "Z3": "WH-3",
}

FALLBACK_WAREHOUSE = "WH-1"


def allocate_warehouse(zone, sku_categories):
    if len(sku_categories) > MAX_LINE_ITEMS:
        raise ValueError(f"order exceeds the {MAX_LINE_ITEMS}-line-item limit")
    if zone not in ZONE_WAREHOUSE:
        raise ValueError(f"unknown shipping zone: {zone!r}")
    preferred = ZONE_WAREHOUSE[zone]
    if set(sku_categories) <= WAREHOUSE_CAPABILITIES[preferred]:
        return preferred
    return FALLBACK_WAREHOUSE
