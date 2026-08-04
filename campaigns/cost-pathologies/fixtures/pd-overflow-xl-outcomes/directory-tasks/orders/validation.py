import re

MAX_LINE_ITEMS = 12

SKU_CATEGORY_PREFIXES = {
    "GEN": "general",
    "FRZ": "frozen",
    "HAZ": "hazardous",
}

_CUSTOMER_ID_RE = re.compile(r"^[A-Za-z0-9]{6,12}$")


def validate_line_items(line_items):
    if len(line_items) > MAX_LINE_ITEMS:
        raise ValueError(f"order exceeds the {MAX_LINE_ITEMS}-line-item limit")


def validate_quantity(quantity):
    if quantity < 1:
        raise ValueError(f"invalid quantity: {quantity}")


def validate_sku_category(sku):
    prefix = sku.split("-", 1)[0]
    if prefix not in SKU_CATEGORY_PREFIXES:
        raise ValueError(f"unrecognized SKU category prefix: {prefix!r}")
    return SKU_CATEGORY_PREFIXES[prefix]


def validate_customer_id_format(customer_id):
    if not _CUSTOMER_ID_RE.match(customer_id):
        raise ValueError(f"invalid customer id format: {customer_id!r}")
