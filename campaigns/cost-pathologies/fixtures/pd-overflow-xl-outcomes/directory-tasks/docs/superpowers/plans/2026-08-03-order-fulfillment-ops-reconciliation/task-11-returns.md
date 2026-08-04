# Task 11: Returns intake

**Files:**
- Create: `orders/returns.py`
- Modify: `orders/settings.py`
- Test: `tests/test_returns.py`

Add `RETURN_WINDOW_DAYS = 30` to `orders/settings.py`.
`is_within_return_window`, `validate_return_reason` (the four allowed
reason codes).

**Verification:** `pytest tests/test_returns.py`
