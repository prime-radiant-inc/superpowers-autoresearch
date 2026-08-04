import datetime

import pytest

from orders.audit_log import classify_audit_event, is_within_retention


def test_classify_known_events():
    assert classify_audit_event("order_edited") == "info"
    assert classify_audit_event("manual_override") == "warning"
    assert classify_audit_event("refund_reversed") == "critical"


def test_classify_unknown_event_raises():
    with pytest.raises(ValueError, match="unknown audit event type: 'bogus'"):
        classify_audit_event("bogus")


def test_within_retention_window():
    event_date = datetime.date(2026, 1, 1)
    today = datetime.date(2026, 3, 31)  # 89 days later
    assert is_within_retention(event_date, today) is True


def test_outside_retention_window():
    event_date = datetime.date(2026, 1, 1)
    today = datetime.date(2026, 4, 5)  # 94 days later
    assert is_within_retention(event_date, today) is False
