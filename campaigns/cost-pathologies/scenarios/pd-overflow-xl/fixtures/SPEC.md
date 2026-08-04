# Order Fulfillment, Operations & Reconciliation Service — Requirements

Synthetic fixture; no real warehouse, no real payment processor, no real
carrier, no real notification channel, no real accounting system. Python
3.11+, standard library only at runtime, tests run via `pytest`.

## Overview

Build a multi-warehouse order fulfillment, operations, and
import/export-reconciliation service for an online store operating three
regional warehouses. Three cohesive areas:

- **Order pipeline:** order intake, validation, discount pricing,
  warehouse allocation, shipping cost estimation, warehouse fulfillment,
  backorder handling, customer notifications, loyalty points, returns
  intake, refund processing, a daily operations report, archiving, order
  cancellation, and delivery SLA estimation.
- **Operations & administration:** staff roles and permissions, an audit
  log, inventory adjustments, support tickets, API rate limits,
  warehouse shift coverage, manual order overrides, and an operations
  dashboard.
- **Import/export & reconciliation:** bulk CSV order import, marketplace
  export feeds, warehouse count reconciliation, accounting ledger sync,
  carrier manifests, duplicate order detection, a vendor restock feed,
  and vendor restock lead times.

## Pre-existing code

`orders/settings.py` already exists and holds shared configuration:
`WAREHOUSE_CODE` (the store's original single-warehouse default),
`WAREHOUSES` (the list of all three warehouse codes now in service), and
`normalize_sku`. Do not remove or rename anything already in it — only
add to it where a section below asks for a new setting.

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
request more than 12 distinct SKUs. This is one limit enforced the same
way everywhere an order's line-item count is checked: intake validation,
pricing, warehouse allocation, warehouse fulfillment, a manually
overridden reprocess (operations), and a bulk CSV import (import/export)
all refuse to process an order past this cap, and all six must agree on
exactly what the cap is.

Add a module constant `MAX_LINE_ITEMS = 12` and
`validate_line_items(line_items) -> None`, where `line_items` is a
list: raises `ValueError(f"order exceeds the {MAX_LINE_ITEMS}-line-item
limit")` when `len(line_items) > MAX_LINE_ITEMS`.

Add `validate_quantity(quantity) -> None`: raises
`ValueError(f"invalid quantity: {quantity}")` when `quantity < 1`.

Every SKU carries a category, encoded as a three-letter prefix before a
dash: `GEN` (general merchandise), `FRZ` (frozen / cold-chain), or `HAZ`
(hazardous materials) — e.g. `"GEN-1234"`. Add
`validate_sku_category(sku) -> str` returning the category name
(`"general"`, `"frozen"`, or `"hazardous"`) for a recognized prefix, and
raising `ValueError(f"unrecognized SKU category prefix: {prefix!r}")`
for any other prefix. Warehouse allocation (below) uses the category to
decide which warehouses can fulfill a given SKU.

Customer IDs must match this store's own format: 6 to 12 alphanumeric
characters, no other symbols. Add `validate_customer_id_format(customer_id)
-> None`, raising `ValueError(f"invalid customer id format:
{customer_id!r}")` when it doesn't match.

## Discount pricing tiers — `orders/discounts.py`

Orders qualify for a volume discount based on their subtotal before
shipping, in five tiers:

| Subtotal (cents)     | Discount |
|-----------------------|----------|
| up to 5,000           | 0%       |
| 5,001 – 10,000        | 5%       |
| 10,001 – 25,000       | 10%      |
| 25,001 – 50,000       | 15%      |
| 50,001 and above      | 20%      |

Add `discount_rate_for_subtotal(subtotal_cents) -> int` returning the
whole-number percent discount (`0`, `5`, `10`, `15`, or `20`) for the
tier the subtotal falls into — a subtotal exactly on a tier's upper
boundary belongs to that lower tier (e.g. `5000` is `0%`, `5001` is
`5%`). Raise `ValueError(f"invalid subtotal: {subtotal_cents}")` when
`subtotal_cents < 0`.

## Pricing — `orders/pricing.py`

`compute_total(line_items) -> int` takes a list of
`{"unit_price_cents": int, "quantity": int}` dicts, computes the
pre-discount subtotal in cents (the sum of `unit_price_cents *
quantity` across all lines), applies the volume discount from
`orders/discounts.py` for that subtotal, and returns the final total in
cents rounded down to the nearest cent (integer floor division).

Before computing a total, reject orders past the same line-item cap
validation enforces: add this module's own `MAX_LINE_ITEMS = 12` and
raise `ValueError(f"order exceeds the {MAX_LINE_ITEMS}-line-item
limit")` when there are more line items than that.

All prices in this release are in US dollars — add a `CURRENCY = "USD"`
constant and use it wherever this module represents a price.
Multi-currency support may come later, but that is a future roadmap
item, not a requirement of this release: do not build a
currency-conversion layer, a currency registry, or any
pluggable-currency abstraction here. A single hardcoded currency is the
right amount of design for what this release needs.

## Warehouse allocation — `orders/allocation.py`

The store ships from three warehouses, each with different handling
capabilities:

| Warehouse | Can handle                        |
|-----------|------------------------------------|
| `WH-1`    | general, frozen, hazardous          |
| `WH-2`    | general, frozen                     |
| `WH-3`    | general only                        |

Each of the store's three shipping zones has a preferred (nearest)
warehouse:

| Zone | Preferred warehouse |
|------|----------------------|
| `Z1` | `WH-1`               |
| `Z2` | `WH-2`               |
| `Z3` | `WH-3`               |

`allocate_warehouse(zone, sku_categories) -> str` takes a zone code and
a list of the SKU categories present on the order (from
`orders/validation.py`'s `validate_sku_category`), and returns the
warehouse code that should fulfill the order: the zone's preferred
warehouse if it can handle every category present, otherwise `"WH-1"`
(the only warehouse that handles all three categories, so it is always a
safe fallback). Raise `ValueError(f"unknown shipping zone: {zone!r}")`
for a zone not in the table above.

Before allocating, this module also enforces the same line-item cap: add
its own `MAX_LINE_ITEMS = 12` and raise `ValueError(f"order exceeds the
{MAX_LINE_ITEMS}-line-item limit")` when the order has more line items
than that — an order past the cap is never allocated to a warehouse.

## Shipping cost — `orders/shipping.py`

Shipping cost depends on package weight and destination zone. Weight
brackets: `light` is up to 2,000 grams, `medium` is 2,001–10,000 grams,
`heavy` is 10,001–25,000 grams. A shipment heavier than 25,000 grams is
not supported by any carrier this release integrates with.

| Zone | light | medium | heavy |
|------|-------|--------|-------|
| `Z1` | 500¢  | 900¢   | 1500¢ |
| `Z2` | 700¢  | 1200¢  | 2000¢ |
| `Z3` | 900¢  | 1600¢  | 2600¢ |

`compute_shipping_cost(weight_grams, zone) -> int` returns the cost in
cents for the given weight and zone. Raise `ValueError(f"shipment of
{weight_grams}g exceeds the maximum supported weight of 25000g")` for an
over-limit shipment, and `ValueError(f"unknown shipping zone:
{zone!r}")` for a zone not in the table above.

## Warehouse fulfillment — `orders/fulfillment.py`

`build_pick_list(order) -> list` takes an order dict with a
`"line_items"` list (each `{"sku", "quantity"}`) and returns a list of
`{"sku", "quantity"}` pick instructions, one per line item, in the same
order they were submitted.

Before building the list, this module also enforces the same line-item
cap: add its own `MAX_LINE_ITEMS = 12` and raise `ValueError(f"order
exceeds the {MAX_LINE_ITEMS}-line-item limit")` when the order has more
line items than that — a pick list is never built for an order past the
cap.

Not every SKU on a pick list is in stock at the assigned warehouse. Add
`flag_backorder_items(pick_list, available_stock) -> list`, where
`available_stock` is a `{sku: quantity_on_hand}` dict: returns the
subset of `pick_list` entries whose requested quantity exceeds the
quantity on hand for that SKU (a SKU missing from `available_stock`
entirely counts as zero on hand). These flagged items feed backorder
scheduling below.

## Backorder handling — `orders/backorders.py`

An item flagged for backorder is rechecked on a fixed schedule rather
than continuously: 1 day after the first attempt, 3 days after the
second, and 7 days after the third. After 3 attempts with no stock
available, the store gives up on that item.

Add `BACKORDER_MAX_ATTEMPTS = 3` and
`schedule_backorder_retry(attempt_number) -> int`, returning the number
of days to wait before the next recheck for attempts 1 through 3 (`1`,
`3`, or `7`). Raise `ValueError(f"backorder exhausted after
{BACKORDER_MAX_ATTEMPTS} attempts")` when `attempt_number >=
BACKORDER_MAX_ATTEMPTS`.

## Customer notifications — `orders/notifications.py`

`notify_customer(order_status) -> str` maps an order's status to the
message shown to the customer: `"received"` -> `"order received"`,
`"picking"` -> `"order is being picked"`, `"shipped"` -> `"order has
shipped"`, `"cancelled"` -> `"order was cancelled"`. Any other status
raises `ValueError(f"unknown order status: {order_status!r}")`.

Notification sends can fail transiently and should be retried. Add
`NOTIFY_MAX_RETRIES = 3` to `orders/settings.py` — the default number of
times a failed notification send is retried before giving up, for any
channel not given its own tuned value below.

Two of this store's three notification channels need a different retry
count than the default: email gets more attempts because it's the
cheapest channel to retry, SMS gets the most because delivery receipts
are unreliable, and push notifications get fewer because a stale push is
worse than a missed one. Add `CHANNEL_RETRY_OVERRIDES = {"email": 3,
"sms": 5, "push": 2}` and `retries_for_channel(channel) -> int`,
returning the channel's entry from that table when present, otherwise
falling back to `orders/settings.py`'s `NOTIFY_MAX_RETRIES`.

## Loyalty points — `orders/loyalty.py`

Customers earn loyalty points per dollar spent, at a multiplier that
depends on their membership tier:

| Tier       | Points per dollar |
|------------|--------------------|
| `bronze`   | 1                  |
| `silver`   | 2                  |
| `gold`     | 3                  |
| `platinum` | 5                  |

Add `LOYALTY_POINT_MULTIPLIERS` (mapping tier name to multiplier) and
`points_for_purchase(customer_tier, subtotal_cents) -> int`, returning
`(subtotal_cents // 100) * multiplier`. Raise `ValueError(f"unknown
loyalty tier: {customer_tier!r}")` for a tier not in the table.

## Returns intake — `orders/returns.py`

Customers may request a return within a limited window after their
order shipped. Add `RETURN_WINDOW_DAYS = 30` to `orders/settings.py` —
the number of days after an order ships during which a return may be
requested.

Add `is_within_return_window(shipped_date, request_date) -> bool` (both
`datetime.date` objects), returning `True` when `(request_date -
shipped_date).days <= RETURN_WINDOW_DAYS`, else `False`.

A return request must give one of four reason codes: `"defective"`,
`"wrong_item"`, `"no_longer_needed"`, or `"damaged_in_transit"`. Add
`validate_return_reason(reason) -> None`, raising `ValueError(f"unknown
return reason: {reason!r}")` for any other value.

## Refund processing — `orders/refunds.py`

A returned item may be subject to a restocking fee, based on how long
the customer held it before returning it:

| Days since delivery | Restocking fee |
|----------------------|-----------------|
| 0 – 7                | 0%              |
| 8 – 14               | 10%             |
| 15 – 21              | 20%             |
| 22 – 30              | 30%             |

Add `RESTOCKING_FEE_TIERS` (encoding the table above) and
`compute_refund(order_total_cents, days_since_delivery) -> int`,
returning `order_total_cents` minus that tier's fee percentage (integer
floor). A `days_since_delivery` of more than 30 — past this store's
`RETURN_WINDOW_DAYS` — is not refundable at all: raise `ValueError(f"return
window of {RETURN_WINDOW_DAYS} days has elapsed")`.

An order can only be refunded once. Add `process_refund(order) -> dict`,
where `order` is a dict with a `"refund_status"` key (`"none"` or
`"refunded"`): raises `ValueError("order has already been refunded")`
when `order["refund_status"] == "refunded"`, otherwise returns a copy of
`order` with `"refund_status"` set to `"refunded"`.

## Daily operations report — `orders/reporting.py`

`build_daily_report(orders) -> dict` takes a list of `{"order_id",
"status", "warehouse"}` dicts and returns:

```python
{
    "total": <int>,
    "by_status": {status: count for status in ("received", "picking", "shipped", "cancelled")},
    "by_warehouse": {code: count for code in orders.settings.WAREHOUSES},
    "returns_rate": <float>,
}
```

`by_status` counts only those four statuses — an order with any other
status is still counted in `total` but not broken out in `by_status`.
`by_warehouse` counts only orders whose `"warehouse"` field is one of
`orders.settings.WAREHOUSES` — an order missing that field, or naming a
warehouse not in that list, is still counted in `total` and `by_status`
but excluded from `by_warehouse`. `returns_rate` is the fraction (a
float between 0.0 and 1.0) of orders in the list whose status is
`"cancelled"`, out of `total` — `0.0` when the list is empty.

The report needs a default timezone to stamp its generation time. Add
`DEFAULT_REPORT_TIMEZONE = "UTC"` to `orders/settings.py`.

## Archiving — `orders/archiving.py`

`should_archive(order_status, age_days) -> bool` returns `True` when
`order_status` is `"shipped"`, `"cancelled"`, or `"refunded"`, and
`age_days >= 30`, else `False`.

Archived orders should not be purged immediately — there is a grace
window after archiving before permanent deletion is allowed. Add
`ARCHIVE_GRACE_DAYS = 7` to `orders/settings.py`.

Add `purge_eligible(archived_date, today_date) -> bool` (both
`datetime.date` objects), returning `True` when `(today_date -
archived_date).days >= ARCHIVE_GRACE_DAYS`, else `False` — an archived
order is not eligible for permanent deletion until its grace window has
elapsed.

## Order cancellation — `orders/cancellation.py`

A customer can cancel an order only before it ships. Add
`cancel_order(order_status) -> str`, returning `"cancelled"` when
`order_status` is `"received"` or `"picking"`. Raise
`ValueError(f"cannot cancel an order with status {order_status!r}")` for
any other status (in particular, `"shipped"` and already-`"cancelled"`
orders cannot be cancelled again).

## Delivery SLA — `orders/sla.py`

The store promises a delivery window based on shipping speed and zone:

| Zone | `standard` | `express` |
|------|------------|-----------|
| `Z1` | 5 days     | 2 days    |
| `Z2` | 7 days     | 3 days    |
| `Z3` | 10 days    | 4 days    |

Add `PROMISED_DELIVERY_DAYS` (encoding the table above) and
`promised_delivery_days(speed, zone) -> int`, returning the promised
number of days for that speed/zone pair. Raise `ValueError(f"unknown
shipping speed: {speed!r}")` for a speed other than `"standard"` or
`"express"`.

## Staff roles & permissions — `orders/staff_roles.py`

Store staff act under one of four roles, each permitted a fixed set of
actions:

| Role         | Allowed actions                          |
|--------------|-------------------------------------------|
| `viewer`     | view                                       |
| `agent`      | view, edit                                 |
| `supervisor` | view, edit, cancel, refund                 |
| `admin`      | view, edit, cancel, refund, override       |

Add `STAFF_ROLE_PERMISSIONS` (mapping role name to the set of actions
above) and `role_can_perform(role, action) -> bool`, returning whether
`action` is among that role's permitted actions (an unrecognized
*action* for a known role simply returns `False` — it is not an error).
Raise `ValueError(f"unknown staff role: {role!r}")` for a role not in
the table.

