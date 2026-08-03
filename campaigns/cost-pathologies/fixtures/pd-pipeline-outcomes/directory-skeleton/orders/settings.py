# Pre-existing warehouse configuration and SKU normalization helper,
# extended per SPEC.md's three settings additions.

WAREHOUSE_CODE = "WH-1"

NOTIFY_MAX_RETRIES = 3
DEFAULT_REPORT_TIMEZONE = "UTC"
ARCHIVE_GRACE_DAYS = 7


def normalize_sku(sku):
    """Uppercases and strips a SKU for consistent lookups."""
    return sku.strip().upper()
