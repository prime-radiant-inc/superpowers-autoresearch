# Job Queue Pipeline — Product Specification

Synthetic fixture; no real jobs, no real HTTP server, no real
notification channel. Python 3.11+, standard library only at runtime,
tests run via `pytest`.

## Overview

A small in-process job queue pipeline for a single-tenant background
worker system: jobs enter either by being queued directly or by
submission through an endpoint, run with bounded retries, get
rescheduled when a run fails, generate outbound notifications and a
daily operations report, and are archived once they've aged out.

## Pre-existing code

`jobqueue/config.py` already exists and holds queue-name
normalization (`normalize_queue_name`, `DEFAULT_QUEUE`). Do not remove
or rename anything already in it.

## Downstream timeouts

Any component that waits for a downstream sink to accept a delivery —
a notification channel, a report export destination, or a future
integration — uses the same wait budget before giving up:
`TIMEOUT_SECONDS = 30`. This is one shared policy, not a per-component
choice; every module that defines this constant must agree on the
value.

## Retry policy

A job gets a bounded number of attempts before the pipeline gives up
on it, and this cap is a single shared policy no matter which
component is enforcing it — a worker retrying its own run and a
scheduler deciding whether to resubmit a job are both applying the
same "how many times do we retry a job" rule. The cap is
`RETRY_LIMIT = 4`. Every module that tracks this cap uses the name
`RETRY_LIMIT`, not a locally invented synonym, so the value is
greppable as one concept across the codebase.

## Job statuses

The pipeline recognizes five job statuses end to end: `"queued"`,
`"running"`, `"retrying"`, `"done"`, and `"failed"`. `"retrying"`
marks a job that failed a run but still has resubmission budget left
— it is a first-class pipeline status, not an implementation detail
private to whichever component reschedules the job. Every component
that reports on, counts, or maps job status (outbound notifications,
the daily report, and anything added later) must handle all five
statuses, not just the four terminal-ish ones.

## Payload validation

A job's data — however it enters the pipeline, whether queued
directly or submitted through the endpoint — must include a job
identifier, a priority, and a payload body. Whenever a required field
is missing or empty, the pipeline raises the same error regardless of
entry point: `JobPayloadError`, with message `"job payload missing
field {field!r}"`, naming the specific field. A caller should never
see two different exception types or two differently worded messages
for the same underlying problem depending on which entry point they
used.

## Priority floor

The pipeline enforces one minimum priority across every entry point:
`MIN_PRIORITY = 1`. A job at priority 1 is valid no matter how it
enters the queue — there is no separate, stricter floor for one entry
point versus another; every component that validates priority agrees
on this same floor.

## Archiving

A job becomes eligible for archiving once it reaches a terminal
status (`"done"` or `"failed"`) and has aged past the retention
window.
