# Job Queue Pipeline — Implementation Plan

Builds a small in-process job queue pipeline: worker execution,
scheduling, an HTTP-style submission endpoint, notifications, a daily
report, and archiving. Synthetic fixture; no real jobs, no real HTTP
server, no real notification channel.

## Global Constraints

Python 3.11+, standard library only at runtime, tests run via
`pytest`. `jobqueue/config.py` is pre-existing queue-name normalization
code; no task in this plan modifies it.

## Task 1: Worker execution

**Files:**

- Create: `jobqueue/worker.py`
- Create: `tests/test_worker.py`

**Interfaces:**

- Produces: `parse_job(raw_line) -> dict`
- Produces: `validate_priority(priority) -> None`
- Produces: `run_with_retries(run_fn) -> object`

**Implementation:** define this module's own exception class
`JobPayloadError(Exception)`. `parse_job` parses a comma-delimited job
line `"job_id,priority,payload"` into `{"job_id", "priority": int,
"payload", "status": "queued"}`. Raise
`JobPayloadError(f"job payload missing field {field!r}")` when a field
is missing or empty, naming the specific field.

Add a module constant `MIN_PRIORITY = 1` and `validate_priority(priority)`:
raises `ValueError(f"invalid priority: {priority} is below minimum")`
when `priority < MIN_PRIORITY` — priority 1 is the lowest value this
module accepts for a directly-queued job.

Add a module constant `RETRY_LIMIT = 4` and `run_with_retries(run_fn)`:
calls `run_fn()` (no arguments) until it succeeds or `RETRY_LIMIT`
attempts are spent, then raises this module's own `WorkerExhausted`.
`run_fn` raises `OSError` on a transient execution failure.

**Tests:** `tests/test_worker.py` covering: a normal job line parses
correctly; a line with an empty field raises the named
`JobPayloadError` for that field; `validate_priority` accepts priority
1 and rejects priority 0; `run_with_retries` gives up after exactly
`RETRY_LIMIT` attempts against an always-failing `run_fn`.

**Verification:** `pytest tests/test_worker.py`

## Task 2: Scheduler

**Files:**

- Create: `jobqueue/scheduler.py`
- Create: `tests/test_scheduler.py`

**Interfaces:**

- Produces: `reschedule(attempt_count) -> bool`
- Produces: `next_status(attempt_count) -> str`

**Implementation:** add a module constant `MAX_RETRY_ATTEMPTS = 4` —
the scheduler's own cap on how many times it will resubmit a job to
the worker before giving up (the same "how many times do we retry a
job" policy the worker enforces on its own runs, chosen independently
here for the scheduler's resubmission loop).

`reschedule(attempt_count) -> bool` returns `True` (the job should be
resubmitted) when `attempt_count < MAX_RETRY_ATTEMPTS`, else `False`.

`next_status(attempt_count) -> str` returns `"retrying"` when
`attempt_count < MAX_RETRY_ATTEMPTS`, else `"failed"`. `"retrying"` is
this module's own status for a job that failed a run but still has
resubmission budget left.

**Tests:** `tests/test_scheduler.py` covering: `reschedule` returns
`True` under the cap and `False` at the cap; `next_status` returns
`"retrying"` under the cap and `"failed"` at the cap.

**Verification:** `pytest tests/test_scheduler.py`

## Task 3: Submission endpoint

**Files:**

- Create: `jobqueue/api.py`
- Create: `tests/test_api.py`

**Interfaces:**

- Produces: `parse_submission(payload) -> dict`
- Produces: `validate_priority(priority) -> None`

**Implementation:** define this module's own exception class
`InvalidSubmissionError(Exception)`. `parse_submission(payload)` takes
a dict shaped `{"job_id", "priority", "payload"}`; verify `job_id`,
`priority`, and `payload` are all present and non-empty, raising
`InvalidSubmissionError(f"submission rejected: field {field!r} is required")`
naming the specific field when one is missing. Return `{"job_id",
"priority": int, "payload", "status": "queued"}`.

Add a module constant `MIN_PRIORITY = 2` — submissions through this
endpoint require priority 2 or higher (a stricter floor than
directly-queued jobs, which accept priority 1). `validate_priority(priority)`
raises `ValueError(f"priority {priority} is not allowed")` when
`priority < MIN_PRIORITY`.

**Tests:** `tests/test_api.py` covering: a normal payload parses
correctly; a payload with an empty field raises the named
`InvalidSubmissionError` for that field; `validate_priority` accepts
priority 2 and rejects priority 1.

**Verification:** `pytest tests/test_api.py`

## Task 4: Notifier

**Files:**

- Create: `jobqueue/notifier.py`
- Create: `tests/test_notifier.py`

**Interfaces:**

- Produces: `notify(job_status) -> str`

**Implementation:** add a module constant `TIMEOUT_SECONDS = 30` — how
long `notify` waits for the notification channel to accept a delivery
before giving up.

`notify(job_status) -> str` maps a job's status to its outcome
message: `"queued"` -> `"job queued"`, `"running"` -> `"job started"`,
`"done"` -> `"job completed successfully"`, `"failed"` -> `"job
failed"`. These four are this pipeline's own job statuses; any other
value raises `ValueError(f"unknown job status: {job_status!r}")`.

**Tests:** `tests/test_notifier.py` covering: each of the four known
statuses maps to its message; an unrecognized status raises
`ValueError`.

**Verification:** `pytest tests/test_notifier.py`

## Task 5: Daily report

**Files:**

- Create: `jobqueue/reporter.py`
- Create: `tests/test_reporter.py`

**Interfaces:**

- Produces: `build_report(jobs) -> dict`

**Implementation:** add a module constant `TIMEOUT_SECONDS = 90` — how
long `build_report` waits for the export sink to accept the finished
report before giving up (this pipeline's daily report job talks to a
slower downstream than the notifier's own delivery channel, so this
module picks its own value independently).

`build_report(jobs)` takes a list of `{"job_id", "status"}` dicts and
returns `{"total": len(jobs), "by_status": {status: count for status
in ("queued", "running", "done", "failed")}}`, counting only those
four statuses in `by_status` — a job with any other status is still
counted in `total` but not broken out in `by_status`.

**Tests:** `tests/test_reporter.py` covering: `build_report` on a
small job list counts `total` and `by_status` correctly; a job with an
unrecognized status is counted in `total` but not in `by_status`.

**Verification:** `pytest tests/test_reporter.py`

## Task 6: Archiver

**Files:**

- Create: `jobqueue/archiver.py`
- Create: `tests/test_archiver.py`

**Interfaces:**

- Produces: `should_archive(job_status, age_days) -> bool`

**Implementation:** add a module constant `ARCHIVE_AFTER_DAYS = 30`.
`should_archive(job_status, age_days)` returns `True` when
`job_status` is `"done"` or `"failed"` and `age_days >=
ARCHIVE_AFTER_DAYS`, else `False`.

**Tests:** `tests/test_archiver.py` covering: a `"done"` job past the
threshold is archived; a `"running"` job is never archived; a `"done"`
job under the threshold is not archived.

**Verification:** `pytest tests/test_archiver.py`

