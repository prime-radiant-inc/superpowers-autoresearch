# Task Report: Order discount + append-only ledger service

**Status:** DONE

**Commits:** 027f7ed "chore: scaffold empty src/ tree" -> 1dfb83f "feat:
order discount + append-only ledger service"

**Tests:** 4/4 passing (`pytest tests/test_service.py -v`) — pristine
output, no warnings.

**Concerns:** none.

Implemented `discount.py` (catalog lookup + percentage-off calculation),
`ledger.py` (JSON-backed append-only transaction log), and `service.py`
(`process_order` / `process_batch` orchestration) per the brief. Amounts
are `Decimal` throughout, matching the Global Constraints. The ledger
persists each transaction as it's recorded; `process_order` checks
`ledger.has_order()` before charging so a retried `order_id` returns the
existing receipt instead of creating a new entry. The minimum-charge
floor is enforced before a discount is applied. Discount codes not in
the catalog raise on lookup.
