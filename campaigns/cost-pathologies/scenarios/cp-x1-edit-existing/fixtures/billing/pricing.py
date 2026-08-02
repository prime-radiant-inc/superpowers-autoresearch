"""Rate computation and proration for storage-overage billing.

Money is always decimal.Decimal, never float, per the service's Global
Constraints (float arithmetic on money amounts introduces rounding
drift). Synthetic fixture; no real system.
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
