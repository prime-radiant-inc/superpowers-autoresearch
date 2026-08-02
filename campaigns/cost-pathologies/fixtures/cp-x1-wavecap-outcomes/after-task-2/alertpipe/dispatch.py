# Alert dispatch: turns a parsed reading into a channel-ready alert and
# delivers it, retrying transient delivery failures up to this module's
# own attempt budget. Synthetic fixture; no real channels, no real
# delivery.
import datetime as _dt

from alertpipe.ingest import parse_reading

MAX_RETRIES = 5

VALID_CHANNELS = ("email", "sms", "webhook")


class DispatchExhausted(Exception):
    """Raised when a channel keeps rejecting delivery past the retry budget."""


def validate_channel(channel):
    if channel not in VALID_CHANNELS:
        raise ValueError(
            f"invalid channel config: channel is missing or unrecognized ({channel!r})"
        )


def format_alert(raw_line, channel):
    """Parses raw_line via alertpipe.ingest.parse_reading, then formats it
    for delivery on channel. Returns {"sensor_id", "severity", "channel",
    "logged_at"} where logged_at re-renders the reading's timestamp in
    this module's own delivery-log format, "%Y-%m-%d %H:%M:%S"
    (space-separated, no "T"/"Z")."""
    validate_channel(channel)
    reading = parse_reading(raw_line)
    ts = _dt.datetime.strptime(reading["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
    return {
        "sensor_id": reading["sensor_id"],
        "severity": reading["severity"],
        "channel": channel,
        "logged_at": ts.strftime("%Y-%m-%d %H:%M:%S"),
    }


def send_with_retries(send_fn):
    """Calls send_fn() (no arguments) until it succeeds or MAX_RETRIES
    attempts are spent, then raises DispatchExhausted. send_fn raises
    OSError on a transient delivery failure."""
    last_error = None
    for _ in range(MAX_RETRIES):
        try:
            return send_fn()
        except OSError as exc:
            last_error = exc
    raise DispatchExhausted(f"gave up after {MAX_RETRIES} attempts") from last_error
