import pytest

from orders.export_feed import build_export_row, feed_format_for_channel


def test_feed_format_for_known_channels():
    assert feed_format_for_channel("marketplace_a") == "MPA-1"
    assert feed_format_for_channel("marketplace_b") == "MPB-2"
    assert feed_format_for_channel("wholesale") == "WS-1"


def test_unknown_channel_raises():
    with pytest.raises(ValueError, match="unknown export channel: 'ebay'"):
        feed_format_for_channel("ebay")


def test_build_export_row():
    order = {"order_id": "O-1", "line_items": [{"sku": "GEN-1"}, {"sku": "GEN-2"}]}
    assert build_export_row(order, "wholesale") == {
        "order_id": "O-1",
        "format": "WS-1",
        "sku_count": 2,
    }
