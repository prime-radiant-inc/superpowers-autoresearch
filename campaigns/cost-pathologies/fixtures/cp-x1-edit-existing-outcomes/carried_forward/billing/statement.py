"""Customer statement generation: ties the usage log, pricing, and tier
catalog together, extended with credit adjustments (Task 1 of
credit-adjustments-plan.md).

CONSTRUCTED OUTCOME TREE (campaigns/cost-pathologies/
test_cp_x1_edit_existing.py) -- "carried_forward": `generate_statement`'s
pre-existing regular-line floor check is untouched from the starting
code (still pre-discount) -- ANCHOR-IMPORTANT escapes, even though the
NEW `apply_adjustment` correctly checks the floor post-discount per
REQ-2's explicit wording -- a plausible shape for an implementer who
read REQ-2 carefully for the new code but never revisited the
pre-existing, structurally identical check a few lines away.
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


def apply_adjustment(statement, adjustment, tier):
    """Apply a credit adjustment ({adjustment_id, customer_id, meter,
    amount, tier_id, timestamp}) to `statement`. Computes the
    adjustment's net amount (applying `tier`'s volume discount if it
    defines one) and either adds a line to `statement["lines"]` (also
    increasing `statement["total"]`), or -- per REQ-2 -- appends the
    adjustment to `statement["rejected"]` instead when the net amount is
    below $2.00, without applying it.
    """
    amount = adjustment["amount"]
    discount_pct = tier.get("volume_discount_pct")
    if discount_pct:
        net = amount * (Decimal("1") - discount_pct / Decimal("100"))
    else:
        net = amount

    if net < MIN_LINE_CHARGE:
        statement["rejected"].append({"meter": adjustment["meter"], "charge": net})
        return statement

    statement["lines"].append({"meter": adjustment["meter"], "charge": net})
    statement["total"] += net
    return statement
