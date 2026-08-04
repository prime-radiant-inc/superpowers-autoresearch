EXPORT_FEED_FORMATS = {
    "marketplace_a": "MPA-1",
    "marketplace_b": "MPB-2",
    "wholesale": "WS-1",
}


def feed_format_for_channel(channel):
    if channel not in EXPORT_FEED_FORMATS:
        raise ValueError(f"unknown export channel: {channel!r}")
    return EXPORT_FEED_FORMATS[channel]


def build_export_row(order, channel):
    return {
        "order_id": order["order_id"],
        "format": feed_format_for_channel(channel),
        "sku_count": len(order["line_items"]),
    }
