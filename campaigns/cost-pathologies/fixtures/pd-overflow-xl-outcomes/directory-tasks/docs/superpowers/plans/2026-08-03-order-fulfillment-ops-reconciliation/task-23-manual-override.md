# Task 23: Manual order override

**Files:**
- Create: `orders/manual_override.py`
- Test: `tests/test_manual_override.py`

Depends on Task 17 (`orders/staff_roles.py`) for `role_can_perform`.
`authorize_override` (requires the `"override"` action). `reprocess_order`
resets status to `"received"`, re-enforcing the shared line-item cap —
its own `MAX_LINE_ITEMS = 12`.

**Verification:** `pytest tests/test_manual_override.py`
