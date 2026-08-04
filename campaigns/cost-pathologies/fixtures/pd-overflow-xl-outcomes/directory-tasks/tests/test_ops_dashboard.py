import pytest

from orders.ops_dashboard import alert_level_for_metric, build_ops_summary


def test_alert_levels():
    assert alert_level_for_metric("cancellation_rate", 0.01) == "ok"
    assert alert_level_for_metric("cancellation_rate", 0.05) == "warning"
    assert alert_level_for_metric("cancellation_rate", 0.15) == "critical"


def test_unknown_metric_raises():
    with pytest.raises(ValueError, match="unknown ops metric: 'bogus'"):
        alert_level_for_metric("bogus", 0.5)


def test_build_ops_summary():
    summary = build_ops_summary({"backorder_rate": 0.30, "return_rate": 0.01})
    assert summary == {"backorder_rate": "critical", "return_rate": "ok"}