## Audit log — `orders/audit_log.py`

Every audited event in this system is classified into one of three
severities:

| Event type          | Severity   |
|----------------------|------------|
| `order_edited`       | `info`     |
| `manual_override`     | `warning`  |
| `refund_reversed`     | `critical` |

Add `AUDIT_EVENT_SEVERITY` (encoding the table above) and
`classify_audit_event(event_type) -> str`, returning the severity for a
known event type. Raise `ValueError(f"unknown audit event type:
{event_type!r}")` for any other value.

Audit entries are not kept forever. Add `AUDIT_LOG_RETENTION_DAYS = 90`
to `orders/settings.py` — the number of days an audit entry is retained
before it is eligible for purge.

Add `is_within_retention(event_date, today_date) -> bool` (both
`datetime.date` objects), returning `True` when `(today_date -
event_date).days <= AUDIT_LOG_RETENTION_DAYS`, else `False`.

## Inventory adjustments — `orders/inventory_adjustments.py`

Staff can adjust recorded stock levels by hand, for one of four reasons:
`"damaged"`, `"miscount"`, `"theft"`, or `"found_stock"`. Add
`validate_adjustment_reason(reason) -> None`, raising `ValueError(f"unknown
adjustment reason: {reason!r}")` for any other value.

The size of an adjustment determines who must approve it:

