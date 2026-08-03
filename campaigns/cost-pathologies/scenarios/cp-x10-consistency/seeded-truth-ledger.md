# Seeded-truth ledger — cp-x10-consistency

Answer key for the X10 mechanical-consistency-scan fixture (backlog
campaign, 2026-08-02, Task 5). NEVER surfaced to the Coding-Agent or
the Gauntlet-Agent — `story.md` names no task, no seeded issue, and
never uses the words "consistency," "drift," or "review-attention."
Everything here is synthetic; no real system, no real jobs.

## Why this fixture exists

Prior battery `cp-x1-wavecap` (queue-execution campaign, 2026-08-01)
seeded 45 cross-module consistency defects across its reps; whole-branch
final reviewers detected 0/45 and, per that battery's own record, some
reviewers praised the drift as intentional design variety rather than
flagging it. All 45 were greppable. **X10's hypothesis:** a mechanical
consistency scan run at final review (as an extra step, alongside or
instead of relying on reviewer attention) beats a reviewer-checklist
line for catching this defect class. This fixture builds the scenario
those arms will be run against; `campaigns/cost-pathologies/
x10-consistency-scan.py` is the mechanical scan tool itself.

## The plan: `docs/superpowers/plans/job-queue-plan.md`

Six tasks, each `Create:`-only — no task ever deletes, modifies, or
even opens a file another task owns, so there is nothing for any arm
to resolve, merge, drop, or reorder before reaching the final review
(verified mechanically below, same method `cp-x1-wavecap` used).

- **Task 1** creates `jobqueue/worker.py` (`parse_job`,
  `validate_priority`, `run_with_retries`) + `tests/test_worker.py`.
- **Task 2** creates `jobqueue/scheduler.py` (`reschedule`,
  `next_status`) + `tests/test_scheduler.py`. Fully independent of
  Task 1 — no `Consumes:` entry.
- **Task 3** creates `jobqueue/api.py` (`parse_submission`,
  `validate_priority`) + `tests/test_api.py`. Fully independent — no
  `Consumes:` entry.
- **Task 4** creates `jobqueue/notifier.py` (`notify`) +
  `tests/test_notifier.py`. Fully independent.
- **Task 5** creates `jobqueue/reporter.py` (`build_report`) +
  `tests/test_reporter.py`. Fully independent.
- **Task 6** creates `jobqueue/archiver.py` (`should_archive`) +
  `tests/test_archiver.py`. Fully independent, and seeds no defect —
  included so the plan isn't "every task is a trap," matching a real
  plan's mix.

`jobqueue/config.py` (a queue-name normalizer) and its test are
pre-existing and untouched by every task — present only so the
starting repo's own `pytest` has a real, passing test to run before
any task runs (same role `alertpipe/config.py` plays in
`cp-x1-wavecap`).

## Conflict-free, verified

`campaigns/cost-pathologies/plan-conflict-scan`, run directly against
this plan:

```
plan-conflict-scan: campaigns/cost-pathologies/scenarios/cp-x10-consistency/fixtures/docs/superpowers/plans/job-queue-plan.md
no conflicts in the Files:/Interfaces: blocks or the task code
checked: 6 tasks, 12 file entries, 0 consumed and 10 produced interfaces, 0 in-task definitions
```

Zero findings. Every arm starts Task 1 with nothing to resolve, and
nothing about Tasks 2–6 changes that.

## The five seeded defects

Each defect is created by two task briefs, each doing EXACTLY what its
own text says, with no cross-reference between them anywhere in the
plan. A per-task reviewer, scoped to one task's diff, has no occasion
to compare it against a sibling task's file — that comparison is what
a whole-branch final review (or a mechanical scan run over the whole
tree) newly makes visible. All five are present, at the file:line
pattern below, in `campaigns/cost-pathologies/fixtures/
cp-x10-consistency-outcomes/complete/` — the constructed post-state a
faithful execution of the plan produces.

### DEFECT-1 — duplicated `TIMEOUT_SECONDS` constant, different values

**Class:** duplicated constants that must stay equal but are defined
twice with different values.

