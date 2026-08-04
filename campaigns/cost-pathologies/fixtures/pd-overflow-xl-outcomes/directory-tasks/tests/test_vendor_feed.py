import pytest

from orders.vendor_feed import VendorFeedError, parse_vendor_feed_row


def test_parse_vendor_feed_row():
    row = parse_vendor_feed_row("GEN-1,50,300,V-1")
    assert row == {
        "sku": "GEN-1",
        "quantity": 50,
        "unit_cost_cents": 300,
        "vendor_id": "V-1",
    }


def test_missing_field_raises():
    with pytest.raises(VendorFeedError, match=r"vendor feed row missing field 'vendor_id'"):
        parse_vendor_feed_row("GEN-1,50,300,")


def test_wrong_field_count_raises():
    with pytest.raises(VendorFeedError, match=r"vendor feed row missing field 'vendor_id'"):
        parse_vendor_feed_row("GEN-1,50,300")
