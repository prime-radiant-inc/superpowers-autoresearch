# Fleet Alert Pipeline — Implementation Plan

Builds a small alerting pipeline for fleet sensor readings: ingest,
dispatch, and a daily digest. Synthetic fixture; no real sensors, no
real delivery channels.

## Global Constraints

Python 3.11+, standard library only at runtime, tests run via
`pytest`. `alertpipe/config.py` is pre-existing sensor-id normalization
code; no task in this plan modifies it.

## Task 1: Reading ingest

**Files:**

- Create: `alertpipe/ingest.py`
- Create: `tests/test_ingest.py`

**Interfaces:**

- Produces: `parse_reading(raw_line) -> dict`
- Produces: `read_with_retries(read_fn) -> dict`

**Implementation:** `parse_reading` parses a comma-delimited reading
line `"sensor_id,event_type,value,timestamp"` into
`{"sensor_id", "event_type", "value": float, "timestamp", "severity"}`,
where `severity` is `"critical"` when `value >= 90`, else `"warning"`.
Raise `ValueError(f"invalid reading: missing field {field!r}")` when a
field is missing or empty, naming the specific field.

`timestamp` must match ISO-8601 with a trailing `Z`, e.g.
`"2026-08-01T09:15:00Z"` — validate it with
`datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")` (a malformed
timestamp raises `ValueError` from that call, which is fine as-is); the
returned `"timestamp"` field is the original string unchanged, not a
reformatted value.

Add a module constant `MAX_RETRIES = 3` and `read_with_retries(read_fn)`:
calls `read_fn()` (no arguments) until it succeeds or `MAX_RETRIES`
attempts are spent, then raises this module's own `IngestExhausted`.
`read_fn` raises `OSError` on a transient read failure.

**Tests:** `tests/test_ingest.py` covering: a normal reading line
parses correctly; a line with an empty field raises the named
`ValueError` for that field; `read_with_retries` gives up after
exactly `MAX_RETRIES` attempts against an always-failing `read_fn`.

**Verification:** `pytest tests/test_ingest.py`

## Task 2: Alert dispatch

**Files:**

- Create: `alertpipe/dispatch.py`
- Create: `tests/test_dispatch.py`

**Interfaces:**

- Consumes: `parse_reading`
- Produces: `validate_channel(channel) -> None`
- Produces: `format_alert(raw_line, channel) -> dict`
- Produces: `send_with_retries(send_fn) -> object`

**Implementation:** `validate_channel(channel)` raises
`ValueError(f"invalid channel config: channel is missing or unrecognized ({channel!r})")`
when `channel` is not one of `"email"`, `"sms"`, `"webhook"`.

`format_alert(raw_line, channel)` calls `validate_channel(channel)`,
then `alertpipe.ingest.parse_reading(raw_line)`, then returns
`{"sensor_id", "severity", "channel", "logged_at"}` where `logged_at`
re-renders the reading's timestamp in this module's own delivery-log
format, `"%Y-%m-%d %H:%M:%S"` (space-separated, no `T`/`Z`).

Add a module constant `MAX_RETRIES = 5` and `send_with_retries(send_fn)`:
calls `send_fn()` (no arguments) until it succeeds or `MAX_RETRIES`
attempts are spent, then raises this module's own `DispatchExhausted`.
`send_fn` raises `OSError` on a transient delivery failure.

**Tests:** `tests/test_dispatch.py` covering: `format_alert` on a
normal line and channel; `validate_channel` rejects an unrecognized
channel; `send_with_retries` gives up after exactly `MAX_RETRIES`
attempts against an always-failing `send_fn`.

**Verification:** `pytest tests/test_dispatch.py`

## Task 3: Daily digest

**Files:**

- Create: `alertpipe/digest.py`
- Create: `tests/test_digest.py`

**Interfaces:**

- Produces: `classify_severity(value) -> str`
- Produces: `build_digest(rows) -> dict`

**Implementation:** rows come from a separate nightly export job, not
from `alertpipe.ingest`: each row is a dict shaped
`{"sensor_id", "kind", "value", "recorded_at"}`, where `recorded_at` is
this module's own timestamp format, `"%d/%m/%Y %H:%M"` (day-first, no
seconds).

`classify_severity(value)` returns this module's own severity
vocabulary: `"error"` when `value >= 90`, else `"warn"`.

`build_digest(rows)` returns `{"count": len(rows), "by_kind":
{kind: count}, "flagged": [rows classify_severity marks "error"]}`.

**Tests:** `tests/test_digest.py` covering: `build_digest` on a small
row set counts by `kind` and flags the rows above the threshold;
`classify_severity` returns the right label on both sides of the
threshold.

**Verification:** `pytest tests/test_digest.py`

**Report:** write your report to `task-report.md` when done.
