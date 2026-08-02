# Seeded-truth ledger — cp-x6-planframed

Answer key and design record for X6's owed plan-framed fixture
(queue-execution campaign, 2026-08-01, Task 7 / item 3 of
`reports/2026-08-cost-pathologies-campaign.md` §6's queue). NEVER
surfaced to the Coding-Agent or the Gauntlet-Agent — `story.md` names
no task, no dispatch shape, and gives no hint that batching, dispatch
count, or dispatch size is being measured. Everything here is
synthetic; no real system.

## Why this fixture exists, verbatim

Per §6 item 3: "**X6 plan-framed fixture.** Either a bigger,
less-trivial dozen-edits fixture that reads as SDD-shaped work under a
free-form prompt, or a story that explicitly frames the work as a plan
or task list — at the cost of then testing 'does X6 help once SDD is
engaged' rather than 'does X6 change whether SDD gets reached for.'
Either way it also owes the **MINE tier this campaign skipped** — a
mined-corpus dispatch-floor distribution — so the fixture's dispatch
counts have a real baseline to sit against."

This task took the second option: `story.md` explicitly names a plan
file and instructs the agent to execute it "using your
subagent-driven-development skill" (the same phrasing
`cp-x1-wavecap`/`cp-x1-edit-existing`/`cp-x7x9-conflicts` already use to
reliably engage SDD), rather than `cp-x6-smalledits`'s free-form "there
are a dozen small independent bugs... please fix all of them" framing,
which the campaign closeout's X6 row confirms produced **zero subagent
dispatches** on its one graded rep — a single rollout file, no child
threads, `npm test` 15/15, $0.49, under a minute (report §2's X6 row).
That gate rep never reached the task loop at all, so neither X6-A's
batching text nor X6-B's inline-when-trivial text — both scoped to
"## The Task Loop," reached only once SDD's per-task dispatch loop is
already running — ever had an occasion to differ from control on that
fixture (report §2: "There is no mechanism by which either arm could
change control's dispatch count on this prompt").

## The disclosed trade-off, stated here (not in the story)

**This fixture tests "does X6 help once SDD is engaged," not "does X6
change whether SDD is reached for."** By explicitly naming a plan file
and instructing "using your subagent-driven-development skill,"
`story.md` all but guarantees the Coding-Agent invokes SDD and its Task
Loop — which is exactly what `cp-x6-smalledits`'s free-form framing
failed to do. That gain comes at the cost of no longer being able to
measure whether X6-A's or X6-B's text changes a session's PROPENSITY to
invoke SDD in the first place on a dozen-small-edits job — this
fixture cannot speak to that question at all, by construction. Any
future battery or report citing this fixture's results must carry this
caveat forward: a result here is about dispatch SHAPE once inside the
Task Loop, never about dispatch REACHABILITY.

## The plan: `docs/superpowers/plans/util-bugfix-plan.md`

Twelve tasks, reusing the exact same seeded work as
`cp-x6-smalledits/fixtures/util/*.js` and `tests/*.js` (byte-identical
copies — same twelve bugs, same twelve tests, same `package.json`; see
that scenario's own `seeded-truth-ledger.md` for the bug-by-bug
rationale and the "why independent matters" note, which applies
identically here). What changes is only the FRAMING: instead of a free
-form "there are a dozen small independent bugs... read `BUGS.md`"
prompt, the same twelve fixes are now the plan's twelve tasks, and
`BUGS.md` is dropped — the plan document is the sole task source, and
`story.md` tells the agent to read the plan, not to go hunting.

**Mechanical smallness criterion, verified by
`test_cp_x6_planframed.py`:** every one of the twelve `## Task N:`
blocks names exactly ONE file, and that file is always a `Modify:`
entry (never a `Create:`) — never more than one file per task, and no
task ever introduces a new file. No task's `Files:` block names a file
another task's `Files:` block also names (the twelve are pairwise
file-disjoint, same independence property `cp-x6-smalledits`'s ledger
documents). No task needs a new or updated test — the plan's own
"Global Constraints" section says so directly, and it's true: each
file's existing test already exercises the one line the task changes.
This is what keeps the batching-vs-per-task-dispatch decision LIVE in
every single task: per `cp/x6a`'s and `cp/x6b`'s own diffs (both
patching `skills/subagent-driven-development/SKILL.md`'s "## The Task
Loop" section on `sim/dev-postmerge`), X6-A's batching rule applies to
"several tasks that are each a small, independent edit of the same
kind," and X6-B's inline-when-trivial boundary applies to "a single,
mechanical edit... that needs no new or updated test and no design
judgment" while explicitly excluding anything that "touches more than
one file, needs a new or updated test, or calls for judgment about
approach." Every one of these twelve tasks satisfies X6-A's shape AND
sits on the permissive side of X6-B's boundary — a plan built any
other way (multi-file tasks, tasks needing new tests) would push some
tasks out of scope for one or both arms and confound the comparison.

## Dispatch-shape signature — what distinguishes the arms

`checks.sh`'s own assertions stay behavior-neutral (same discipline as
`cp-x6-smalledits/seeded-truth-ledger.md`'s "What is NOT measured
here" section) — nothing in `checks.sh` asserts dispatch count,
`Agent`/`Task` tool-call count, or batching shape; that is exactly what
a future battery's scorer is for. The scorer is `score_x6_floor.py`
(Task 2, corpus-validated, unmodified) — its `dispatch_floor()`
resolves every `spawn_agent` dispatch in a rollout tree and reports
each one's `total_tokens` (a cumulative floor cost) and
`useful_output_tokens` (a size-of-delivered-work proxy), so its
`floor_ratio` is the floor tax per dispatch. On THIS fixture, the
predicted signature per arm (not yet observed — no real reps have run
against this fixture; see Validation below) is:

- **Control (unpatched base):** something close to twelve separate
  `spawn_agent` dispatches, one per task, each paying its own context
  floor — `dispatch_floor()` reports roughly twelve entries, most with
  a high `floor_ratio` (small `useful_output_tokens` against a fixed
  floor cost each).
- **X6-A (batching rule):** dispatch count converging toward ONE (or a
  small number of) batch dispatch(es) covering several/all twelve
  tasks in one brief — `dispatch_floor()` reports few entries, each
  with a much lower `floor_ratio` (the same floor cost now amortized
  over many tasks' worth of `useful_output_tokens`).
- **X6-B (inline-when-trivial):** dispatch count converging toward
  ZERO — the controller does some or all twelve fixes itself, in its
  own turn, with no `spawn_agent` call at all — `dispatch_floor()`
  reports few or no entries, because there is no dispatch to score
  (the savings show up as an absence, not as a cheaper dispatch).

`test_cp_x6_planframed.py` validates that `score_x6_floor.dispatch_floor()`
correctly discriminates a batched-dispatch transcript from a
per-task-dispatch transcript on synthetic rollout data shaped like THIS
scenario (twelve tasks) — see `fixtures/cp-x6-planframed-dispatch-
shapes/{batched,per-task}/` and that test file's own docstring. This
confirms the INSTRUMENT can tell the three predicted shapes apart; it
is not itself evidence about which shape a real session produces.

## MINE tier — a real baseline for dispatch counts

Per §6 item 3's second half ("it also owes the MINE tier this campaign
skipped... so the fixture's dispatch counts have a real baseline to sit
against"): `campaigns/cost-pathologies/x6_mine_dispatch_floor.py`
(committed alongside this fixture) computes the AGGREGATE per-session
dispatch-count and per-dispatch size distribution over any corpus root
supplied on its command line, reusing `score_x6_floor.py`'s own tested
per-dispatch scoring. It was run once, read-only, against the mined
corpus this campaign's design doc cites (aggregate numbers only — see
this task's report, not this ledger, for the resulting distribution
table; the corpus itself is never committed and no corpus-derived
figure beyond aggregate counts/percentiles/histograms belongs in any
committed file, this one included). That baseline is descriptive
context for whatever a future battery's control-arm dispatch count
turns out to be — it is not a prediction this fixture's own control arm
is expected to match, since the mined corpus's sessions are real,
varied production work, not this fixture's twelve-tiny-independent-
edits shape.

## Validation (controller ruling, no container/API spend)

Per the same controller ruling `cp-x1-edit-existing` and
`cp-x1-wavecap` operated under, this task spends no containers or API
budget on real reps. `campaigns/cost-pathologies/test_cp_x6_planframed.py`
validates, against this scenario's own committed fixtures:

1. **Setup determinism.** Two independent copies of `fixtures/` are
   byte-identical, and the materialized starting tree's `npm test` run
   is deterministic and reproduces the same known pre-fix result twice
   in a row (matching `cp-x6-smalledits/seeded-truth-ledger.md`'s
   documented baseline for this identical fixture content: 14 failing /
   1 passing out of 15 total assertions). "Green" here means the
   harness itself runs cleanly to a reproducible result — not that the
   tests pass; they are seeded to fail until the plan's twelve fixes
   land.
2. **Plan task-structure / smallness.** The plan parses into exactly
   twelve `## Task N:` blocks; every block's `Files:` section names
   exactly one file, always as a `Modify:` entry; no two tasks name the
   same file.
3. **Dispatch-shape discrimination.** `score_x6_floor.dispatch_floor()`
   reports 1 dispatch on the constructed batched-dispatch synthetic
   transcript and 12 on the constructed per-task-dispatch synthetic
   transcript, both shaped like this scenario's own twelve tasks.

This task's brief line ("MICRO validation (2 reps)") predates the
controller ruling that produced the `cp-x1-edit-existing`/
`cp-x1-wavecap` committed-pytest-only precedent; this task follows the
ruling actually handed to it (no container spend, a committed pytest
covering the three properties above) rather than dispatching real reps.
