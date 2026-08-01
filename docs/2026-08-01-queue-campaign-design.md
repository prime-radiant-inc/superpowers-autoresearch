# Queue-Execution Campaign — Design (2026-08-01)

Continuation of the cost-pathologies campaign
(`docs/2026-07-31-cost-pathologies-campaign-design.md`, report
`reports/2026-08-cost-pathologies-campaign.md`). Jesse's directive,
2026-08-01: run the full 23-item queue from the report's §6, assuming PRs
#2059–#2064 have landed; new budget envelope $1000. This document maps the
queue onto executable tasks; it does not restate the queue items — §6 is
their source of truth, cited by number throughout.

## Test base: the "PRs landed" world

The six fix-cycle PRs are still open, so the post-merge dev they'd produce
is simulated locally:

- **`sim/dev-postmerge`** (local branch in the superpowers repo, NEVER
  pushed) = `origin/dev` @ bb2a34b + no-ff merges of the four PR heads:
  `fix/t1-sdd-no-worker-reviewers` @ 7c560e0 (T1),
  `fix/t5-codex-spawn-routing` @ e9686d5 (T3+T2+T5 stack),
  `fix/t4-brainstorming-three-paths` @ 4dc71b1 (T4),
  `fix/docs-codex-efficiency-campaign` @ 3ff8d15 (docs).
- Verified delta vs the previous arm base 329b8f1 (the
  `codex-efficiency-fixes` tip): **4 deleted lines in
  `skills/subagent-driven-development/SKILL.md`** — exactly the 433184c
  text Jesse dropped from the T2 PR. Nothing else differs. The PR-set and
  the fix branch are otherwise content-identical.
- All `cp/*` arms rebase from 329b8f1 onto `sim/dev-postmerge`. New SHAs
  recorded in a dated section of
  `campaigns/cost-pathologies/arm-manifest.md`. **`cp/x9a`'s rebased text
  is ungraded until the Task 12 composed battery runs** (it rewrites SDD
  SKILL.md regions the T1/T2 PR text also touches); the standing rule —no
  treatment ships text a battery didn't run — applies to the rebased text,
  not just the original.

If dev moves or a PR merges mid-campaign, rebuild `sim/dev-postmerge`
against the real state, re-verify the delta, and log the change.

## Structure

Same campaign directory (`campaigns/cost-pathologies/`) — every queue item
extends an existing experiment's scorers, scenarios, or arms; a parallel
tree would duplicate all of them. New plan, new log:

- Plan: `docs/plans/2026-08-01-queue-campaign.md` (SDD-executed)
- Log: `logs/2026-08-01-queue-campaign.md` (append-only, standing
  discipline header carried over from the cost-pathologies log)
- Ledger: `.superpowers/sdd/2026-08-01-queue-campaign/progress.md`

## Workstreams (queue item → task mapping)

**W1 — Instruments first (items 9–14).** Scorer fixes gate honest scoring
of every later battery, so they run before any battery. Three tasks:
`score_x1_chains` (11: `NONE_VALUE_RE` under-matching; 12: the invisible
re-tasked-reviewer chain pattern), `score_x5_leases` (9: prose-aware honor
detection alongside the strict grammar; 10: distinct-event counting +
exec-call scanning), and a hygiene sweep (14: dot-directory `glob('**')`
audit across all scorers; 13: a blocking-precision BAIT signature separate
from the recall signature). All corpus-validated with regression tests
against this campaign's actual rep artifacts where they exist.

**W2 — Scenario hardening (items 15, 20, 21, 22, 23).** One task:
pin every paraphrase-guided Gauntlet reply in `cp-x7x9-conflicts`,
`cp-x2-advisory`, and `cp-x8-approvals` to exact verbatim strings (15 —
mandatory before any re-run); add a did-main-advance check to
`cp-x1-buggy-sdd` (20); rule on 60m-ceiling sizing (21 — default: accept
~25% non-merge as the honest baseline and grade it, rather than growing
wall-clock cost); investigate persisting `provenance.superpowers_rev`
per-rep (22 — fix if it's a runner-side one-liner, otherwise document);
capture the SDD ledger before the session's finishing step deletes the
workspace (23).

**W3 — Fixtures owed (items 1–6).** Four authoring tasks: the X1
edit-existing-code fixture (1) and the independent wave-cap fixture (2);
the X6 plan-framed fixture plus the skipped MINE-tier dispatch-floor
distribution (3); the X8 no-disclosure-confound fixture (4) and X2-B
isolation fixture (5); X5-at-scale is a battery (W4) once W1's scorer
fixes land — its fixture question (6) is resolved inside that task by
sizing the plan up. Every new fixture gets MICRO validation (seeded-truth
check, deflection pinned from birth) before FULL spend.

**W4 — Batteries (items 6, 7, 8 + runs for W3's fixtures).** X5 savings at
scale (6; n≥8/arm across A/B/control, distinct-event scorer); X3-B
controller-half as a real mounted arm (7); X7+X9 composed (8; doubles as
the re-validation battery for rebased `cp/x9a` and `cp/x7a/b` text); then
one battery per W3 fixture. Pre-registration in the log before every
battery, per standing discipline. Every battery reports against its §6
item by number.

**W5 — Design-and-decide (items 16, 17, 19).** X7-B parser scope: add
regression tests encoding the three ratified limits, implement the cheap
one (multi-name backtick span decomposition) if tests show it's local (16).
X5-A honoring channel: amend the design to echo honor/invalidate lines
through an unencrypted channel (17). Scope auditability (19):
machine-readable declared scope in dispatch briefs — design here, battery
deferred to the plan-decomposition campaign, where it is a foundation
piece (the manifest concept subsumes it).

**W6 — Parked with evidence (item 18).** The three silent harness bridges
need a mined corpus from gemini/pi/antigravity before any text is
proposed. No such corpus exists on any reachable host. Parked explicitly
in the closeout report; not silently dropped.

## What "done" means

Each §6 item ends the campaign in exactly one state: **fixed** (with the
commit), **answered** (with a battery verdict), **designed** (W5's
deliverables), or **parked with the evidence gap named** (item 18, and any
battery the budget can't reach — flagged to Jesse before, not after).
The closeout report replaces §6 with a new queue.

## Budget

$1000 envelope. Planned split: ~$30 MICRO validation, ~$400–500 FULL
batteries (X5-scale ~24 reps; composed ~12; X3-B ~9; X1-edit ~16;
wave-cap ~9; X6 ~12; X8 ~9; X2-B ~9 — ~100 reps at the campaign's
observed ~$4.50/rep), remainder held for the plan-decomposition campaign
that follows. Instruments/fixtures/design tasks are near-zero API cost.
If battery evidence argues for more reps anywhere, ask Jesse before
exceeding the envelope.

## Standing rules (unchanged)

Raw sessions and `_tmp` corpora never committed; hostname aliases in all
published text; needle sweeps over staged diffs AND commit messages; arms
never pushed/merged/PR'd; no treatment text ships ungraded; deflections
pinned verbatim; subagents poll in foreground; append-only log with
corrections as new dated entries; pre-registration before batteries;
discrimination rule (a scorer that can't distinguish arms on the seeded
truth stops the battery).