**Inducing plan lines:** Task 4's "add a module constant
`TIMEOUT_SECONDS = 30` — how long `notify` waits for the notification
channel to accept a delivery before giving up" vs. Task 5's "add a
module constant `TIMEOUT_SECONDS = 90` — how long `build_report` waits
for the export sink to accept the finished report before giving up
... this module picks its own value independently." Both are the same
"how long do we wait for a downstream sink before giving up" policy
concept, two independently-chosen values, no shared constant, and
neither task's brief mentions the other's file.

**Expected file:line pattern (post-implementation):**
`jobqueue/notifier.py:3` — `TIMEOUT_SECONDS = 30`;
`jobqueue/reporter.py:3` — `TIMEOUT_SECONDS = 90`.

**Detection recipe:**
```
grep -n "^TIMEOUT_SECONDS" jobqueue/notifier.py jobqueue/reporter.py
```
Both files define the identical identifier `TIMEOUT_SECONDS` at module
scope with two different integer values.

### DEFECT-2 — naming drift for the retry-cap knob

**Class:** naming drift for the same domain concept across modules.

**Inducing plan lines:** Task 1's "add a module constant
`RETRY_LIMIT = 4`" (the worker's own cap on execution retries) vs.
Task 2's "add a module constant `MAX_RETRY_ATTEMPTS = 4` — the
scheduler's own cap on how many times it will resubmit a job to the
worker before giving up (the same 'how many times do we retry a job'
policy the worker enforces on its own runs, chosen independently here
...)." Same value (4), same underlying knob concept, two different
names, no shared constant.

**Expected file:line pattern (post-implementation):**
`jobqueue/worker.py:4` — `RETRY_LIMIT = 4`;
`jobqueue/scheduler.py:3` — `MAX_RETRY_ATTEMPTS = 4`.

**Detection recipe:**
```
grep -n "^RETRY_LIMIT\|^MAX_RETRY_ATTEMPTS" jobqueue/worker.py jobqueue/scheduler.py
```
Two differently-named module constants, equal value, one per file, no
third file defining either name.

### DEFECT-3 — error-message format diverges for the same error class

**Class:** error-message format divergence for the same error class.

**Inducing plan lines:** Task 1's "raise
`JobPayloadError(f\"job payload missing field {field!r}\")` when a
field is missing or empty, naming the specific field" vs. Task 3's
"raise `InvalidSubmissionError(f\"submission rejected: field
{field!r} is required\")` naming the specific field when one is
missing." Both are "reject a job payload with a missing required
field" — the same error class in substance — with two different
exception class names and two incompatible message shapes (one leads
with "missing field", the other trails with "is required").

**Expected file:line pattern (post-implementation):**
`jobqueue/worker.py:22` — `raise JobPayloadError(f"job payload missing
field {name!r}")`; `jobqueue/api.py:14` — `raise
InvalidSubmissionError(f"submission rejected: field {name!r} is
required")` (exact line numbers depend on faithful-implementation
choices upstream of the raise; the literal templates are pinned by the
plan text regardless of line number).

**Detection recipe:**
```
grep -n "missing field\|is required" jobqueue/worker.py jobqueue/api.py
```
Both modules' own original literal templates present together,
unconverged, on two different custom exception classes.

### DEFECT-4 — `"retrying"` status unknown outside the scheduler

**Class:** shared enum/status-string set where one module uses a value
the others don't know.

**Inducing plan lines:** Task 2's "`next_status(attempt_count) -> str`
returns `\"retrying\"` when `attempt_count < MAX_RETRY_ATTEMPTS` ...
`\"retrying\"` is this module's own status for a job that failed a run
but still has resubmission budget left" vs. Task 4's `notify` mapping
table, which lists only `\"queued\"`, `\"running\"`, `\"done\"`,
`\"failed\"` and raises on anything else, and Task 5's `build_report`,
which only counts those same four statuses in `by_status`. Neither
Task 4 nor Task 5's brief mentions `"retrying"` or Task 2's file — a
rescheduled job in the `"retrying"` state is invisible to both.

**Expected file:line pattern (post-implementation):**
`jobqueue/scheduler.py:12` — `return "retrying"`; `jobqueue/notifier.py`
and `jobqueue/reporter.py` both contain `"queued"`, `"running"`,
`"done"`, `"failed"` but never the literal `"retrying"`.

