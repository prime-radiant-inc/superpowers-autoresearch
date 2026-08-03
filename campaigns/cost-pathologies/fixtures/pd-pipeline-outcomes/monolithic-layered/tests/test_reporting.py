import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orders.reporting import build_daily_report


def test_counts_total_and_by_status():
    orders = [
        {"order_id": "o1", "status": "received"},
        {"order_id": "o2", "status": "shipped"},
        {"order_id": "o3", "status": "shipped"},
    ]
    report = build_daily_report(orders)
    assert report["total"] == 3
    assert report["by_status"]["shipped"] == 2
    assert report["by_status"]["received"] == 1


def test_unrecognized_status_counted_in_total_only():
    orders = [{"order_id": "o1", "status": "weird"}]
    report = build_daily_report(orders)
    assert report["total"] == 1
    assert "weird" not in report["by_status"]
