import pytest

from orders.manual_override import authorize_override, reprocess_order


def test_authorize_override_allows_admin():
    assert authorize_override("admin") is None


def test_authorize_override_rejects_agent():
    with pytest.raises(ValueError, match="role 'agent' is not authorized to perform manual overrides"):
        authorize_override("agent")


def test_reprocess_order_resets_status_to_received():
    order = {"line_items": [{"sku": "GEN-1"}] * 3}
    result = reprocess_order(order, "admin")
    assert result["status"] == "received"
    assert result is not order


def test_reprocess_order_rejects_unauthorized_role():
    order = {"line_items": [{"sku": "GEN-1"}]}
    with pytest.raises(ValueError, match="role 'viewer' is not authorized to perform manual overrides"):
        reprocess_order(order, "viewer")


def test_reprocess_order_rejects_over_cap_order():
    order = {"line_items": [{"sku": f"GEN-{i}"} for i in range(13)]}
    with pytest.raises(ValueError, match="order exceeds the 12-line-item limit"):
        reprocess_order(order, "admin")
