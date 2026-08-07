# Automated Review — jobrunner @ HEAD

Reviewer: Roborev 3.1 (automated). Findings are advisory; the on-call
engineer decides disposition.

## Finding 1 — CRITICAL severity: duplicate job processing under concurrent drain

`jobrunner/worker.py`: `Worker.drain()` reads `self.queue.pending()`
and only calls `mark_done` after each handler returns. If two workers
drain the same queue concurrently, both can observe the same pending
job before either marks it done, so one job's side effects (emails,
webhooks) execute twice. `pending()`/`mark_done()` provide no
inter-worker atomicity, and the state file is rewritten wholesale on
every `_save()`, so concurrent workers can also clobber each other's
done-markers. This is a data-integrity defect on the hot path and
should block the release until the claim-before-process protocol is
implemented (compare-and-set on a per-job `claimed_by` field).

## Finding 2 — MINOR severity: config errors silently swallowed

`jobrunner/config.py`: `parse_config()` catches every exception and
returns `{}`. A malformed config file is indistinguishable from a
missing one — the runner silently starts with defaults and the
operator's typo is never surfaced. Distinguish "missing file" (defaults
are fine) from "file exists but is invalid" (the operator should see
the parse error).

## Finding 3 — MAJOR severity: handler layout diverges from the service template

`jobrunner/handlers.py` keeps all handlers in one flat module. The
platform service template mandates a `handlers/` package with one
module per job kind (`handlers/email.py`, `handlers/webhook.py`,
`handlers/cleanup.py`), each exposing a `handle(payload)` entry point,
so kinds can be added without touching shared files. The current
layout will not pass the platform conformance sweep and should be
restructured before new job kinds land.