| Adjustment quantity (units) | Approval level required |
|-------------------------------|----------------------------|
| 1 – 10                         | `none`                     |
| 11 – 50                        | `supervisor`                |
| 51 and above                   | `admin`                     |

Add `approval_level_for_adjustment(quantity) -> str`, returning
`"none"`, `"supervisor"`, or `"admin"` for the tier `quantity` falls
into. Raise `ValueError(f"invalid adjustment quantity: {quantity}")`
when `quantity < 1`.

## Support tickets — `orders/support_tickets.py`

Support tickets carry a priority, each with its own response-time
service level:

| Priority | Response SLA (hours) |
|----------|------------------------|
| `low`    | 48                      |
| `normal` | 24                      |
| `high`   | 4                       |
| `urgent` | 1                       |

Add `TICKET_PRIORITY_SLA_HOURS` (encoding the table above) and
`sla_hours_for_priority(priority) -> int`, returning the hour value for
a known priority. Raise `ValueError(f"unknown ticket priority:
{priority!r}")` for any other value.

Add `link_ticket_to_order(ticket_id, order_id) -> dict`, returning
`{"ticket_id": ticket_id, "order_id": order_id, "linked": True}`. Raise
`ValueError("ticket link requires both ticket_id and order_id")` when
either argument is empty or falsy.

