# Pre-existing multi-warehouse configuration and SKU normalization
# helper, plus the settings.py micro-edits SPEC.md asked for.

WAREHOUSE_CODE = "WH-1"

WAREHOUSES = ["WH-1", "WH-2", "WH-3"]

NOTIFY_MAX_RETRIES = 3

DEFAULT_REPORT_TIMEZONE = "UTC"

ARCHIVE_GRACE_DAYS = 7

RETURN_WINDOW_DAYS = 30

AUDIT_LOG_RETENTION_DAYS = 90

RECONCILIATION_TOLERANCE_CENTS = 500


def normalize_sku(sku):
    """Uppercases and strips a SKU for consistent lookups."""
    return sku.strip().upper()
