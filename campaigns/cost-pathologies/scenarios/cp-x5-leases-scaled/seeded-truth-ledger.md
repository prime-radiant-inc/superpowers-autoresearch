# Seeded-truth ledger — cp-x5-leases-scaled

Answer key for a scaled X5 battery (queue-execution campaign Task 9,
item 6 of `reports/2026-08-cost-pathologies-campaign.md` §6). NEVER
surfaced to the Coding-Agent or the Gauntlet-Agent. Everything here is
synthetic. Base template: `cp-x5-leases`'s own ledger (same
gate-suite / required-rerun / duplicate-run-opportunity structure),
scaled from a 3-task plan to 5 tasks so the worst-case duplicate count
reaches item 6's target instead of the 3-task fixture's much smaller
one.

Why the old fixture couldn't answer item 6: "3 reps × a 3-task plan
cannot separate a real 10-15% reduction from ordinary SDD variance, and
this fixture's scope may be structurally too small to show the
duplicate-verification worst case the design doc names." The design
doc's own "12x" was a rough narrative quote; the report's corrected,
mechanically-reproduced anchor is **10** (Task 7's independent hand
recount of the same exemplar, under the X5 scorer's same-command-text
definition). This fixture's structure is sized to make a comparable
order of magnitude reachable, not to hit 10 exactly.

## The plan's per-task verification commands (mandated, not descriptive)

Straight from `fixtures/docs/superpowers/plans/dispatch-queue-plan.md`:

| Task | Verification command | Scope, per the plan's own text |
|---|---|---|
| 1 (queue) | `pytest tests/test_queue.py` | own file only — no integration surface exists yet |
| 2 (worker pool) | `pytest tests/` | full suite — depends on Task 1's ordering/capacity contract |
| 3 (retry policy) | `pytest tests/` | full suite — re-enqueues through Task 1's queue, interacts with Task 2's assignment path |
| 4 (lower default capacity) | `pytest tests/` | full suite, REQUIRED — invalidates Tasks 1-3's own already-passing assertions |
| 5 (dead-letter handling) | `pytest tests/` | full suite — first path exercising Tasks 1-4 together |

Two tasks' own plan text explicitly names the re-verification pressure
for a reviewer, per the brief's "at least two tasks whose review
naturally tempts a full-suite re-run" lever:

- **Task 3**: "this is exactly the kind of change a reviewer should be
  nervous could have silently broken an earlier guarantee, not one to
  sign off on from `retry.py`'s own file in isolation."
- **Task 5**: "a reviewer here has the strongest reason anywhere in
  this plan to want every test green, not just `deadletter.py`'s own
  file, since this is where any latent mismatch between the earlier
  tasks would first surface."

## The gate-suite command and its duplicate-run windows

`pytest tests/` is the fixture's shared, growing gate suite. Because
Tasks 2 through 5 each mandate the FULL suite (not a per-task file) as
their own verification command — a real consequence of each task
genuinely depending on the previous tasks' guarantees, not an
arbitrary choice — the tree stabilizes at a new SHA after each of
those four tasks' implementer commits, and stays there until the next
task's implementer commits. Call these four stable states
`SHA_2`..`SHA_5`. Task 1's own command (`pytest tests/test_queue.py`,
file-scoped) is a DIFFERENT `command_norm` under `score_x5_leases` and
never joins the `pytest tests/` duplicate groups below — Task 1's
window is deliberately excluded from the headline count, keeping it
conservative.

For each of the four windows, up to three genuinely-plausible
occurrences of `pytest tests/` can land at that window's unchanged
SHA, even without any lease mechanism:

1. **The implementer's own mandated run** (per the plan's Verification
   line) — legitimate, the first occurrence, not a duplicate.
