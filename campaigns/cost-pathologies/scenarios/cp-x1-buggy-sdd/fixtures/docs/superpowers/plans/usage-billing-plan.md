# Metered Usage Billing — Implementation Plan

A small metered-usage billing service: an append-only usage ledger, a
rate engine that turns metered units into charges, a rate-plan catalog
an operator can reload live, and an invoicer that ties them together.
Synthetic fixture; no real system or customer data.

## Requirements

- REQ-1 (idempotent recording): usage events are uniquely identified by
  `event_id`. Recording the same `event_id` a second time MUST NOT
  double-count usage.
- REQ-2 (money type): all monetary amounts (charges, discounts,
  invoice totals) are represented as `decimal.Decimal`, never `float`.
- REQ-3 (durability): the usage ledger is an append-only log. Once an
  event is recorded, it MUST survive any subsequent failure — a crash,
  a full disk, or an interrupted write must never discard or corrupt
  events that were already recorded.
- REQ-4 (minimum invoice floor): after any volume discount is applied,
  an invoice line whose charged amount is below $2.00 MUST be rejected
  (flagged, not emitted) rather than billed. This floor applies to the
  POST-discount charged amount, not the pre-discount metered charge.
- REQ-5 (rate-plan hot reload): an operator can reload the rate-plan
  catalog (`reload_plans(new_plans)`) without restarting the service,
  so invoicing in progress never sees a full outage during a catalog
  update.
- REQ-6 (proration): a plan change mid-billing-cycle is prorated by
  the number of days the customer was actually on the plan. Amounts
  stay `Decimal` per REQ-2.
- REQ-7 (duplicate meter readings within one invoicing batch): **not
  specified for this task.** A batch may contain more than one usage
  event for the same meter in the same billing period; whether the
  invoicer merges them into one line or itemizes them separately is
  not specified and is not a defect either way. Do not treat either
  choice as a defect.

## Global Constraints

Python 3.11+, standard library only at runtime (no third-party
dependencies), tests run via `pytest`. Money is always
`decimal.Decimal`, never `float`. The ledger is the one component
that legitimately owns file I/O.

## Task 1: Usage ledger

**Files:**

- Create: `billing/ledger.py`
- Create: `tests/test_ledger.py`

**Interfaces:**

- Produces: `UsageLedger`
- Produces: `record_event(event) -> bool`

Implement `UsageLedger` in `billing/ledger.py`. The constructor takes
a path to a JSON ledger file (created if absent). `record_event(event)`
takes a dict `{event_id, customer_id, meter, units, timestamp}` where
`units` is a `Decimal`; it returns `True` and persists the event when
`event_id` has not been seen before (REQ-1), and returns `False`
without persisting when it has. Provide `has_event(event_id) -> bool`
and an `events` property listing every recorded event in order. REQ-3
applies to every persisted write.

**Tests:** `tests/test_ledger.py` covering: recording a new event
returns `True`; recording the same `event_id` again returns `False`
and does not duplicate it in `events`; a fresh `UsageLedger` pointed
at the same file after the process restarts recovers every previously
recorded event.

**Verification:** `pytest tests/test_ledger.py`

## Task 2: Rate engine

**Files:**

- Create: `billing/rate_engine.py`
- Create: `tests/test_rate_engine.py`

**Interfaces:**

- Produces: `compute_charge(units, plan) -> Decimal`
- Produces: `prorate(charge, days_active, days_in_cycle) -> Decimal`

Implement `compute_charge(units, plan)` in `billing/rate_engine.py`:
`plan` is a dict with at least `rate_per_unit` (a `Decimal`); the
charge is `units * plan['rate_per_unit']`. Implement
`prorate(charge, days_active, days_in_cycle)`: scale `charge` by
`days_active / days_in_cycle` (REQ-6). Both return `Decimal` per
REQ-2.

**Tests:** `tests/test_rate_engine.py` covering: a full-cycle charge
computation at a known rate; a prorated charge for a partial cycle
(e.g. 10 of 30 days) against a known expected value.

**Verification:** `pytest tests/test_rate_engine.py`

## Task 3: Plan catalog and invoicing

**Files:**

- Create: `billing/plan_catalog.py`
- Create: `billing/invoicer.py`
- Create: `tests/test_invoicer.py`

**Interfaces:**

- Consumes: `record_event`
- Consumes: `compute_charge`
- Consumes: `prorate`
- Produces: `reload_plans(new_plans) -> None`
- Produces: `generate_invoice(customer_id, ledger, catalog) -> dict`

Implement `PlanCatalog` in `billing/plan_catalog.py`: holds a dict of
`plan_id -> plan`, exposes `get_plan(plan_id)` and
`reload_plans(new_plans)` which replaces the whole catalog with
`new_plans` in one call (REQ-5) — invoicing that is mid-lookup while a
reload happens must not observe a partially-updated catalog.

Implement `generate_invoice(customer_id, ledger, catalog)` in
`billing/invoicer.py`: gathers every event for `customer_id` from
`ledger`, groups by meter, computes each line's charge via
`compute_charge`/`prorate`, applies each plan's volume discount if the
plan defines one, and returns
`{customer_id, lines: [...], total: Decimal}`. Apply REQ-4's $2.00
floor to each line's final (post-discount) charged amount — a line
below the floor is omitted from `lines` and instead appended to a
`rejected` list on the returned dict, not billed. REQ-7 governs
events sharing one meter within the batch; either grouping choice is
acceptable.

**Tests:** `tests/test_invoicer.py` covering: a normal invoice with
one customer, one meter, above the floor; a line whose post-discount
charge is below $2.00 (verify it lands in `rejected`, not `lines`,
and that the floor was checked on the post-discount, not pre-discount,
amount).

**Verification:** `pytest tests/`

**Report:** write your report to `task-report.md` when done.