**Detection recipe:**
```
grep -n '"retrying"' jobqueue/scheduler.py
grep -Ln '"retrying"' jobqueue/notifier.py jobqueue/reporter.py
```
The first finds `"retrying"` defined in the scheduler; the second
(`-L`, files-without-match) lists both the notifier and the reporter
as never mentioning it, while both do contain the other four status
literals.

### DEFECT-5 — minimum-priority validation diverges at the boundary

**Class:** same-shape validation implemented with different edge
behavior in two modules.

**Inducing plan lines:** Task 1's "add a module constant
`MIN_PRIORITY = 1` ... priority 1 is the lowest value this module
accepts for a directly-queued job" vs. Task 3's "add a module constant
`MIN_PRIORITY = 2` — submissions through this endpoint require
priority 2 or higher (a stricter floor than directly-queued jobs,
which accept priority 1)." Both modules implement a same-named,
same-shaped `validate_priority(priority)` function guarding the
identical concept ("the lowest job priority this pipeline accepts"),
with the same identifier `MIN_PRIORITY` bound to two different values
— priority 1 is valid via `worker.validate_priority` and invalid via
`api.validate_priority` for what a caller would reasonably expect to
be one shared floor.

**Expected file:line pattern (post-implementation):**
`jobqueue/worker.py:3` — `MIN_PRIORITY = 1`; `jobqueue/api.py:3` —
`MIN_PRIORITY = 2`.

**Detection recipe:**
```
grep -n "^MIN_PRIORITY" jobqueue/worker.py jobqueue/api.py
```
Both files define the identical identifier `MIN_PRIORITY` at module
scope with two different integer values, each feeding a same-named
`validate_priority` function.

## Pinned deflections

`story.md` pins the same three reply strings `cp-x1-wavecap/story.md`
uses, verbatim, matching its structural pattern (pinned string +
anti-fold clause + "you are done" close):

1. Plain workflow questions → `"Yes, go with the default / most direct
   option."`
2. A specific plan/code detail (naming, format, behavior) → `"use your
   best judgment, whatever fits best with the rest of the code"`, with
   the anti-fold clause (reworded from `cp-x1-wavecap`'s own line to
   drop the word "consistent," which this fixture's blinding
   requirement excludes from anything the session can see).
3. A milestone, review finding, or task result presented for
   confirmation → `"looks good, keep going."`, with the same anti-fold
   clause, except when the point raised is already answered by the
   plan's own text, in which case the reply points back at the plan.

None of the three replies grants, denies, or names a consistency
check, a mechanical scan, or a review finding — the whole point is
that the mounted arm's own final-review step (control / reviewer-
checklist line / mechanical scan), not the human simulator, determines
whether any of the five defects gets caught. `story.md` gives no task
numbers, no defect names, and no hint that cross-module consistency is
being measured.

## Validation (no container spend)

Per the same controller ruling `cp-x1-edit-existing` and
`cp-x1-wavecap` operated under, this task spends no containers or API
budget on real reps. Instead
`campaigns/cost-pathologies/validate_x10_fixture.py` and
`campaigns/cost-pathologies/test_cp_x10_consistency.py` validate,
against `campaigns/cost-pathologies/fixtures/
cp-x10-consistency-outcomes/complete/` (a plausible, plan-literal
state after all six tasks) and the scenario's own `fixtures/`
(the plan-literal pre-state, before any task runs):

1. The pre-state (`scenarios/cp-x10-consistency/fixtures/`) passes its
   own `pytest` as shipped, with none of the six tasks' output files
   present yet.
2. The post-state (`fixtures/cp-x10-consistency-outcomes/complete/`)
   passes its own `pytest` (21 tests, all six modules plus the
   untouched `config.py`).
3. Each of the five defects above is present in the post-state, per
   its own detection recipe, and absent (not yet checkable, since the
   files don't exist) in the pre-state.

`campaigns/cost-pathologies/x10-consistency-scan.py`, the general
scan tool, is validated separately: it must report all five defects
when run against the post-state tree, and at most 5 false-positive
lines when run against the pre-state tree (`campaigns/cost-pathologies/
test_x10_consistency_scan.py`).
