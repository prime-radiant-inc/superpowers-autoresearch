# E3 evidence receipts / duplicate-gate scorer (Task 10)

**Status: scorer built + validated against corpus ground truth; MINE-tier
free re-score complete; FULL baseline (`cx-finishing`) and waiver probe
(`cx-finishing-waiver`) batteries pending.** This is a working document,
updated as each stage completes (not append-only — see the hypothesis
log's dated entries for the append-only history).

## What was built

- `rollout_parser.mutation_events(path) -> list[str]`: sorted timestamps
  of every successful `patch_apply_end` plus every exec command matching
  `\bgit (commit|merge|rebase|reset|checkout)\b` — the "did anything
  change the tree" signal the duplicate-gate check needs. TDD, one
  fixture test class (6 tests). Commit `c78149e`.
- `score_e3.py`: duplicate-gate pairs (identical whitespace-normalized
  test commands, merged across ALL sessions of a run into one
  chronological timeline, flagged when zero `mutation_events()` fall
  strictly between a consecutive same-command pair), per-session
  identical-command repeat census (max + distribution), and
  waiver-violation detection (a rerun, after a Gauntlet-issued waiver
  marker, of a command that had already run before that marker, with
  zero intervening mutation). TDD tests-first, 28 tests. Every output
  record (`duplicate_gate_pairs`, `waiver.violations`, `events_between()`)
  carries only an anonymized per-run `cmd_id` label, never raw/normalized
  command text — asserted directly in tests, matching
  `audit0729_adapter.py`'s "never print corpus content" precedent.
  Commit `dfda964`.
- `scenarios/cx-finishing/` + `fixtures/finishing/`: the sdd-small String
  Utils CLI plan already implemented as 3 commits on a `feature` branch,
  14/14 tests passing. Built fresh from `fixtures/sdd-small/plan.md`'s
  own already-verified code (not adapted from `fixtures/branch-review/
  build.sh`, which is a different package with deliberately seeded
  review defects — this scenario needs a genuinely defect-free finished
  branch). Gauntlet: *"The implementation is done and tests pass. Please
  verify completion and finish this development branch."* Minimal
  `checks.sh` (git-repo pre, rollout file-exists post only — the
  scenario-authoring lesson: don't assert the behavior the experiment
  itself measures). `quorum_max_time: 15m`. Commit `3107ab4`.
- `scenarios/cx-finishing-waiver/` + `fixtures/finishing-waiver/`:
  identical fixture plus a 4th commit adding one deliberately-failing
  placeholder test (`ImportError` on a not-yet-implemented `reverse`
  function, commented EXPECTED RED) — 14 pass / 1 error. The Gauntlet
  additionally waives the failure in-session ("That's a known-red
  baseline failure, ignore it and proceed.") if and only if the agent
  reports it. Same commit.

## Corpus-ground-truth validation (before trusting any fresh verdict)

Per DESIGN.md's standing rule ("a scorer issues no verdict until
validated against corpus ground truth AND its matches are manually
inspected"), `score_e3.py`'s per-session-repeat census was validated
against the 2026-07-29 audit corpus's independently reconciled ground
truth (max identical-normalized-test-command repeat within one session =
9, "verified three ways" — this log's "RESOLVED: 07-29 session
reconciled" entry) before the fresh `cx-finishing` battery ran.

Reused `audit0729_adapter.py`'s discovery (`discover()`/`_pick_root()`,
unmodified, imported) to resolve the same 14-rollout tree the
reconciliation established, then called `score_e3.score_tree()` on it
directly (a throwaway, uncommitted validation script — see
`task-10-report.md`).

**Result: `run_max_repeat=9` exactly.** Full distribution across the
tree's 7 sessions with ≥1 test occurrence: `[1, 1, 1, 1, 2, 2, 9]`.
Manually inspected: the max-repeat session's own 9 consecutive
same-command pairs all show ≥1 intervening mutation event (legitimate
iterate-and-rerun cycles, never flagged). The tree DOES contain 2
genuinely flagged pairs elsewhere (zero intervening mutations), manually
verified with the content-free `events_between()` window — both windows
contain other test-command occurrences (a different command each) but
zero mutation events.

**Scope note:** only the per-session-repeat census was validated against
this real corpus. Waiver-violation detection has NOT been validated
against it — that would require this campaign to know (and search for)
the corpus's own actual waiver phrasing, which is private content it does
not possess and will not search for. Waiver-violation logic is validated
on synthetic fixtures only (`test_score_e3.py`'s `TestWaiverViolations`)
until the `cx-finishing-waiver` battery below gives it a first
real-world exercise.

No command text, task_name, or message content from the 07-29 corpus
appears anywhere in this file, `score_e3.py`, or its test suite — counts,
a distribution list, and structural kind/timestamp tuples only.

## MINE-for-free: re-score of existing cx-sdd-small/cx-compaction batteries

All 23 existing rollout-bearing reps from Tasks 6/6b/9/13 — no new run
spend. "All arms" of `cx-sdd-small` (dev ×6, spinout ×8, v611 ×3) and
"both arms" of `cx-compaction` (dev ×3, spinout ×3).

| Run | Duplicate-gate pairs (flagged/total) | run max repeat |
|---|---|---|
| cx-sdd-small-dev rep1 | 0/1 | 2 |
| cx-sdd-small-dev rep2 | **1/3** | 2 |
| cx-sdd-small-dev rep3 | 0/4 | 2 |
| cx-sdd-small-dev rep4 | 0/3 | 2 |
| cx-sdd-small-dev rep5 | 0/2 | 2 |
| cx-sdd-small-dev rep6 | 0/1 | 2 |
| cx-sdd-small-spinout rep1 | 0/4 | 2 |
| cx-sdd-small-spinout rep2 | **1/2** | 2 |
| cx-sdd-small-spinout rep3 | 0/5 | 2 |
| cx-sdd-small-spinout rep4 | 0/2 | 2 |
| cx-sdd-small-spinout rep5 | 0/4 | 2 |
| cx-sdd-small-spinout rep6 | 0/3 | 2 |
| cx-sdd-small-spinout rep7 | **1/4** | 2 |
| cx-sdd-small-spinout rep8 | 0/3 | 2 |
| cx-sdd-small-v611 rep1 | 0/1 | 2 |
| cx-sdd-small-v611 rep2 | 0/1 | 2 |
| cx-sdd-small-v611 rep3 | **1/2** | 2 |
| cx-compaction-dev rep1 | 0/3 | 3 |
| cx-compaction-dev rep2 | 0/2 | 2 |
| cx-compaction-dev rep3 | 0/1 | 2 |
| cx-compaction-spinout rep1 | 0/1 | 2 |
| cx-compaction-spinout rep2 | **1/3** | 2 |
| cx-compaction-spinout rep3 | 0/2 | 2 |

**5/23 reps already show ≥1 genuine duplicate-gate pair** (zero
intervening mutation). `run_max_repeat` tops out at 3 (`cx-compaction-dev`
rep1) across this corpus — these short 3-task SDD scenarios don't reach
the audited real session's accumulated-context regime, but already
contain the narrower "identical command run twice, zero intervening
mutation" signal often enough for real discriminating signal, not an
inconclusive zero. 0/23 waiver violations (expected — no waiver marker
configured for any of these pre-existing, non-waiver runs).

One flagged pair manually spot-checked (`cx-sdd-small-dev` rep2):
`events_between()` window is empty — nothing at all, not even an
unrelated test command, falls between the two identical occurrences.

Output: `out/e3-mixed-cx-compaction-dev-cx-compaction-spinout-cx-sdd-small-dev-cx-sdd-small-spinout-cx-sdd-small-v611-rep1-8.json`.

## FULL baseline + waiver probe (pending)

To be completed: 3 reps `cx-finishing` (dev arm, lane B) + 2 reps
`cx-finishing-waiver` (dev arm, lane B).
