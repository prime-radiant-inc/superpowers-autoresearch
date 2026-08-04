class ImportRowError(Exception):
    pass


MAX_LINE_ITEMS = 12

VALID_IMPORT_SOURCES = ("web", "phone", "marketplace")

_FIELDS = ("order_id", "customer_id", "sku", "quantity", "unit_price_cents", "source")


def parse_import_row(raw_row):
    parts = raw_row.split(",")
    if len(parts) != len(_FIELDS):
        raise ImportRowError(f"import row missing field {_FIELDS[len(parts)]!r}")
    values = dict(zip(_FIELDS, parts))
    for field in _FIELDS:
        if not values[field]:
            raise ImportRowError(f"import row missing field {field!r}")
    if values["source"] not in VALID_IMPORT_SOURCES:
        raise ValueError(f"unknown import source: {values['source']!r}")
    return {
        "order_id": values["order_id"],
        "customer_id": values["customer_id"],
        "sku": values["sku"],
        "quantity": int(values["quantity"]),
        "unit_price_cents": int(values["unit_price_cents"]),
        "source": values["source"],
    }


def validate_import_batch(rows):
    skus = {row["sku"] for row in rows}
    if len(skus) > MAX_LINE_ITEMS:
        raise ValueError(f"order exceeds the {MAX_LINE_ITEMS}-line-item limit")
