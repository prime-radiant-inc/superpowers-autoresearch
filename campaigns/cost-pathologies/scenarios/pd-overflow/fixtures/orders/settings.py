# Pre-existing multi-warehouse configuration and SKU normalization
# helper. Synthetic fixture; SPEC.md does not ask to modify
# normalize_sku, WAREHOUSE_CODE, or WAREHOUSES -- only to add new
# constants alongside them.

WAREHOUSE_CODE = "WH-1"

WAREHOUSES = ["WH-1", "WH-2", "WH-3"]


def normalize_sku(sku):
    """Uppercases and strips a SKU for consistent lookups."""
    return sku.strip().upper()
