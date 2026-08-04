from orders.reporting import build_daily_report


def test_build_report_counts_correctly():
    orders = [
        {"order_id": "O1", "status": "shipped", "warehouse": "WH-1"},
        {"order_id": "O2", "status": "cancelled", "warehouse": "WH-2"},
        {"order_id": "O3", "status": "weird", "warehouse": "WH-1"},
        {"order_id": "O4", "status": "shipped"},
    ]
    report = build_daily_report(orders)
    assert report["total"] == 4
    assert report["by_status"]["shipped"] == 2
    assert report["by_status"]["cancelled"] == 1
    assert report["by_warehouse"] == {"WH-1": 2, "WH-2": 1, "WH-3": 0}
    assert report["returns_rate"] == 0.25


def test_empty_report():
    report = build_daily_report([])
    assert report["total"] == 0
    assert report["returns_rate"] == 0.0
