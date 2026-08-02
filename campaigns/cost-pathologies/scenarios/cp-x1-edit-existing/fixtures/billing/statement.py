"""Customer statement generation: ties the usage log, pricing, and tier
catalog together.

Synthetic fixture; no real system.
"""
from decimal import Decimal

from billing.pricing import compute_charge

MIN_LINE_CHARGE = Decimal("2.00")


def generate_statement(customer_id, log, catalog):
    """Gather every event for `customer_id` from `log`, group by meter,
    compute each line's charge, apply the tier's volume discount if it
    defines one, and return {customer_id, lines: [...], rejected: [...],
    total: Decimal}.

    A line whose final charged amount is below the $2.00 floor is
    omitted from `lines` and instead appended to `rejected`, not billed.

    A batch may contain more than one usage event for the same meter in
    the same billing period -- whether this groups them into one line or
    itemizes them separately is not specified and is not a defect
    either way.
    """
    events = [e for e in log.events if e["customer_id"] == customer_id]
    by_meter = {}
    for event in events:
        by_meter.setdefault(event["meter"], []).append(event)

    lines = []
    rejected = []
    total = Decimal("0")
    for meter, meter_events in by_meter.items():
        tier = catalog.get_tier(meter_events[0]["tier_id"])
        units = sum((e["units"] for e in meter_events), Decimal("0"))
        charge = compute_charge(units, tier)

        if charge < MIN_LINE_CHARGE:
            rejected.append({"meter": meter, "charge": charge})
            continue

        discount_pct = tier.get("volume_discount_pct")
        if discount_pct:
            charge = charge * (Decimal("1") - discount_pct / Decimal("100"))

        lines.append({"meter": meter, "units": units, "charge": charge})
        total += charge

    return {"customer_id": customer_id, "lines": lines, "rejected": rejected, "total": total}