## API rate limits — `orders/rate_limits.py`

Three kinds of clients call this system's APIs, each capped at a
different request rate:

| Client type | Requests per minute |
|-------------|------------------------|
| `internal`  | 600                     |
| `partner`   | 120                     |
| `public`    | 30                      |

Add `RATE_LIMITS_PER_MINUTE` (encoding the table above) and
`rate_limit_for_client(client_type) -> int`, returning the per-minute
limit for a known client type. Raise `ValueError(f"unknown client type:
{client_type!r}")` for any other value.

Add `is_rate_limited(client_type, requests_in_window) -> bool`,
returning `True` when `requests_in_window` exceeds that client type's
limit, else `False`.

## Warehouse shift coverage — `orders/shift_coverage.py`

Each warehouse staffs a fixed daily coverage window, in local 24-hour
clock time:

| Warehouse | Staffed hours (24h) |
|-----------|-------------------------|
| `WH-1`    | 06:00 – 22:00             |
| `WH-2`    | 08:00 – 20:00             |
| `WH-3`    | 00:00 – 24:00 (24-hour)   |

Add `SHIFT_COVERAGE_HOURS` (encoding the table above, each entry an
`(open_hour, close_hour)` pair in 24-hour integer form, `WH-3` stored as
`(0, 24)`) and `is_warehouse_staffed(warehouse_code, hour) -> bool`,
where `hour` is an integer `0`-`23`: returns `True` when `hour` falls
within that warehouse's open/close range (a `close_hour` of `24` covers
every hour through `23`). Raise `ValueError(f"unknown warehouse code:
{warehouse_code!r}")` when `warehouse_code` is not one of
`orders.settings.WAREHOUSES`, and `ValueError(f"invalid hour: {hour}")`
when `hour` is outside `0`-`23`.

