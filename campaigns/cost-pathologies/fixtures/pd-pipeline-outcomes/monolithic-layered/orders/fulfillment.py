MAX_LINE_ITEMS = 12


def build_pick_list(order):
    line_items = order["line_items"]
    if len(line_items) > MAX_LINE_ITEMS:
        raise ValueError(f"order exceeds the {MAX_LINE_ITEMS}-line-item limit")
    return [{"sku": item["sku"], "quantity": item["quantity"]} for item in line_items]
