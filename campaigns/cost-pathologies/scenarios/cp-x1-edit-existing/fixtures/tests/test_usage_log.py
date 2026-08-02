from decimal import Decimal

from billing.usage_log import UsageLog


def _event(event_id, customer_id="cust-1", meter="storage-gb", units="10", tier_id="standard"):
    return {
        "event_id": event_id,
        "customer_id": customer_id,
        "meter": meter,
        "units": Decimal(units),
        "tier_id": tier_id,
        "timestamp": "2026-08-01T00:00:00Z",
    }


def test_record_event_returns_true_and_persists(tmp_path):
    log = UsageLog(tmp_path / "usage.json")
    assert log.record_event(_event("evt-1")) is True
    assert log.has_event("evt-1")
    assert len(log.events) == 1


def test_record_event_duplicate_returns_false_and_does_not_duplicate(tmp_path):
    log = UsageLog(tmp_path / "usage.json")
    log.record_event(_event("evt-1"))
    assert log.record_event(_event("evt-1")) is False
    assert len(log.events) == 1


def test_fresh_log_recovers_previously_recorded_events(tmp_path):
    path = tmp_path / "usage.json"
    first = UsageLog(path)
    first.record_event(_event("evt-1"))
    first.record_event(_event("evt-2"))

    second = UsageLog(path)
    assert second.has_event("evt-1")
    assert second.has_event("evt-2")
    assert len(second.events) == 2