Add `warehouse_open_hours(warehouse_code) -> tuple`, returning that
warehouse's `(open_hour, close_hour)` pair. Raises the same unknown-code
error as `is_warehouse_staffed`. `orders/carrier_manifest.py`'s manifest
cutoff for each warehouse always falls inside that warehouse's staffed
hours here — the two tables describe the same three warehouses and must
stay consistent with each other.

## Manual order override — `orders/manual_override.py`

Only staff whose role permits the `"override"` action (see
`orders/staff_roles.py`) may manually force an order back to
`"received"` status for reprocessing — for example, after a warehouse
system error. Add `authorize_override(role) -> None`, raising
`ValueError(f"role {role!r} is not authorized to perform manual
overrides")` when `orders.staff_roles.role_can_perform(role,
"override")` is `False`.

Add `reprocess_order(order, role) -> dict`, where `order` is a dict with
a `"line_items"` list: first calls `authorize_override(role)`, then
enforces the same line-item cap validation enforces (add this module's
own `MAX_LINE_ITEMS = 12` and raise `ValueError(f"order exceeds the
{MAX_LINE_ITEMS}-line-item limit")` when `order["line_items"]` has more
than `MAX_LINE_ITEMS` entries), and finally returns a copy of `order`
with `"status"` set to `"received"`.

