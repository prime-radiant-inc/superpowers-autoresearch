from decimal import Decimal

from billing.statement import generate_statement
from billing.tier_catalog import TierCatalog
from billing.usage_log import UsageLog


def _event(event_id, customer_id, meter, units, tier_id):
    return {
        "event_id": event_id,
        "customer_id": customer_id,
        "meter": meter,
        "units": Decimal(units),
        "tier_id": tier_id,
        "timestamp": "2026-08-01T00:00:00Z",
    }


def test_statement_normal_line_above_floor(tmp_path):
    log = UsageLog(tmp_path / "usage.json")
    log.record_event(_event("evt-1", "cust-1", "storage-gb", "1000", "standard"))
    catalog = TierCatalog({"standard": {"rate_per_unit": Decimal("0.01")}})

    statement = generate_statement("cust-1", log, catalog)

    assert statement["rejected"] == []
    assert len(statement["lines"]) == 1
    assert statement["lines"][0]["charge"] == Decimal("10.00")
    assert statement["total"] == Decimal("10.00")


def test_statement_line_below_floor_is_rejected_not_billed(tmp_path):
    log = UsageLog(tmp_path / "usage.json")
    log.record_event(_event("evt-1", "cust-1", "bandwidth-gb", "10", "standard"))
    catalog = TierCatalog({"standard": {"rate_per_unit": Decimal("0.01")}})

    statement = generate_statement("cust-1", log, catalog)

    assert statement["lines"] == []
    assert len(statement["rejected"]) == 1
    assert statement["rejected"][0]["meter"] == "bandwidth-gb"
