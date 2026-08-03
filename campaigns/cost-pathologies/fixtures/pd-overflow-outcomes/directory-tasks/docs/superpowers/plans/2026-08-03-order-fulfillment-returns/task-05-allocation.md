# Task 5: Warehouse allocation

**Files:**
- Create: `orders/allocation.py`
- Test: `tests/test_allocation.py`

`allocate_warehouse` (zone-preferred warehouse, falling back to `WH-1`
when the preferred warehouse lacks a needed SKU-category capability),
`MAX_LINE_ITEMS = 12`.

**Verification:** `pytest tests/test_allocation.py`
