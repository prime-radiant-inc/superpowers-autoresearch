# Task 25: Bulk CSV order import

**Files:**
- Create: `orders/csv_import.py`
- Test: `tests/test_csv_import.py`

`VALID_IMPORT_SOURCES`, `ImportRowError`, `parse_import_row`
(six-field comma row, mirrors Task 1's intake parser). Re-enforces the
shared line-item cap — its own `MAX_LINE_ITEMS = 12` — via
`validate_import_batch`.

**Verification:** `pytest tests/test_csv_import.py`
