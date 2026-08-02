# Campaign: Cost pathologies

**Design doc (source of truth for scope):**
`docs/2026-07-31-cost-pathologies-campaign-design.md` — read the base doc
AND Amendments 1–2 at the bottom (Amendment 1 adds X7/X8 and the X1 wave-arm
addendum E/F/G; Amendment 2 reframes X7/X8 non-blocking and adds X9). Every
arm, criterion, and guard is reproduced verbatim in the hypothesis log's
`## Pre-registered criteria` section — the log is the grading contract;
this file is pointers only.

**Hypothesis log (append-only, pre-registration + verdicts):**
`logs/2026-07-31-cost-pathologies.md`

**Implementation plan / SDD ledger:**
`docs/plans/2026-07-31-cost-pathologies-evals.md`,
`.superpowers/sdd/2026-07-31-cost-pathologies-evals/`

**Arm manifest** (arm → branch → SHA → files touched; built in Task 3):
`campaigns/cost-pathologies/arm-manifest.md`

## Arm-branch convention

Treatment-arm skill text lives on LOCAL branches in
`/Users/jesse/git/superpowers/superpowers`, named `cp/<exp><arm>` (e.g.
`cp/x1a`, `cp/x2c`), each cut from `codex-efficiency-fixes`' tip (the
current control text). These are experiment apparatus only — never pushed,
never merged, never PR'd. Quorum batteries run them as arms against the
established container lanes; the arm manifest is the citable source of
branch SHAs for every battery.

## Corpora

`_tmp/cost-pathologies-2026-07-31/` — three miner reports (local,
remote-host-a, remote-host-b), the M0 mechanical-check output, and
Drew's donated-session analysis. Local-only, NEVER committed; only
aggregates and manually-reconciled exemplars cross into the log or scorer
validation tables.

## Runner conventions

Quorum batteries reuse `campaigns/codex-efficiency/run-quorum.sh` and its
env conventions (`EVALS_ROOT` for lane selection, `JOBS` for parallel reps,
`CODING_AGENT`/`CREDENTIAL` for cross-harness runs) — see that script's
header comment for the full contract, including its known REPS-abort
limitation on a mid-battery fail/indeterminate verdict. Scorers import
`campaigns/codex-efficiency/rollout_parser.py` rather than forking it.

**This campaign's own scenarios** (`cp-x1-buggy-sdd`, `cp-x1-edit-existing`,
`cp-x2-advisory`, `cp-x7x9-conflicts` + its `-clean`/`-prose` siblings,
`cp-x8-approvals`, `cp-x5-leases`, `cp-x6-smalledits`) run through
`campaigns/cost-pathologies/run-quorum.sh` instead — modeled on the
codex-efficiency script but simpler (each scenario carries its own
`fixtures/` subdirectory, so a battery syncs the whole scenario directory
into the evals lane rather than merging a separate top-level fixtures
tree). **Known gap (Task 6, owed to Task 8+):** it only resolves ARM
`control` (pointing at a caller-created `/tmp/cp-arm-control` worktree at
`codex-efficiency-fixes` @ 329b8f1); it does not yet know how to
materialize one of the 17 `cp/<arm>` branches from
`campaigns/cost-pathologies/arm-manifest.md` into its own worktree the way
codex-efficiency's script resolves its four fixed arm names. See the
script's own header comment for the fuller constraint (each arm needs its
own directory; `JOBS>1` would race on a shared one).

## Budget

~$580 ceiling (of the original $1000 envelope, net of the codex-efficiency
fix cycle's spend); STOP-and-report checkpoint at $400 cumulative. Ledger
tracked in the hypothesis log.
