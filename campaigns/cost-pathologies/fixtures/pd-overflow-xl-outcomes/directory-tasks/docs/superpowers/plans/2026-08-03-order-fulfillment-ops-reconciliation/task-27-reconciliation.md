# Task 27: Warehouse count reconciliation

**Files:**
- Create: `orders/reconciliation.py`
- Test: `tests/test_reconciliation.py`

`is_discrepant`, `reconciliation_status` (uses the reconciliation
tolerance setting added in Task 35), `reconcile_warehouse_count`
(against `orders.settings.WAREHOUSES`).

**Verification:** `pytest tests/test_reconciliation.py`
