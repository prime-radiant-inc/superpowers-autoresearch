class VendorFeedError(Exception):
    pass


_FIELDS = ("sku", "quantity", "unit_cost_cents", "vendor_id")


def parse_vendor_feed_row(raw_row):
    parts = raw_row.split(",")
    if len(parts) != len(_FIELDS):
        raise VendorFeedError(f"vendor feed row missing field {_FIELDS[len(parts)]!r}")
    values = dict(zip(_FIELDS, parts))
    for field in _FIELDS:
        if not values[field]:
            raise VendorFeedError(f"vendor feed row missing field {field!r}")
    return {
        "sku": values["sku"],
        "quantity": int(values["quantity"]),
        "unit_cost_cents": int(values["unit_cost_cents"]),
        "vendor_id": values["vendor_id"],
    }