2. **The task-reviewer's own re-verification pass** — SDD's base text
   (unpatched `subagent-driven-development/SKILL.md`, `sim/dev-postmerge`)
   already says "the implementer's report carries the test evidence,"
   but nothing MECHANICALLY prevents a reviewer from re-running the
   full suite itself anyway, a routine caution behavior real sessions
   exhibit (documented directly in `cp-x5-leases`'s own corpus). A
   duplicate at the SAME SHA.
3. **A cautious pre-next-task check** (Tasks 2-4: the controller
   double-checks the tree is green before dispatching the next task's
   implementer) or, for Task 5 specifically (no next task exists),
   **Final Review's own re-verification pass** before declaring the
   plan done. A second duplicate at the SAME SHA.

That is 2 avoidable duplicate `pytest tests/` runs per window x 4
windows = **8 duplicated runs available to an undisciplined session**
(12 total occurrences across the 4 duplicate groups: 4 legitimate +
8 duplicated), satisfying item 6's "structurally too small" complaint
— an order of magnitude the 3-task original could not reach (its own
ledger describes only ONE such window).

## The REQUIRED-rerun point — Task 4 (the guard)

**Location:** Task 4 modifies `dispatchqueue/queue.py`'s default
capacity (`100` -> `20`) AFTER Tasks 1, 2, and 3 have each already
passed the full suite at least once. **Why re-run is mechanically
required, not just policy:** `tests/test_queue.py` (Task 1),
`tests/test_workers.py` (Task 2), and `tests/test_retry.py` (Task 3)
each assert the OLD default (`100`); Task 4's own text requires
updating all three to `20`. Any receipt recorded for `pytest tests/`
at `SHA_3` (Task 3's stable state) is invalid the moment Task 4's
commit lands — the tree changed, and the old receipt's green result no
longer describes the current code. An arm that skips re-running here
because "the suite was already green at `SHA_3`" is not just claiming
an unearned savings, it would ship a genuinely broken tree: three
separate prior tasks' own tests would still assert `100` against code
that now defaults to `20`.

`SHA_4`'s window (Task 4's own row in the table above) is one of the
four windows already counted in the 8-duplicate figure; the guard's
required, NON-duplicate event is the implementer's own fresh
`pytest tests/` run that establishes `SHA_4`'s (first, legitimate)
verification occurrence in that window — mechanically forced
regardless of lease discipline, since `score_x5_leases`'s
`duplicate_groups` keys strictly on `(command_norm, tree_sha)` and a
`SHA_3` receipt can never satisfy a `SHA_4` check.

## What lease-honoring evidence looks like, per arm

Per `score_x5_leases.py`'s own SPEC (the module docstring's "a SPEC,
not a discovered format" section) and Task 2's (queue-campaign) added
prose detector — both channels apply to BOTH arms; the difference
between X5-A and X5-B is which channel the real corpus showed each
arm actually using (report §2 X5 section), not which channel is
"correct" for that arm.

**Strict grammar** (`_LEASE_LINE_RE`, line-anchored, case-sensitive):

```
LEASE-RECEIPT: command=<command_norm> tree_sha=<sha> result=<pass|fail>
LEASE-HONORED: command=<command_norm> tree_sha=<sha>
LEASE-INVALIDATED: command=<command_norm> tree_sha=<sha>
```

- **X5-A** (`cp/x5a`, receipts in the implementer's own report/final
  message): `implementer-prompt.md`'s patched Report Format mandates a
  `LEASE-RECEIPT:` line after every task's own mandated verification
  run, repeated in the final short-status message. A later seat cites
  it by putting `LEASE-HONORED:`/`LEASE-INVALIDATED:` directly into
  ITS OWN dispatch or report text (`SKILL.md`'s patched reviewer-
  dispatch and fix-round text).
- **X5-B** (`cp/x5b`, a machine-checkable receipts file): the same
  three markers, but appended to a per-task `…/task-N-receipts.md`
  file (named alongside the report file) instead of living in prose;
  a later seat `cat`s or `grep`s that file before composing its own
  dispatch, per `SKILL.md`'s patched text ("run `cat` on the task's
  receipts file yourself... rather than trusting your own memory of
  it").

**Prose forms** (Task 2's `_lease_events_prose()` — real corpus
finding, report §2 X5 section: "codex reviewers under X5-A routinely
narrate honoring or declining a supplied lease receipt in their OWN
WORDS rather than reproducing the fixed marker syntax"): a lease/
receipt TERM ("lease" or "receipt") and an explicit rerun-or-not
PHRASE co-occurring on the same line, e.g.:

- Honored: "Full-suite verification was not rerun per review
  constraints; the provided lease receipt reports 44 passed."
- Declined/invalidated: "The implementation report's lease receipt
  does not certify the reviewed commit; independent focused
  verification was run."

## Predicted per-arm signatures

These are MECHANICAL predictions for a maximally arm-compliant
transcript — what `lease_stats()` reports when a session actually
follows its arm's own injected instructions at every one of the four
windows and the Task 4 guard point. They are what this scenario's
`test_cp_x5_leases_scaled.py` constructs and scores directly, to prove
the scorer discriminates a disciplined transcript from an undisciplined
one. They are NOT a prediction of what a real Coding-Agent battery will
produce — `cp-x5-leases`'s own real battery (report §2 X5 section)
found BOTH real arms' `duplicate_groups` means landed AT OR ABOVE
control's at n=3 ("savings UNPROVEN... unchanged by any correction"),
so this scaled fixture's own real battery (the controller's job, not
this ledger) is what actually answers item 6, not this table.

**A dedup subtlety that shapes these numbers (read before trusting
`lease_events` as a savings count):** `_lease_events()` dedups on
`(kind, command_norm, tree_sha)` (Task 2, item 10) — this correctly
collapses a re-READ of the identical historical line (the bug that
motivated item 10), but it ALSO collapses two seats INDEPENDENTLY
honoring the same fact ("`pytest tests/` still holds at this SHA"),
since both produce byte-identical `(command_norm, tree_sha)` regardless
of who said it or how many times. A window where BOTH the task-reviewer
AND a cautious pre-next-task check each decide to honor the same
receipt is therefore still only **1** distinct `HONORED` event, even
though 2 real re-runs were avoided. `lease_events` is a lower bound on
decisions made, not a count of runs avoided — the actual runs-avoided
proof is `duplicate_groups` staying at 0 (see the discrimination test's
own two-occasion construction, which mechanically demonstrates this).
The per-arm counts below are written to the model where each window's
avoided duplicate collapses to a SINGLE honoring citation (the simplest
compliant shape, and the one this scenario's constructed transcripts
use), not two.

| Arm | `duplicate_groups` (`pytest tests/`) | strict `lease_events` | prose `lease_events` | guard |
|---|---|---|---|---|
| **Control (X5-C)** | up to 4 groups, worst case count 3 each (the full 8-duplicate structural opportunity — no mechanism suppresses it) | all zero (no grammar exists under control) | all zero | required `SHA_4` run still happens (base SDD re-runs after any change; no lease needed for correctness, only for the savings question) |
| **X5-A compliant** | 0 groups (each window's 2 would-be-duplicate occasions never happen — the receipt already answers the question) | 4 `LEASE-RECEIPT` (one per window; the Report Format's receipt line is mandated grammar in both arms), 0 `LEASE-HONORED`, 0 `LEASE-INVALIDATED` — X5-A's reviewers narrate the honor/decline decision in their own words instead (real corpus finding) | 4 `receipts_honored_prose` (one per window's honoring decision) + 1 `invalidation_reruns_prose` (the `SHA_3` guard decline) | holds: the `SHA_3`-stale receipt is declined in prose, a fresh `SHA_4` receipt is issued and cited going forward |
| **X5-B compliant** | 0 groups, same mechanism as X5-A | 4 `LEASE-RECEIPT`, 4 `LEASE-HONORED` (one per window), 1 `LEASE-INVALIDATED` (the `SHA_3` guard event) — a `cat`/`grep`'d file is the machine-checkable channel this arm's own text points at | little to none — X5-B's mechanism is file-based, not narrated | holds, same shape as X5-A |

Total distinct events for a maximally compliant arm (either channel
split): 4 `RECEIPT` + 4 `HONORED` + 1 `INVALIDATED` = **9** distinct
events — the two arms differ in which CHANNEL (strict grammar vs. Task
2's prose detector) carries the 5 honor/decline decisions, not in the
count of decisions made or in `duplicate_groups`, which is the number
that actually stands in for "runs avoided" and is identical (0) for
both compliant arms.

## Discrimination guard (pre-registered, mirrors `cp-x5-leases`'s own)

An arm's `duplicate_groups` reduction is credited as a REAL savings
signal only jointly with the guard holding: the `SHA_4` window's
verification run (or an explicit `LEASE-INVALIDATED` citing `SHA_3`
followed by a fresh `SHA_4` receipt) must be present in every rep,
regardless of arm. An arm that shows 0 `duplicate_groups` AND skips the
`SHA_4` re-run entirely is not "efficient" — it shipped a broken tree
and fails regardless of its savings number, per the same rule
`cp-x5-leases`'s own ledger states.
