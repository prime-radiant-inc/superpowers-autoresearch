_KNOWN_STATUSES = ("received", "picking", "shipped", "cancelled")


def build_daily_report(orders):
    by_status = {status: 0 for status in _KNOWN_STATUSES}
    for order in orders:
        status = order["status"]
        if status in by_status:
            by_status[status] += 1
    return {"total": len(orders), "by_status": by_status}
