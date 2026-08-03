MAX_LINE_ITEMS = 12


def validate_line_items(line_items):
    if len(line_items) > MAX_LINE_ITEMS:
        raise ValueError(f"order exceeds the {MAX_LINE_ITEMS}-line-item limit")


def validate_quantity(quantity):
    if quantity < 1:
        raise ValueError(f"invalid quantity: {quantity}")
