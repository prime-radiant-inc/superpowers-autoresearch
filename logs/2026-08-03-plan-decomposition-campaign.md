# Plan-Decomposition Campaign Log (2026-08-03)

Append-only; corrections are dated entries. Standing discipline carried
forward from the backlog campaign log header, plus the two rules minted
there: (1) every battery pre-registration states HOW the arm text is
reachable from the scenario's execution path; (2) base-rate replication
is pre-registered whenever a pathology's existence is the treatment's
justification. Design: docs/2026-08-03-plan-decomposition-campaign-design.md.
Plan: docs/plans/2026-08-03-plan-decomposition-campaign.md. Budget ≈$836
at open.

## 2026-08-03 — Campaign open

Empirical cornerstones inherited (see design §"Empirical foundation"):
authority gap, attention routing, structural-dedupe constraint, x2b
lens effect size, cost anchors, fresh-session localization. Arms will
use pd/* local branches off sim/dev-postmerge @ 1fed99d.

## 2026-08-03 — Task 4 pre-registration: P1/P2 battery (pd-pipeline + pd-overflow)

**Arms:** control @ 1fed99d; pd-p1 @ ee0c6b0; pd-p2 @ 292da9c
(includes x7a ea84cf9 — p2's effect is measured RELATIVE to control,
so any x7a main-effect is bundled; the composed cell + prior x7a
batteries bound that confound and the p1p2-vs-p1 contrast isolates the
p2 mechanism); pd-p1p2 @ 1a1a8fd (composition defect found and fixed
at drafting: p1's dont-hold-task-files rule vs p2's value-table need —
the preflight is defined as the controller's one pass).

**Cells:** pd-pipeline {control, p1, p2, p1p2} ×3 (12 reps);
pd-overflow {control, p1} ×2 (4 reps). Lane A: pipeline-control ×3,
pipeline-p2 ×3, overflow-control ×2. Lane B: pipeline-p1 ×3,
pipeline-p1p2 ×3, overflow-p1 ×2. Est. ~$8-10/pipeline rep,
~$12-18/overflow rep ≈ $140-170.

**Reachability:** all arm text lives in writing-plans + SDD SKILL.md;
the scenario's opening message explicitly invokes BOTH skills
(authoring then execution) — reachable by construction on every arm;
p1's directory instruction binds at authoring, p2's at SDD setup.

**Criteria:** (1) PRIMARY (P1): plan shape — directory adoption
(score_pd_planshape: form, file count, task sizes) + return-window
failures (baseline expectation: possibly zero even in control on
pd-pipeline; pd-overflow is the discriminating scenario, and
OVERFLOW-OCCURRENCE IS A MEASURED OBSERVABLE — if overflow-control
shows 0 return-window failures, the P1 overflow claim is
INCONCLUSIVE-BY-INSUFFICIENT-SIZE and the probe expands before any
conclusion (T3 size model honestly reached only ~10-20k tokens).
(2) PRIMARY (P2): coherence — cross-module divergence count in final
trees (score_pd_coherence tree mode) + the cross-cutting constant
family presence lines; plan-text divergence caught-and-amended at
preflight (ledger/plan-diff evidence). Baseline: pd-pipeline's
constant family seeds natural divergence pressure via the spec.
(3) Guards: completion parity (post-checks), dispatch counts within
control range (p1 must not inflate dispatches), review rounds, cost.
(4) Micro-edit disposition + YAGNI markers recorded as observables for
P4's later design (not criteria here).

**Scorer caveat (registered):** observables_from_verdict +
return_window_failures meet their first real reps in this battery —
scorer-vs-reality discrepancies are instrument findings first, data
second (T2 ⚠️ carried).

## 2026-08-03 — Task 4 VERDICT: P1 delivers its mechanism and INTRODUCES cross-cutting requirement loss; P2 inert on self-authored plans; overflow unconfirmed

17 reps (16 + 1 backfill after an infra death, quarantined; tolerant
chains; only final post-chain verdicts scored — a mid-run verdict
read taught the rule). Battery ≈ $118.

**Per pre-registered criteria:**

1. **P1 plan-shape: the arm DELIVERS.** 6/6 directory-arm pipeline
   reps authored genuine plan directories (plan.md + task files,
   sizes 5-9 tasks); 6/6 monolithic-arm reps stayed monolithic.
   Task-count granularity: control 4/7/6, p2 6/8/8, p1 8/5/6, p1p2
   9/8/8 — directional toward the spec's 6-10 grain under treatment
   arms but overlapping; no clean claim. **Return-window/overflow:
   INCONCLUSIVE-BY-INSUFFICIENT-SIZE** as pre-committed: both
   monolithic overflow controls completed their large plans
   (36/36 checks; repeat-write candidates 1/1 unconfirmed as
   truncations) — the T3 size model's honest shortfall was borne
   out; the probe expands before any P1-overflow claim.
2. **P2 coherence: INCONCLUSIVE-BY-CEILING on self-authored plans.**
   All monolithic cells (control + p2) coherent — a session that
   authors its own plan rarely plants cross-task contradictions for
   the gate to catch. FIXTURE-ARM MISMATCH recorded: P2's
   discriminating scenario class is a PRE-WRITTEN incoherent plan
   (exactly cp-x10-consistency's shape — reusable as-is for a P2
   follow-up battery). The p2 controller rollouts do engage the
   constant family at preflight (value-table text active), with
   nothing to amend.
3. **NEW FINDING (exploratory-flagged, the battery's headline): P1
   INDUCES cross-cutting requirement loss.** The spec's shared
   constant family landed incompletely in 2/6 directory-arm pipeline
   reps (p1-rep3: absent from ALL three modules + failing suite,
   final=fail; p1p2-rep1: present in 1/3 modules, masked by green
   self-authored tests) vs 0/6 monolithic reps. Mechanism: per-task
   files are written one response at a time; a requirement spanning
   several tasks must be re-carried into each file, and without the
   whole plan in one view it lands in some and not others — the
   return-window fix recreates, at authoring, the same
   cross-cutting-attention failure the campaign found at review
   (wave-cap) and adjudication (authority gap). The composed p2 gate
   did NOT reliably rescue it (its scan reads what the files say;
   an absent requirement produces no divergent value-pair to flag).
4. **Guards:** completion — monolithic 6/6 pass; directory 5/6
   (p1-rep3 fail, the requirement-loss rep). Dispatch counts within
   range (arm means 13.7-17.3 vs control 15.3; tracks task counts).
   Costs: control mean $6.13, p1 $6.24, p2 $6.69, p1p2 $7.48 — no
   treatment cost win; composed +22%.

**Dispositions:** pd/p1 NOT ship-eligible as drafted — its central
risk (requirement loss) now has direct evidence; the fix shape is
known (the cross-cutting family must live in plan.md's Global
Constraints/index as the single source, with task files REFERENCING
not restating it — plus a completeness row in the p2 table: every
spec requirement maps to a task file). pd/p2 unproven here, correct
test queued on the existing incoherent-plan fixture. Overflow probe
expansion queued. The requirement-loss finding graduates to a
pre-registered confirmatory battery before any revised-P1 ships.
Grading by controller, disclosed; scorer stack validated in
production this battery.

## 2026-08-03 — CORRECTION: T4's requirement-loss headline was an instrument artifact (6th strict-instrument case)

Jesse's iterate-on-this directive prompted a mechanism chase that
overturned the verdict's headline in three steps, each documented:
(1) the "lost" requirement was present in BOTH losing reps' plan
text (so not an authoring-attention failure as published); (2) the
task files contained complete code with the constant (so not an
execution drop); (3) the BUILT MODULES contain it — p1p2-rep1's
orders/pricing.py line 1 is `MAX_LINE_ITEMS: int = 12`. checks.sh's
extraction regex (`^MAX_LINE_ITEMS[[:space:]]*=`) cannot see
annotated assignments or import-references. Tolerant re-derivation
over ALL 12 pipeline reps: **12/12 carry the constant at value 12 in
all three modules — every arm, ceiling everywhere. P1 does NOT
induce requirement loss.** The false negatives clustered in
directory arms only because their implementers used type
annotations — style variance, not substance.

Standing: the published T4 headline (finding 3) is WITHDRAWN. What
survives of T4: arm delivery (6/6 directories), task-count direction
(overlapping), P2 ceiling on self-authored plans (unchanged — but
now for coherence AND presence), overflow inconclusive (unchanged),
p1-rep3's completion failure (1/6 guard hit — pytest collection
error, requires separate classification; its constants are present),
cost parity. P1's disposition improves from
harmful-as-drafted to DELIVERS-MECHANISM / NO-DEMONSTRATED-HARM /
NO-DEMONSTRATED-BENEFIT-YET. Queued fixes: checks.sh tolerant
extraction (annotated + import forms) in both pd scenarios +
scorer alignment + validator exercising checks.sh itself (the gap
that let two emit-format defects through in one campaign).

**The unmeasured objective:** P1's core payoff hypothesis —
controller context economy (plan.md-only vs whole-monolith in
controller context; the 2.7M-token orchestrator anchor) — was never
scored. Next analysis (free, existing rollouts): controller input
tokens per arm.

## 2026-08-03 — Controller-economy analysis + ITERATION plan (Jesse's directive)

Controller cumulative input (median, main rollout token_count):
control 4.23M / p2 5.23M / p1 5.24M / p1p2 6.23M; peak context flat
150-160k. **P1's context-economy hypothesis is negative at this
scale** — dispatch count and turns dominate; plan-artifact shape is
not the lever here. Combined with the withdrawn harm finding: P1
delivers mechanism, no benefit, no harm, at pd-pipeline scale.

**Iteration (new competing arms + re-aimed batteries):**
- **P2-on-foreign-plan battery (pre-registered below)** — the gate's
  discriminating scenario existed all along: cp-x10-consistency.
- **p1b arm (new)**: single-file plan authored INCREMENTALLY (header +
  constraints + index first; one Edit-append per task; re-read before
  each append). Rationale: the return-window constraint binds per
  WRITE, not per FILE — p1b keeps the monolith's whole-plan view
  (which the withdrawn finding wrongly indicted but the analysis
  showed is where coherence lives) while removing the single-write
  ceiling. To battery on the EXPANDED overflow probe only (where
  control can actually fail).
- **Overflow probe expansion** (T3's registered path): grow the spec
  until monolithic single-write authoring demonstrably fails in
  control; then {control, p1, p1b} ×3.
- Instrument fixes FIRST (required for further batteries on these
  scenarios): checks.sh tolerant constant extraction (annotated +
  import forms) in pd-pipeline + pd-overflow; validators exercise
  checks.sh itself (two emit-format defects escaped it this
  campaign).

## 2026-08-03 — Pre-registration: P2-on-cp-x10 battery (the coherence gate's real test)

**Scenario:** cp-x10-consistency (unchanged; 5 PLAN-INDUCED
cross-module defects, each seeded by two task briefs pinning
incompatible values — precisely P2's shared-name value-row class).
**Arms:** pd-p2 @ 292da9c ×3 (lane A). **Baseline:** the backlog
campaign's control ×3 on this scenario (0/5 final-review detection;
all seeded defects present in final trees; plan authority dismissed
scan candidates). No new controls (scenario + harness unchanged since;
the X10 battery ran 2026-08-03).
**Reachability:** p2's text binds at SDD setup preflight — the
scenario's opening message invokes SDD on the pre-written plan;
reachable by construction (and this time the plan is foreign, so the
gate has real conflicts to catch).
**Criteria:** (1) PRIMARY: seeded-defect death rate — defects
neutralized by preflight AMENDMENT (plan diff/ledger evidence) and
absent/consistent in the final tree, per the seeded-truth ledger's
recipes (tolerant forms), vs baseline all-present. PASS = median ≥3/5
neutralized. (2) Guards: completion parity (task post-checks), no
hard stop (rulings + amendments are the non-catastrophic path — a rep
that STOPS to ask about the conflicts fails the never-stall
expectation), cost. (3) The amendment mechanism specifically: value
rows in the ledger table + plan text edited before Task 1 (hand-read
per rep, disclosed). Est. 3 reps × ~$8 ≈ $25.
