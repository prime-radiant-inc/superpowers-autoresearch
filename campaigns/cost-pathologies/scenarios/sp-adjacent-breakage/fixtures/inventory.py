INVENTORY = {
    "widgets": 12,
    "gadgets": 3,
    "gizmos": 40,
}


def get_quantity(item):
    return INVENTORY.get(item, 0)
