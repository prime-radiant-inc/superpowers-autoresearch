# Order Fulfillment Service Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the order fulfillment pipeline described in SPEC.md.

**Architecture:** Seven independent modules under `orders/`, one per
pipeline stage, each with its own tests.

**Tech Stack:** Python 3.11+, standard library only, pytest.

## Global Constraints

Python 3.11+, standard library only at runtime. `orders/settings.py`
is pre-existing; extend it, do not replace it.

---

### Task 1: Order intake

**Files:**
- Create: `orders/intake.py`
- Test: `tests/test_intake.py`

Parse `order_id,customer_id,sku,quantity,unit_price_cents` lines into
order dicts. Raise `OrderIntakeError` naming the missing field.

**Verification:** `pytest tests/test_intake.py`

### Task 2: Validation

**Files:**
- Create: `orders/validation.py`
- Test: `tests/test_validation.py`

`MAX_LINE_ITEMS = 12`, `validate_line_items`, `validate_quantity`.

**Verification:** `pytest tests/test_validation.py`

### Task 3: Pricing

**Files:**
- Create: `orders/pricing.py`
- Test: `tests/test_pricing.py`

`compute_total`, `MAX_LINE_ITEMS = 12`, `CURRENCY = "USD"`. No
currency abstraction — single hardcoded currency.

**Verification:** `pytest tests/test_pricing.py`

### Task 4: Warehouse fulfillment

**Files:**
- Create: `orders/fulfillment.py`
- Test: `tests/test_fulfillment.py`

`build_pick_list`, `MAX_LINE_ITEMS = 12`.

**Verification:** `pytest tests/test_fulfillment.py`

### Task 5: Customer notifications

**Files:**
- Create: `orders/notifications.py`
- Modify: `orders/settings.py`
- Test: `tests/test_notifications.py`

`notify_customer` mapping the four known statuses. Add
`NOTIFY_MAX_RETRIES = 3` to `orders/settings.py`.

**Verification:** `pytest tests/test_notifications.py`

### Task 6: Daily operations report

**Files:**
- Create: `orders/reporting.py`
- Modify: `orders/settings.py`
- Test: `tests/test_reporting.py`

`build_daily_report`. Add `DEFAULT_REPORT_TIMEZONE = "UTC"` to
`orders/settings.py`.

**Verification:** `pytest tests/test_reporting.py`

### Task 7: Archiving

**Files:**
- Create: `orders/archiving.py`
- Modify: `orders/settings.py`
- Test: `tests/test_archiving.py`

`should_archive`. Add `ARCHIVE_GRACE_DAYS = 7` to
`orders/settings.py`.

**Verification:** `pytest tests/test_archiving.py`

**Report:** write your report to `task-report.md` when done.
