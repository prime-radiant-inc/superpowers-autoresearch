"""Rate computation and proration for storage-overage billing, extended
with a zero-length-cycle guard (REQ-7 of credit-adjustments-plan.md's
Task 2).

CONSTRUCTED OUTCOME TREE (campaigns/cost-pathologies/
test_cp_x1_edit_existing.py) -- "fixed": `prorate` now quantizes to
cents with an explicit rounding mode -- DEBATABLE-2 is caught.
"""
from decimal import ROUND_HALF_UP, Decimal


def compute_charge(units, tier):
    """`tier` is a dict with at least `rate_per_unit` (a Decimal). Returns
    the metered charge for `units` at that rate.
    """
    return units * tier["rate_per_unit"]


def prorate(charge, days_active, days_in_cycle):
    """Scale `charge` by `days_active / days_in_cycle`, for a tier change
    mid-billing-cycle. Both `days_active` and `days_in_cycle` are ints.
    Raises ValueError for a zero-length cycle (REQ-7) rather than
    letting a bare ZeroDivisionError propagate. Rounded to the cent,
    half-up, so proration never returns a value with more precision than
    money should carry.
    """
    if days_in_cycle == 0:
        raise ValueError("days_in_cycle must be greater than 0")
    scaled = charge * Decimal(days_active) / Decimal(days_in_cycle)
    return scaled.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