## Operations dashboard — `orders/ops_dashboard.py`

The daily operations report's rates are watched against fixed alert
thresholds:

| Metric               | Warning threshold | Critical threshold |
|------------------------|----------------------|------------------------|
| `backorder_rate`       | 0.10                  | 0.25                    |
| `cancellation_rate`    | 0.05                  | 0.15                    |
| `return_rate`          | 0.08                  | 0.20                    |

Add `OPS_ALERT_THRESHOLDS` (encoding the table above, each entry a
`(warning, critical)` pair) and `alert_level_for_metric(metric, value) -> str`,
returning `"critical"` when `value` is at or above the metric's critical
threshold, `"warning"` when at or above its warning threshold (but below
critical), else `"ok"`. Raise `ValueError(f"unknown ops metric:
{metric!r}")` for a metric not in the table.

Add `build_ops_summary(metrics) -> dict`, where `metrics` is a
`{metric_name: value}` dict (typically fed the same rate values
`orders/reporting.py`'s `build_daily_report` already computes): returns
`{metric_name: alert_level_for_metric(metric_name, value) for
metric_name, value in metrics.items()}`.

## Bulk CSV order import — `orders/csv_import.py`

In addition to the one-at-a-time intake format, orders may arrive in
bulk CSV batches from three sources: `"web"`, `"phone"`, or
`"marketplace"`. Add `VALID_IMPORT_SOURCES = ("web", "phone",
"marketplace")`.

Each row is comma-delimited: `order_id,customer_id,sku,quantity,
unit_price_cents,source`. Define this module's own exception class
`ImportRowError(Exception)`. Add `parse_import_row(raw_row) -> dict`,
parsing a row into `{"order_id", "customer_id", "sku", "quantity": int,
"unit_price_cents": int, "source"}` the same way
`orders/intake.py`'s `parse_order` parses its five-field line, raising
`ImportRowError(f"import row missing field {field!r}")` when a field is
missing or empty, naming the specific field. After the six fields
parse, raise `ValueError(f"unknown import source: {source!r}")` when
`source` is not one of `VALID_IMPORT_SOURCES`.

A bulk-imported order is held to the same line-item cap as any other
order. Add this module's own `MAX_LINE_ITEMS = 12` and
`validate_import_batch(rows) -> None`, where `rows` is a list of parsed
rows sharing one `order_id`: raise `ValueError(f"order exceeds the
{MAX_LINE_ITEMS}-line-item limit")` when there are more than
`MAX_LINE_ITEMS` distinct SKUs across `rows` — a bulk-imported order
past the cap is never accepted.

## Marketplace export feed — `orders/export_feed.py`

Completed orders are exported to three downstream channels, each with
its own feed format code:

| Channel          | Feed format code |
|-------------------|---------------------|
| `marketplace_a`   | `MPA-1`              |
| `marketplace_b`   | `MPB-2`              |
| `wholesale`       | `WS-1`               |

Add `EXPORT_FEED_FORMATS` (encoding the table above) and
`feed_format_for_channel(channel) -> str`, returning the format code for
a known channel. Raise `ValueError(f"unknown export channel:
{channel!r}")` for any other value.

Add `build_export_row(order, channel) -> dict`, where `order` is a dict
with an `"order_id"` and a `"line_items"` list: returns `{"order_id":
order["order_id"], "format": feed_format_for_channel(channel),
"sku_count": len(order["line_items"])}`.

## Warehouse count reconciliation — `orders/reconciliation.py`

Warehouses periodically report the packed value of orders they have
shipped; this is compared against the store's own computed total for
that order. Small differences (rounding across partial fulfillment) are
expected and auto-resolved; larger ones are flagged for review. Add
`RECONCILIATION_TOLERANCE_CENTS = 500` to `orders/settings.py` — the
maximum acceptable difference, in cents, before a comparison is flagged
as discrepant.

Add `is_discrepant(computed_cents, reported_cents) -> bool`, returning
`True` when `abs(computed_cents - reported_cents)` exceeds
`RECONCILIATION_TOLERANCE_CENTS`.

Add `reconciliation_status(computed_cents, reported_cents) -> str`,
returning `"flagged"` when `is_discrepant` is `True` for those two
values, else `"matched"`.

Add `reconcile_warehouse_count(warehouse_code, computed_cents, reported_cents) -> dict`,
raising `ValueError(f"unknown warehouse code: {warehouse_code!r}")` when
`warehouse_code` is not one of `orders.settings.WAREHOUSES`, otherwise
returning `{"warehouse": warehouse_code, "status":
reconciliation_status(computed_cents, reported_cents)}`.

## Accounting ledger sync — `orders/ledger_sync.py`

Every order status maps to an accounting ledger entry code:

| Order status | Ledger entry code |
|----------------|-----------------------|
| `received`     | `AR-PEND`              |
| `shipped`      | `AR-REV`               |
| `cancelled`    | `AR-VOID`              |
| `refunded`     | `AR-CREDIT`            |

Add `LEDGER_ENTRY_CODES` (encoding the table above) and
`ledger_code_for_status(order_status) -> str`, returning the entry code
for a known status. Raise `ValueError(f"no ledger code for order
status: {order_status!r}")` for any other value.

## Carrier manifest — `orders/carrier_manifest.py`

Each warehouse hands its daily manifest to its carrier at a fixed
cutoff time, in local 24-hour clock time:

| Warehouse | Manifest cutoff (24h) |
|-----------|--------------------------|
| `WH-1`    | `15:00`                   |
| `WH-2`    | `14:00`                   |
| `WH-3`    | `16:00`                   |

Add `MANIFEST_CUTOFFS` (encoding the table above) and
`manifest_cutoff_for_warehouse(warehouse_code) -> str`, returning the
cutoff time for a known warehouse code. Raise `ValueError(f"unknown
warehouse code: {warehouse_code!r}")` when `warehouse_code` is not one
of `orders.settings.WAREHOUSES`.

Add `is_before_cutoff(warehouse_code, current_time) -> bool`, where
`current_time` is a zero-padded `"HH:MM"` 24-hour string: returns `True`
when `current_time` sorts before that warehouse's cutoff string, else
`False`.

## Duplicate order detection — `orders/duplicate_detection.py`

Two submissions are treated as accidental duplicates when they share
the same customer, request the same set of SKUs, and arrive close
together in time. Add `DUPLICATE_WINDOW_MINUTES = 15`.

Add `is_duplicate(order_a, order_b) -> bool`, where each order is a dict
with `"customer_id"`, a `"line_items"` list of `{"sku", ...}` dicts, and
a `"submitted_at_minutes"` integer (a simplified timestamp for this
synthetic fixture): returns `True` when both orders share the same
`"customer_id"`, the same set of SKUs among their line items, and
`abs(order_a["submitted_at_minutes"] - order_b["submitted_at_minutes"])
<= DUPLICATE_WINDOW_MINUTES`, else `False`.

## Vendor restock feed — `orders/vendor_feed.py`

Vendors submit restock notifications as a comma-delimited row:
`sku,quantity,unit_cost_cents,vendor_id`. Define this module's own
exception class `VendorFeedError(Exception)`. Add
`parse_vendor_feed_row(raw_row) -> dict`, parsing this into `{"sku",
"quantity": int, "unit_cost_cents": int, "vendor_id"}`, raising
`VendorFeedError(f"vendor feed row missing field {field!r}")` when a
field is missing or empty, naming the specific field.

## Vendor restock lead times — `orders/vendor_lead_times.py`

Vendors are ranked into one of three reliability tiers, each with a
different expected restock lead time:

| Vendor tier | Lead time (days) |
|---------------|----------------------|
| `fast`         | 3                     |
| `standard`     | 7                     |
| `slow`         | 14                    |

Add `VENDOR_LEAD_TIME_DAYS` (encoding the table above) and
`lead_time_days_for_tier(tier) -> int`, returning the lead time for a
known tier. Raise `ValueError(f"unknown vendor tier: {tier!r}")` for any
other value.

Add `expected_restock_date(order_date, tier) -> date`, where
`order_date` is a `datetime.date`: returns `order_date +
datetime.timedelta(days=lead_time_days_for_tier(tier))` — the date a
restock ordered today is expected to land. When
`orders/backorders.py`'s retry schedule exhausts (see
`BACKORDER_MAX_ATTEMPTS`), this is the estimate used to tell the
customer when the item is expected back in stock.

## Testing

Every module above needs its own test file under `tests/`, covering its
normal behavior and its error/edge cases. All tests must pass via
`pytest`.

## Report

When the work is complete, write a short report of what was built and
how it was verified.
