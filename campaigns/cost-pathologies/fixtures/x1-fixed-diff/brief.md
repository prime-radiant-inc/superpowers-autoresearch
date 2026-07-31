# Task Brief: Order discount + append-only ledger service

Synthetic fixture for the X1 MICRO (reviewer-arm calibration). Nothing
here describes a real system; all names, amounts, and requirements are
invented for this eval.

**Files:**

- Create: `src/discount.py`
- Create: `src/ledger.py`
- Create: `src/service.py`
- Create: `tests/test_service.py`

**Interfaces:**

- Consumes: an order dict `{order_id, customer_id, subtotal, code,
  timestamp}`.
- Produces: `apply_discount(subtotal, code) -> Decimal` in `discount.py`;
  `Ledger` (with `has_order`, `record_transaction`) in `ledger.py`;
  `process_order(order, ledger) -> dict` and `process_batch(orders,
  ledger) -> list[dict]` in `service.py`.

**Requirements:**

- REQ-1 (discount codes): a fixed catalog maps a promo code to a percent
  off, 0-100 inclusive. An order presenting a code that is not in the
  catalog MUST be rejected with a caught, reported error — never allowed
  to propagate as an unhandled exception out of `process_order` or
  `process_batch`.
- REQ-2 (money type): all monetary amounts (subtotal, discount, charged
  total) are represented as `decimal.Decimal`, never `float` — see
  Global Constraints below.
- REQ-3 (idempotency): processing the same `order_id` a second time
  (e.g. after a client retry following a timeout) MUST NOT create a
  second ledger entry or charge the customer again — the service must
  detect the duplicate and return the original receipt unchanged.
- REQ-4 (durability): the ledger is an append-only log. Once a
  transaction is recorded, it MUST survive any subsequent failure — a
  crash, a full disk, or an interrupted write must never discard
  transactions that were already recorded.
- REQ-5 (minimum charge): after any discount is applied, an order whose
  final charged amount is below $1.00 MUST be rejected outright (no
  ledger entry, no charge). This floor applies to the POST-DISCOUNT
  charged amount, not the pre-discount subtotal.

**Global Constraints:** Python 3.10+, standard library only at runtime,
no third-party dependencies. Money is always `decimal.Decimal`, never
`float`. Prefer pure functions where reasonable; the ledger is the one
component that legitimately owns I/O (its JSON file).

**Report:** write your report to `task-report.md` when done.
