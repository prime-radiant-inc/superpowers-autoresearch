# Seeded-truth ledger — cp-x5-leases

Answer key for X5's arms (Task 11). NEVER surfaced to the Coding-Agent
or the Gauntlet-Agent. Everything here is synthetic.

Per the design doc: "SDD flow whose gate suite is expensive and
repeated at unchanged tree state + one mid-flow mutation leg where
re-run is REQUIRED." Prerequisite scorer: the substring-aware
duplicate-command counter (`score_x5_leases`, Task 7). Guard: "the
invalidation probe — mutate the tree mid-flow and the suite MUST
re-run (an arm that skips a required re-run fails regardless of
savings)."

## The gate-suite command

`pytest tests/` (or `pytest tests/test_X.py` for a single task's own
file) is this fixture's verification command, run naturally at three
or more points across a normal SDD flow on this plan even without any
lease mechanism: after Task 1's implementer finishes; after Task 2's
implementer finishes (Task 2's own verification is scoped to
`tests/`, the whole directory, per the plan text, since middleware
depends on the bucket); at any task-reviewer's own re-verification
pass; and again at Final Review / finishing. Every one of those
invocations before Task 3 lands runs against the SAME tree SHA once
Task 1+2 are both complete and nothing has changed — the duplicate-run
opportunity the lease arms are meant to collapse.

## The REQUIRED-rerun point — Task 3

**Location:** Task 3 modifies `ratelimit/token_bucket.py`'s default
capacity (`100` -> `10`) AFTER Task 1 and Task 2 have both already
passed the full suite once. **Why re-run is mechanically required, not
just policy:** `tests/test_middleware.py` (written in Task 2) asserts
the OLD default (`100` requests allowed before `allow_request` returns
`False`); Task 3's own text requires updating that assertion to `10`.
Any receipt recorded for `tests/` at Task 2's tree SHA is invalid the
moment Task 3's commit lands — the tree changed, and the old receipt's
green result no longer describes the current code. This is the
fixture's guard case: any lease/receipt mechanism (X5-A, X5-B) MUST
trigger a fresh `pytest tests/` run after Task 3, not reuse Task 2's
stale green receipt. An arm that skips re-running here — because "the
suite was already green" — is not just claiming an unearned savings,
it would ship a genuinely broken tree (Task 2's own test would still
assert the stale `100` default against code that now defaults to
`10`, and the update Task 3's text mandates for that test would go
unverified).

## Duplicate-run opportunity (what a lease should collapse)

Between "Task 1 done" and "Task 3 starts," the tree does not change.
Any `pytest tests/` invocation in that window (a reviewer double-
checking Task 2's work, a cautious re-run before Final Review) is,
by definition, re-verifying a tree state a prior receipt already
certified. `score_x5_leases` (Task 7) is the substring-aware counter
that should attribute these correctly: same command + same tree SHA =
a duplicate a lease-aware arm should skip (citing the receipt
instead); same command + a DIFFERENT tree SHA (anything after Task 3
lands) = a required, non-duplicate run.
