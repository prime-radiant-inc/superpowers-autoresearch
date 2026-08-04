TICKET_PRIORITY_SLA_HOURS = {
    "low": 48,
    "normal": 24,
    "high": 4,
    "urgent": 1,
}


def sla_hours_for_priority(priority):
    if priority not in TICKET_PRIORITY_SLA_HOURS:
        raise ValueError(f"unknown ticket priority: {priority!r}")
    return TICKET_PRIORITY_SLA_HOURS[priority]


def link_ticket_to_order(ticket_id, order_id):
    if not ticket_id or not order_id:
        raise ValueError("ticket link requires both ticket_id and order_id")
    return {"ticket_id": ticket_id, "order_id": order_id, "linked": True}
