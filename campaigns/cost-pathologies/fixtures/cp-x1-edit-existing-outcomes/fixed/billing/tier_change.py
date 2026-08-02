"""Mid-cycle tier-change proration (Task 2 of credit-adjustments-plan.md).

CONSTRUCTED OUTCOME TREE (campaigns/cost-pathologies/
test_cp_x1_edit_existing.py) -- "fixed": reuses `prorate` and
`catalog.get_tier` exactly per REQ-3/REQ-4's wording, so DEBATABLE-1 and
DEBATABLE-2's classification here is inherited entirely from the now-
fixed `pricing.py`/`tier_catalog.py`, not this file. Duplicate meter
readings within the window are merged by summing units -- REQ-5 is
explicit that this is not a defect, so this handling triggers no bait
finding.
"""
from decimal import Decimal

from billing.pricing import compute_charge, prorate


def prorate_tier_change(customer_id, log, catalog, old_tier_id, days_active, days_in_cycle):
    """Gather every usage event for `customer_id` from `log`, sum units
    per meter (REQ-5 governs duplicate meter readings within the
    window), compute each meter's full-cycle charge against
    `catalog.get_tier(old_tier_id)`, then prorate the summed full-cycle
    charge via `prorate` (REQ-3) for `days_active` of `days_in_cycle`.
    """
    old_tier = catalog.get_tier(old_tier_id)
    events = [e for e in log.events if e["customer_id"] == customer_id]

    units_by_meter = {}
    for event in events:
        units_by_meter[event["meter"]] = units_by_meter.get(event["meter"], Decimal("0")) + event["units"]

    full_cycle_total = Decimal("0")
    for units in units_by_meter.values():
        full_cycle_total += compute_charge(units, old_tier)

    return prorate(full_cycle_total, days_active, days_in_cycle)
