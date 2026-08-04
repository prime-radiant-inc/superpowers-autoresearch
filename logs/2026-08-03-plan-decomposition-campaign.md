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

## 2026-08-03 — Pre-registration: certified-overflow battery (pd-overflow-xl)

**Scenario:** pd-overflow-xl (reviewed; size model independently
recomputed: ≈48.6k-token faithful monolithic plan vs ~32k single-write
budget — overflow certified by arithmetic with 1.5× margin; 32 tasks,
3 subsystems).
**Arms:** control @ 1fed99d ×3; pd-p1 @ ee0c6b0 (plan-as-directory)
×3; pd-p1b @ 831fbfd (incremental single-file) ×3. Lane B chain:
control ×3 then p1b ×3; p1 ×3 appended to lane A after the P2-x10
chain exits. Est. 9 reps × ~$12-18 ≈ $120.
**Reachability:** all arm text in writing-plans, invoked by the
scenario's authoring step — reachable by construction; p1b's
mechanism binds exactly at the write that overflow breaks.
**Criteria:** (1) PRIMARY — authoring survival: control's monolithic
single-write plan should now FAIL or truncate (return_window_failures
confirmed events + plan completeness vs the 32-task spec). If control
completes cleanly 3/3 ANYWAY, the size model is refuted empirically —
INCONCLUSIVE-BY-MODEL-FAILURE, recorded as such (this battery is
falsifiable in both directions). (2) Plan completeness per arm: task
count vs spec's 32 sections; index↔section reconciliation (p1b) and
directory file-count (p1). (3) Execution: completion post-checks,
coherence family (6 modules, tolerant extraction), micro-edit
disposition. (4) Costs + controller economy (same rollout analysis as
T4). PASS for an arm = complete plan authored + executed with
completion ≥ control and no coherence regression.

## 2026-08-03 — P2-on-cp-x10 VERDICT: FAIL — the authority gap survives the preflight value-table; it is a GROUND-TRUTH gap

3/3 reps pass 14/14 post-checks (~$6.9 each; battery $20.76). Seeded
defects neutralized: rep1 1/5 (seed 4 — the runtime-breakage class,
the ONLY class any instrument in this program has ever caught),
reps 2-3 0/5. Pre-registered bar (median ≥3/5): **FAIL.**

Behavioral layer (controller rollouts, hand-read): the p2 mechanism
EXECUTED — the controller ran the "required cross-task consistency
scan before any implementation dispatch," enumerated the exact seeded
divergences by name (MIN_PRIORITY, timeouts, status scope), and ruled
them "deliberate module-local differences... internally explained. No
plan amendment is needed."

**Refinement of the authority gap:** it is not an attention gap
(X10's scanner closed that), and not a table gap (P2's value rows
closed that). It is a GROUND-TRUTH gap: when the plan is the only
authority in scope, plan-internal justification ("each task explains
its value") is unfalsifiable at every layer — final review, scan
adjudication, and now preflight-with-amendment-power all reach the
same "intentional per-module policy" conclusion. P2's own ruling
clause ("the spec is the binding authority, the plan is its
argument") had nothing to bind to: cp-x10's scenario ships a plan
with NO independent spec above it.

**Iteration (P2'):** anchor the gate to an EXTERNAL ground truth —
when a spec exists, the preflight's shared-name rows compare each
task's pinned value against THE SPEC's value, and divergence from
spec (not from sibling tasks) is the amendment trigger. Fixture
follow-up: cp-x10-spec variant = cp-x10-consistency + a SPEC.md
stating the true shared values (small edit, high discriminating
power: same plan, now falsifiable). Real-world reading: a plan
executed without its spec is unauditable for coherence — an argument
for SDD carrying spec access into preflight, and for the
plan-as-directory manifest bundling the spec. Seed-4's uniqueness
(runtime breakage outranks text) also suggests executable
contracts/cross-module tests as the coherence mechanism of last
resort.

## 2026-08-03 — Pre-registration: P2' battery (cp-x10-spec, three arms)

**Scenario:** cp-x10-spec (reviewed; same seeded plan as
cp-x10-consistency plus the product spec it derives from; 5/5
resolutions spec-derivable, hand-verified; new spec-resolution-N
emit lines).
**Arms ×3 each:** control @ 1fed99d (does spec availability alone fix
coherence with no gate?); pd-p2 @ 292da9c (does p2's existing
"spec is binding" clause activate once a spec exists?); pd-p2s @
1937691 (the spec-anchored rows + provisional-ruling clause). The
triple isolates ground-truth availability from gate wording.
**Baseline:** P2-on-cp-x10 (specless): 0-1/5 neutralized, "internally
explained" ruling.
**Reachability:** arms in SDD SKILL.md, bound at preflight; the spec
is named in the opening message; the plan/spec-disagreement deflection
is pinned verbatim.
**Criteria:** (1) PRIMARY: spec-resolution score (median of the 5
spec-resolution-N lines = yes) per arm; PASS for an arm = median ≥3/5
with control's median strictly lower (discrimination guard: if
control ≥3/5, spec availability alone suffices and gate text adds
nothing — a REAL and shippable answer, recorded as such, not a
failure). (2) Preflight behavior (hand-read): value table built,
amendments committed pre-Task-1, "internally explained"-class
rationalization present/absent. (3) Guards: completion post-checks,
no human-stall (pinned deflections consumed at most), cost. Est. 9
reps × ~$7 ≈ $65. Queue: launches on first freed lane behind the XL
battery.
