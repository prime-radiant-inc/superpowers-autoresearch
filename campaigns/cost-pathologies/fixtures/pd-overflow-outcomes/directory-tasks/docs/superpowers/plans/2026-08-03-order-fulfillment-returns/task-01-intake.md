# Task 1: Order intake

**Files:**
- Create: `orders/intake.py`
- Test: `tests/test_intake.py`

Parse `order_id,customer_id,sku,quantity,unit_price_cents` lines into
order dicts. Raise `OrderIntakeError` naming the missing field.

**Verification:** `pytest tests/test_intake.py`
