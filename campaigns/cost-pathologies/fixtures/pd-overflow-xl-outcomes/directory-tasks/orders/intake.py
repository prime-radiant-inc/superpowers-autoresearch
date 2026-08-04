class OrderIntakeError(Exception):
    pass


_FIELDS = ("order_id", "customer_id", "sku", "quantity", "unit_price_cents")


def parse_order(raw_line):
    parts = raw_line.split(",")
    if len(parts) != len(_FIELDS):
        raise OrderIntakeError(f"order line missing field {_FIELDS[len(parts)]!r}")
    values = dict(zip(_FIELDS, parts))
    for field in _FIELDS:
        if not values[field]:
            raise OrderIntakeError(f"order line missing field {field!r}")
    return {
        "order_id": values["order_id"],
        "customer_id": values["customer_id"],
        "sku": values["sku"],
        "quantity": int(values["quantity"]),
        "unit_price_cents": int(values["unit_price_cents"]),
        "status": "received",
    }
