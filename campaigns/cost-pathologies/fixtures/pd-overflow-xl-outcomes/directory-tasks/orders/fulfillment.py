MAX_LINE_ITEMS = 12


def build_pick_list(order):
    line_items = order["line_items"]
    if len(line_items) > MAX_LINE_ITEMS:
        raise ValueError(f"order exceeds the {MAX_LINE_ITEMS}-line-item limit")
    return [{"sku": item["sku"], "quantity": item["quantity"]} for item in line_items]


def flag_backorder_items(pick_list, available_stock):
    return [
        item
        for item in pick_list
        if available_stock.get(item["sku"], 0) < item["quantity"]
    ]
