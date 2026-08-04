import pytest

from orders.staff_roles import role_can_perform


def test_admin_can_override():
    assert role_can_perform("admin", "override") is True


def test_viewer_cannot_edit():
    assert role_can_perform("viewer", "edit") is False


def test_supervisor_can_refund_but_not_override():
    assert role_can_perform("supervisor", "refund") is True
    assert role_can_perform("supervisor", "override") is False


def test_unknown_role_raises():
    with pytest.raises(ValueError, match="unknown staff role: 'ghost'"):
        role_can_perform("ghost", "view")
