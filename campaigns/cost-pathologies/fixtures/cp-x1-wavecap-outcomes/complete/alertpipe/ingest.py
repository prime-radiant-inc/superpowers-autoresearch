# Sensor-reading ingest: parses a raw comma-delimited reading line and
# retries a flaky read source up to this module's own attempt budget.
# Synthetic fixture; no real sensors, no real hardware.
import datetime as _dt

MAX_RETRIES = 3

REQUIRED_FIELDS = ("sensor_id", "event_type", "value", "timestamp")


class IngestExhausted(Exception):
    """Raised when a reading source keeps failing past the retry budget."""


def parse_reading(raw_line):
    """Parses one comma-delimited reading line into a dict.

    raw_line: "sensor_id,event_type,value,timestamp" where timestamp is
    ISO-8601 with a trailing Z, e.g. "2026-08-01T09:15:00Z".
    Returns {"sensor_id": str, "event_type": str, "value": float,
    "timestamp": str, "severity": "warning"|"critical"}.
    """
    parts = raw_line.strip().split(",")
    if len(parts) != len(REQUIRED_FIELDS):
        raise ValueError(f"invalid reading: missing field {REQUIRED_FIELDS[-1]!r}")
    values = dict(zip(REQUIRED_FIELDS, parts))
    for field in REQUIRED_FIELDS:
        if not values[field]:
            raise ValueError(f"invalid reading: missing field {field!r}")
    # Validate the ISO-8601 shape; the returned "timestamp" field is the
    # original string unchanged, not a reformatted value.
    _dt.datetime.strptime(values["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
    reading_value = float(values["value"])
    return {
        "sensor_id": values["sensor_id"],
        "event_type": values["event_type"],
        "value": reading_value,
        "timestamp": values["timestamp"],
        "severity": "critical" if reading_value >= 90 else "warning",
    }


def read_with_retries(read_fn):
    """Calls read_fn() (no arguments) until it succeeds or MAX_RETRIES
    attempts are spent, then raises IngestExhausted. read_fn raises
    OSError on a transient read failure."""
    last_error = None
    for _ in range(MAX_RETRIES):
        try:
            return read_fn()
        except OSError as exc:
            last_error = exc
    raise IngestExhausted(f"gave up after {MAX_RETRIES} attempts") from last_error
