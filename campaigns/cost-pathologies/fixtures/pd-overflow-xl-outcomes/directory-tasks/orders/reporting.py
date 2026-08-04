from orders.settings import WAREHOUSES

_TRACKED_STATUSES = ("received", "picking", "shipped", "cancelled")


def build_daily_report(orders):
    total = len(orders)
    by_status = {status: 0 for status in _TRACKED_STATUSES}
    by_warehouse = {code: 0 for code in WAREHOUSES}
    cancelled = 0

    for order in orders:
        status = order.get("status")
        if status in by_status:
            by_status[status] += 1
        if status == "cancelled":
            cancelled += 1
        warehouse = order.get("warehouse")
        if warehouse in by_warehouse:
            by_warehouse[warehouse] += 1

    return {
        "total": total,
        "by_status": by_status,
        "by_warehouse": by_warehouse,
        "returns_rate": (cancelled / total) if total else 0.0,
    }
