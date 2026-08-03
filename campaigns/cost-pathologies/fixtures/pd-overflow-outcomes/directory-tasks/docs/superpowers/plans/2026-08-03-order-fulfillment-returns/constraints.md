# Order Fulfillment & Returns Service — Global Constraints

Python 3.11+, standard library only at runtime. `orders/settings.py` is
pre-existing; extend it, do not replace it. `MAX_LINE_ITEMS = 12` is
enforced identically in `validation.py`, `pricing.py`, `allocation.py`,
and `fulfillment.py`.
