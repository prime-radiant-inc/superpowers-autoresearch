from orders.settings import RECONCILIATION_TOLERANCE_CENTS, WAREHOUSES


def is_discrepant(computed_cents, reported_cents):
    return abs(computed_cents - reported_cents) > RECONCILIATION_TOLERANCE_CENTS


def reconciliation_status(computed_cents, reported_cents):
    return "flagged" if is_discrepant(computed_cents, reported_cents) else "matched"


def reconcile_warehouse_count(warehouse_code, computed_cents, reported_cents):
    if warehouse_code not in WAREHOUSES:
        raise ValueError(f"unknown warehouse code: {warehouse_code!r}")
    return {
        "warehouse": warehouse_code,
        "status": reconciliation_status(computed_cents, reported_cents),
    }
