"""Mid-cycle tier-change proration (Task 2 of credit-adjustments-plan.md).

CONSTRUCTED OUTCOME TREE (campaigns/cost-pathologies/
test_cp_x1_edit_existing.py) -- "carried_forward": reuses `prorate` and
`catalog.get_tier`/`has_tier` exactly per REQ-3/REQ-4/REQ-6's wording,
so DEBATABLE-1 and DEBATABLE-2's classification here is inherited
entirely from `pricing.py`/`tier_catalog.py`, not this file. Duplicate
meter readings within the window are merged by summing units -- REQ-5
is explicit that this is not a defect, so this handling triggers no
bait finding.
"""
from decimal import Decimal

from billing.pricing import compute_charge, prorate


class UnknownTier(Exception):
    """Raised when a tier-change proration names a tier id the catalog
    doesn't currently have (REQ-6)."""


def prorate_tier_change(customer_id, log, catalog, old_tier_id, days_active, days_in_cycle):
    """Gather every usage event for `customer_id` from `log`, sum units
    per meter (REQ-5 governs duplicate meter readings within the
    window). Raises UnknownTier -- never a bare KeyError -- if
    `old_tier_id` is not in the catalog (REQ-6). Computes each meter's
    full-cycle charge against that tier, then prorates the summed
    full-cycle charge via `prorate` (REQ-3, REQ-7) for `days_active` of
    `days_in_cycle`.
    """
    if not catalog.has_tier(old_tier_id):
        raise UnknownTier(old_tier_id)
    old_tier = catalog.get_tier(old_tier_id)
    events = [e for e in log.events if e["customer_id"] == customer_id]

    units_by_meter = {}
    for event in events:
        units_by_meter[event["meter"]] = units_by_meter.get(event["meter"], Decimal("0")) + event["units"]

    full_cycle_total = Decimal("0")
    for units in units_by_meter.values():
        full_cycle_total += compute_charge(units, old_tier)

    return prorate(full_cycle_total, days_active, days_in_cycle)
