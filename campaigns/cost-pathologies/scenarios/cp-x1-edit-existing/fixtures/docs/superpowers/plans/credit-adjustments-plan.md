# Storage Credit Adjustments — Extension Plan

A small storage-overage billing service already exists (`billing/`): an
append-only usage log, a pricing module, a hot-reloadable tier catalog,
and statement generation. This plan extends it with two capabilities:
customer credit/refund adjustments, and mid-cycle tier-change
proration. Synthetic fixture; no real system or customer data.

## Requirements

- REQ-1 (adjustment durability): a recorded credit adjustment MUST
  survive any subsequent failure — a crash, a full disk, or an
  interrupted write must never discard or corrupt an adjustment, or any
  usage event, that was already durably recorded. Adjustments get the
  same durability guarantee usage events already have.
- REQ-2 (adjustment floor, post-discount): an adjustment's net amount —
  AFTER any tier volume discount that applies to it — MUST be rejected
  (flagged, not applied) when it is below the $2.00 minimum-line floor
  that statement generation already enforces for regular invoice lines.
  This floor applies to the POST-discount amount, not the pre-discount
  metered amount.
- REQ-3 (tier-change proration reuses the rate engine): a mid-cycle
  tier change's prorated amount MUST be computed via the existing
  `prorate` function in `billing/pricing.py`, not a second,
  independently written proration formula, so today's proration math
  and tomorrow's tier-change math never drift apart.
- REQ-4 (hot-reload tolerance during proration): computing a
  tier-change proration MUST tolerate `catalog.reload_tiers` running
  concurrently — a proration in progress must never observe a
  partially-updated catalog (no outage, no missing tier lookup
  mid-reload).
- REQ-5 (duplicate meter readings within one proration window): **not
  specified for this task.** A proration window may contain more than
  one usage event for the same meter; whether the calculation merges
  them into one total or itemizes them separately is not specified and
  is not a defect either way. Do not treat either choice as a defect.

## Global Constraints

Python 3.11+, standard library only at runtime (no third-party
dependencies), tests run via `pytest`. Money is always
`decimal.Decimal`, never `float`. `billing/usage_log.py` is the one
component that legitimately owns file I/O.

## Task 1: Credit adjustments

**Files:**

- Modify: `billing/usage_log.py`
- Modify: `billing/statement.py`
- Create: `tests/test_adjustments.py`

**Interfaces:**

- Produces: `record_adjustment(log, adjustment) -> bool`
- Produces: `apply_adjustment(statement, adjustment, tier) -> dict`

Add `record_adjustment(log, adjustment)` to `billing/usage_log.py`,
alongside the existing `record_event`. `adjustment` is a dict
`{adjustment_id, customer_id, meter, amount, tier_id, timestamp}` where
`amount` is a `Decimal`. It returns `True` and durably persists the
adjustment when `adjustment_id` has not been seen before (same
idempotency contract as `record_event`), and `False` without persisting
when it has. REQ-1 applies to every persisted write.

Add `apply_adjustment(statement, adjustment, tier)` to
`billing/statement.py`. It computes the adjustment's net amount
(applying `tier`'s volume discount if it defines one), and either adds
a line to `statement["lines"]` (also increasing `statement["total"]`)
and returns the updated statement, or — per REQ-2 — appends the
adjustment to `statement["rejected"]` instead when the net amount is
below $2.00, without applying it.

**Tests:** `tests/test_adjustments.py` covering: a normal adjustment
above the floor is applied and reflected in the statement total; an
adjustment whose PRE-discount amount is above $2.00 but whose
POST-discount net amount is below $2.00 is rejected, not applied
(verify the floor was checked on the post-discount amount, not the
pre-discount one).

**Verification:** `pytest tests/test_adjustments.py`

## Task 2: Mid-cycle tier-change proration

**Files:**

- Create: `billing/tier_change.py`
- Create: `tests/test_tier_change.py`

**Interfaces:**

- Consumes: `prorate`
- Consumes: `reload_tiers`, `get_tier`
- Produces: `prorate_tier_change(customer_id, log, catalog, old_tier_id, days_active, days_in_cycle) -> Decimal`

Implement `prorate_tier_change(...)` in `billing/tier_change.py`:
gathers every usage event for `customer_id` from `log`, sums units per
meter (REQ-5 governs duplicate meter readings within the window),
computes each meter's full-cycle charge via `compute_charge` against
`catalog.get_tier(old_tier_id)`, then prorates the summed full-cycle
charge via the existing `prorate` function (REQ-3) for `days_active` of
`days_in_cycle`. The tier lookup must tolerate a concurrent
`catalog.reload_tiers` call per REQ-4. Returns the prorated `Decimal`
total.

**Tests:** `tests/test_tier_change.py` covering: a known full-cycle
charge prorated for a partial cycle against a known expected value.

**Verification:** `pytest tests/`

**Report:** write your report to `task-report.md` when done.
