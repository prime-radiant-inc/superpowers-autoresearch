OPS_ALERT_THRESHOLDS = {
    "backorder_rate": (0.10, 0.25),
    "cancellation_rate": (0.05, 0.15),
    "return_rate": (0.08, 0.20),
}


def alert_level_for_metric(metric, value):
    if metric not in OPS_ALERT_THRESHOLDS:
        raise ValueError(f"unknown ops metric: {metric!r}")
    warning, critical = OPS_ALERT_THRESHOLDS[metric]
    if value >= critical:
        return "critical"
    if value >= warning:
        return "warning"
    return "ok"


def build_ops_summary(metrics):
    return {name: alert_level_for_metric(name, value) for name, value in metrics.items()}
