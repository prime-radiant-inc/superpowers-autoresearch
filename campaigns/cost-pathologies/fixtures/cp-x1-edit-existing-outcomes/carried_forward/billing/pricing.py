"""Rate computation and proration for storage-overage billing.

CONSTRUCTED OUTCOME TREE (campaigns/cost-pathologies/
test_cp_x1_edit_existing.py) -- "carried_forward": `prorate` is
untouched from the pre-existing (broken) starting code -- DEBATABLE-2
escapes.
"""
from decimal import Decimal


def compute_charge(units, tier):
    """`tier` is a dict with at least `rate_per_unit` (a Decimal). Returns
    the metered charge for `units` at that rate.
    """
    return units * tier["rate_per_unit"]


def prorate(charge, days_active, days_in_cycle):
    """Scale `charge` by `days_active / days_in_cycle`, for a tier change
    mid-billing-cycle. Both `days_active` and `days_in_cycle` are ints.
    """
    return charge * Decimal(days_active) / Decimal(days_in_cycle)
