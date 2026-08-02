"""Rate computation and proration for storage-overage billing.

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
    Rounded to the cent, half-up, so proration never returns a value
    with more precision than money should carry.
    """
    scaled = charge * Decimal(days_active) / Decimal(days_in_cycle)
    return scaled.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
