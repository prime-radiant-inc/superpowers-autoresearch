import pytest

from orders.support_tickets import link_ticket_to_order, sla_hours_for_priority


def test_sla_hours_for_known_priorities():
    assert sla_hours_for_priority("low") == 48
    assert sla_hours_for_priority("normal") == 24
    assert sla_hours_for_priority("high") == 4
    assert sla_hours_for_priority("urgent") == 1


def test_unknown_priority_raises():
    with pytest.raises(ValueError, match="unknown ticket priority: 'critical'"):
        sla_hours_for_priority("critical")


def test_link_ticket_to_order():
    assert link_ticket_to_order("T-1", "O-1") == {
        "ticket_id": "T-1",
        "order_id": "O-1",
        "linked": True,
    }


def test_link_requires_both_ids():
    with pytest.raises(ValueError, match="ticket link requires both ticket_id and order_id"):
        link_ticket_to_order("", "O-1")
    with pytest.raises(ValueError, match="ticket link requires both ticket_id and order_id"):
        link_ticket_to_order("T-1", "")
