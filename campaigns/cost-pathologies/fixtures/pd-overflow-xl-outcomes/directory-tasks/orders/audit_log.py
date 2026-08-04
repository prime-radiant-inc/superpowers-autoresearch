from orders.settings import AUDIT_LOG_RETENTION_DAYS

AUDIT_EVENT_SEVERITY = {
    "order_edited": "info",
    "manual_override": "warning",
    "refund_reversed": "critical",
}


def classify_audit_event(event_type):
    if event_type not in AUDIT_EVENT_SEVERITY:
        raise ValueError(f"unknown audit event type: {event_type!r}")
    return AUDIT_EVENT_SEVERITY[event_type]


def is_within_retention(event_date, today_date):
    return (today_date - event_date).days <= AUDIT_LOG_RETENTION_DAYS
