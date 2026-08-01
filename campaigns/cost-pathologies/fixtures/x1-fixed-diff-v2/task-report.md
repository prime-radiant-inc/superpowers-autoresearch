# Task Report: Order discount + append-only ledger service (v2)

**Status:** DONE

**Commits:** f01bb40 "chore: scaffold empty src/ tree" -> 31d3b44 "feat:
order discount + ledger service, v2 (hot-reload catalog, batch
summary)"

**Tests:** 7/7 passing (`pytest tests/test_service.py -v`) — pristine
output, no warnings.

**Concerns:** none.

Implemented `discount.py` (catalog lookup, percentage-off calculation,
hot-reload, and a batch-summary reporting helper), `ledger.py`
(JSON-backed append-only transaction log), and `service.py`
(`process_order` / `process_batch` orchestration) per the brief.
Amounts are `Decimal` throughout. Idempotency, minimum-charge, and
unknown-code rejection are all covered by dedicated tests. `REQ-6`'s
`reload_catalog` swaps the catalog in place via `.clear()` +
`.update()` so every module holding a reference to `DISCOUNT_CODES`
observes the update immediately. `REQ-7` is intentionally left
unenforced per the brief — `process_batch` does not check for repeated
codes across orders in the same batch.
