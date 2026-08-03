# Deliberately diverges from validation.py / pricing.py's MAX_LINE_ITEMS
# (12) -- this tree is the incoherent-constant construction for the
# pd-pipeline MICRO validation (see probe-design-notes.md).
MAX_LINE_ITEMS = 10


def build_pick_list(order):
    line_items = order["line_items"]
    if len(line_items) > MAX_LINE_ITEMS:
        raise ValueError(f"order exceeds the {MAX_LINE_ITEMS}-line-item limit")
    return [{"sku": item["sku"], "quantity": item["quantity"]} for item in line_items]
