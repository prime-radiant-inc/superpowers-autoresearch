# Task 1: Walking skeleton — intake through pricing, thinnest path

**Files:**
- Create: `orders/intake.py`
- Create: `orders/validation.py`
- Create: `orders/pricing.py`

Stand up the thinnest possible end-to-end slice: parse one order line
(`orders/intake.py`), accept it (`orders/validation.py`), and price it
(`orders/pricing.py`) — happy path only, widened by later tasks.

**Verification:** `pytest tests/test_intake.py tests/test_validation.py tests/test_pricing.py -k "not widen"`
