"""Rate computation and proration for storage-overage billing, extended
with a zero-length-cycle guard (REQ-7 of credit-adjustments-plan.md's
Task 2).

CONSTRUCTED OUTCOME TREE (campaigns/cost-pathologies/
test_cp_x1_edit_existing.py) -- "carried_forward": the REQ-7 guard was
added (a plain divide-by-zero check, unrelated to rounding), but the
unquantized division below it is untouched from the pre-existing
(broken) starting code -- DEBATABLE-2 escapes.
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
    Raises ValueError for a zero-length cycle (REQ-7) rather than
    letting a bare ZeroDivisionError propagate.
    """
    if days_in_cycle == 0:
        raise ValueError("days_in_cycle must be greater than 0")
    return charge * Decimal(days_active) / Decimal(days_in_cycle)
