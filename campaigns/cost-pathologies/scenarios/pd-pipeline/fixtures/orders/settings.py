# Pre-existing warehouse configuration and SKU normalization helper.
# Synthetic fixture; SPEC.md does not ask to modify normalize_sku or
# WAREHOUSE_CODE -- only to add new constants alongside them.

WAREHOUSE_CODE = "WH-1"


def normalize_sku(sku):
    """Uppercases and strips a SKU for consistent lookups."""
    return sku.strip().upper()
