# Order Fulfillment & Returns Service — Requirements

Synthetic fixture; no real warehouse, no real payment processor, no real
carrier, no real notification channel. Python 3.11+, standard library
only at runtime, tests run via `pytest`.

## Overview

Build a multi-warehouse order fulfillment and returns service for an
online store operating three regional warehouses: order intake,
validation, discount pricing, warehouse allocation, shipping cost
estimation, warehouse fulfillment, backorder handling, customer
notifications, loyalty points, returns intake, refund processing, a
daily operations report, archiving, order cancellation, and delivery
SLA estimation.

## Pre-existing code

`orders/settings.py` already exists and holds shared configuration:
`WAREHOUSE_CODE` (the store's original single-warehouse default),
`WAREHOUSES` (the list of all three warehouse codes now in service),
and `normalize_sku`. Do not remove or rename anything already in it —
only add to it where a section below asks for a new setting.

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
validation, pricing, warehouse allocation, and warehouse fulfillment
all refuse to process an order past this cap, and all four must agree
on exactly what the cap is.

Add a module constant `MAX_LINE_ITEMS = 12` and
`validate_line_items(line_items) -> None`, where `line_items` is a
list: raises `ValueError(f"order exceeds the {MAX_LINE_ITEMS}-line-item
limit")` when `len(line_items) > MAX_LINE_ITEMS`.

Add `validate_quantity(quantity) -> None`: raises
`ValueError(f"invalid quantity: {quantity}")` when `quantity < 1`.

Every SKU carries a category, encoded as a three-letter prefix before
a dash: `GEN` (general merchandise), `FRZ` (frozen / cold-chain), or
`HAZ` (hazardous materials) — e.g. `"GEN-1234"`. Add
`validate_sku_category(sku) -> str` returning the category name
(`"general"`, `"frozen"`, or `"hazardous"`) for a recognized prefix,
and raising `ValueError(f"unrecognized SKU category prefix:
{prefix!r}")` for any other prefix. Warehouse allocation (below) uses
the category to decide which warehouses can fulfill a given SKU.

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
`orders/discounts.py` for that subtotal, and returns the final total
in cents rounded down to the nearest cent (integer floor division).

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
(the only warehouse that handles all three categories, so it is always
a safe fallback). Raise `ValueError(f"unknown shipping zone:
{zone!r}")` for a zone not in the table above.

Before allocating, this module also enforces the same line-item cap:
add its own `MAX_LINE_ITEMS = 12` and raise `ValueError(f"order exceeds
the {MAX_LINE_ITEMS}-line-item limit")` when the order has more line
items than that — an order past the cap is never allocated to a
warehouse.

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
{weight_grams}g exceeds the maximum supported weight of 25000g")` for
an over-limit shipment, and `ValueError(f"unknown shipping zone:
{zone!r}")` for a zone not in the table above.

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

Not every SKU on a pick list is in stock at the assigned warehouse.
Add `flag_backorder_items(pick_list, available_stock) -> list`, where
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
`schedule_backorder_retry(attempt_number) -> int`, returning the
number of days to wait before the next recheck for attempts 1 through
3 (`1`, `3`, or `7`). Raise `ValueError(f"backorder exhausted after
{BACKORDER_MAX_ATTEMPTS} attempts")` when `attempt_number >=
BACKORDER_MAX_ATTEMPTS`.

## Customer notifications — `orders/notifications.py`

`notify_customer(order_status) -> str` maps an order's status to the
message shown to the customer: `"received"` -> `"order received"`,
`"picking"` -> `"order is being picked"`, `"shipped"` -> `"order has
shipped"`, `"cancelled"` -> `"order was cancelled"`. Any other status
raises `ValueError(f"unknown order status: {order_status!r}")`.

Notification sends can fail transiently and should be retried. Add
`NOTIFY_MAX_RETRIES = 3` to `orders/settings.py` — the default number
of times a failed notification send is retried before giving up, for
any channel not given its own tuned value below.

Two of this store's three notification channels need a different
retry count than the default: email gets more attempts because it's
the cheapest channel to retry, SMS gets the most because delivery
receipts are unreliable, and push notifications get fewer because a
stale push is worse than a missed one. Add
`CHANNEL_RETRY_OVERRIDES = {"email": 3, "sms": 5, "push": 2}` and
`retries_for_channel(channel) -> int`, returning the channel's entry
from that table when present, otherwise falling back to
`orders/settings.py`'s `NOTIFY_MAX_RETRIES`.

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

Add `is_within_return_window(shipped_date, request_date) -> bool`
(both `datetime.date` objects), returning `True` when `(request_date -
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
returning `order_total_cents` minus that tier's fee percentage
(integer floor). A `days_since_delivery` of more than 30 — past this
store's `RETURN_WINDOW_DAYS` — is not refundable at all: raise
`ValueError(f"return window of {RETURN_WINDOW_DAYS} days has
elapsed")`.

An order can only be refunded once. Add `process_refund(order) -> dict`,
where `order` is a dict with a `"refund_status"` key (`"none"` or
`"refunded"`): raises `ValueError("order has already been refunded")`
when `order["refund_status"] == "refunded"`, otherwise returns a copy
of `order` with `"refund_status"` set to `"refunded"`.

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
`orders.settings.WAREHOUSES` — an order missing that field, or naming
a warehouse not in that list, is still counted in `total` and
`by_status` but excluded from `by_warehouse`. `returns_rate` is the
fraction (a float between 0.0 and 1.0) of orders in the list whose
status is `"cancelled"`, out of `total` — `0.0` when the list is empty.

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
order is not eligible for permanent deletion until its grace window
has elapsed.

## Order cancellation — `orders/cancellation.py`

A customer can cancel an order only before it ships. Add
`cancel_order(order_status) -> str`, returning `"cancelled"` when
`order_status` is `"received"` or `"picking"`. Raise
`ValueError(f"cannot cancel an order with status {order_status!r}")`
for any other status (in particular, `"shipped"` and already-
`"cancelled"` orders cannot be cancelled again).

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

## Testing

Every module above needs its own test file under `tests/`, covering
its normal behavior and its error/edge cases. All tests must pass via
`pytest`.

## Report

When the work is complete, write a short report of what was built and
how it was verified.
