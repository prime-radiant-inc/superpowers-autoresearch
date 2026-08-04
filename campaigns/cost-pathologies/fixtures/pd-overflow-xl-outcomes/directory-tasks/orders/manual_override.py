from orders.staff_roles import role_can_perform

MAX_LINE_ITEMS = 12


def authorize_override(role):
    if not role_can_perform(role, "override"):
        raise ValueError(f"role {role!r} is not authorized to perform manual overrides")


def reprocess_order(order, role):
    authorize_override(role)
    if len(order["line_items"]) > MAX_LINE_ITEMS:
        raise ValueError(f"order exceeds the {MAX_LINE_ITEMS}-line-item limit")
    return {**order, "status": "received"}
