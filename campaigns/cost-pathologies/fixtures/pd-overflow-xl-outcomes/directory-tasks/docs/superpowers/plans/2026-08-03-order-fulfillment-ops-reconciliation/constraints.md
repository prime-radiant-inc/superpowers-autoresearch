# Order Fulfillment, Operations & Reconciliation Service — Global Constraints

Python 3.11+, standard library only at runtime. `orders/settings.py` is
pre-existing; extend it, do not replace it. `MAX_LINE_ITEMS = 12` is
enforced identically in `validation.py`, `pricing.py`, `allocation.py`,
`fulfillment.py`, `manual_override.py`, and `csv_import.py` — one
consuming module in each of the three subsystems.
