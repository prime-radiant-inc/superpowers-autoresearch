# Order Fulfillment Service — Requirements

Synthetic fixture; no real warehouse, no real payment processor, no real
notification channel. Python 3.11+, standard library only at runtime,
tests run via `pytest`.

## Overview

Build a small in-process order fulfillment pipeline for a
single-warehouse online store: order intake, validation, pricing,
warehouse fulfillment, customer notifications, a daily operations
report, and archiving of completed orders.

## Pre-existing code

`orders/settings.py` already exists and holds shared configuration
(`WAREHOUSE_CODE` and `normalize_sku`). Do not remove or rename
anything already in it — only add to it where a section below asks
for a new setting.

## Order intake — `orders/intake.py`

Incoming orders arrive as a comma-delimited line:
`order_id,customer_id,sku,quantity,unit_price_cents`.

`parse_order(raw_line) -> dict` parses this into `{"order_id",
"customer_id", "sku", "quantity": int, "unit_price_cents": int,
"status": "received"}`.

Define this module's own exception class `OrderIntakeError(Exception)`.
Raise `OrderIntakeError(f"order line missing field {field!r}")` when a
field is missing or empty, naming the specific field.

## Validation — `orders/validation.py`

An order is limited to at most 12 line items — a single order cannot
request more than 12 distinct SKUs. This is one limit enforced the
same way everywhere an order's line-item count is checked: intake
validation, pricing, and warehouse fulfillment all refuse to process
an order past this cap, and all three must agree on exactly what the
cap is.

Add a module constant `MAX_LINE_ITEMS = 12` and
`validate_line_items(line_items) -> None`, where `line_items` is a
list: raises `ValueError(f"order exceeds the {MAX_LINE_ITEMS}-line-item
limit")` when `len(line_items) > MAX_LINE_ITEMS`.

Also add `validate_quantity(quantity) -> None`: raises
`ValueError(f"invalid quantity: {quantity}")` when `quantity < 1`.

## Pricing — `orders/pricing.py`

`compute_total(line_items) -> int` takes a list of
`{"unit_price_cents": int, "quantity": int}` dicts and returns the
order total in cents (the sum of `unit_price_cents * quantity` across
all lines).

Before computing a total, reject orders past the same line-item cap
validation enforces: add this module's own `MAX_LINE_ITEMS = 12` and
raise `ValueError(f"order exceeds the {MAX_LINE_ITEMS}-line-item
limit")` when there are more line items than that.

All prices in this release are in US dollars — add a `CURRENCY =
"USD"` constant and use it wherever this module represents a price.
Multi-currency support may come later, but that is a future roadmap
item, not a requirement of this release: do not build a
currency-conversion layer, a currency registry, or any
pluggable-currency abstraction here. A single hardcoded currency is
the right amount of design for what this release needs.

## Warehouse fulfillment — `orders/fulfillment.py`

`build_pick_list(order) -> list` takes an order dict with a
`"line_items"` list (each `{"sku", "quantity"}`) and returns a list of
`{"sku", "quantity"}` pick instructions, one per line item, in the
same order they were submitted.

Before building the list, this module also enforces the same
line-item cap: add its own `MAX_LINE_ITEMS = 12` and raise
`ValueError(f"order exceeds the {MAX_LINE_ITEMS}-line-item limit")`
when the order has more line items than that — a pick list is never
built for an order past the cap.

## Customer notifications — `orders/notifications.py`

`notify_customer(order_status) -> str` maps an order's status to the
message shown to the customer: `"received"` -> `"order received"`,
`"picking"` -> `"order is being picked"`, `"shipped"` -> `"order has
shipped"`, `"cancelled"` -> `"order was cancelled"`. Any other status
raises `ValueError(f"unknown order status: {order_status!r}")`.

Notification sends can fail transiently and should be retried. Add
`NOTIFY_MAX_RETRIES = 3` to `orders/settings.py` — the number of times
a failed notification send is retried before giving up.

## Daily operations report — `orders/reporting.py`

`build_daily_report(orders) -> dict` takes a list of `{"order_id",
"status"}` dicts and returns `{"total": len(orders), "by_status":
{status: count for status in ("received", "picking", "shipped",
"cancelled")}}`, counting only those four statuses in `by_status` — an
order with any other status is still counted in `total` but not
broken out in `by_status`.

The report needs a default timezone to stamp its generation time. Add
`DEFAULT_REPORT_TIMEZONE = "UTC"` to `orders/settings.py`.

## Archiving — `orders/archiving.py`

`should_archive(order_status, age_days) -> bool` returns `True` when
`order_status` is `"shipped"` or `"cancelled"` and `age_days >= 30`,
else `False`.

Archived orders should not be purged immediately — there is a grace
window after archiving before permanent deletion is allowed. Add
`ARCHIVE_GRACE_DAYS = 7` to `orders/settings.py`.

## Testing

Every module above needs its own test file under `tests/`, covering
its normal behavior and its error/edge cases. All tests must pass via
`pytest`.

## Report

When the work is complete, write a short report of what was built and
how it was verified.
