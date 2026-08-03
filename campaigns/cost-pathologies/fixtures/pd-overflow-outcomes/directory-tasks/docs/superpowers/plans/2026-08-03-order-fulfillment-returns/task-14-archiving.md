# Task 14: Archiving

**Files:**
- Create: `orders/archiving.py`
- Test: `tests/test_archiving.py`

`should_archive` (shipped/cancelled/refunded, 30+ days), `purge_eligible`
(uses the `ARCHIVE_GRACE_DAYS` setting added by Task 18).

**Verification:** `pytest tests/test_archiving.py`
