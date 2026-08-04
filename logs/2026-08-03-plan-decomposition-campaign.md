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

## 2026-08-04 — Certified-overflow battery VERDICT: size model empirically refuted by GRANULARITY ADAPTATION; the plan-artifact-shape axis closes negative

9/9 reps final=pass with full post-checks (56-63), coherence 9/9,
and — decisive — FULL SCOPE in every arm: 34/34 service modules
implemented per rep (venv-excluded count), verified directly in the
trees. Battery ≈ $108.

**The refutation mechanism (the finding):** nobody overflowed because
NOBODY WROTE THE 32-TASK PLAN. Control authored 6/8/7-task monolithic
plans; p1 directories held 7/8/7 task files; p1b's incremental method
produced 12/7/8. Authors COMPRESS plan granularity to fit the writing
budget — bundling ~4-5 spec modules per task — while execution
preserves full scope. The size model's premise (faithful
maximal-granularity authoring per the skill's bite-sized-step
mandate) is what sessions abandon under size pressure, and they
abandon it SAFELY. Return-window overflow does not arise from spec
size with this model + skill text; it is self-preventing at
authoring. Jesse's observed real-world overflow failures must arise
elsewhere (different model/harness bundling behavior, mandated
granularity, or revision/append contexts) — recorded as an open
localization question, NOT reproducible by scale alone.

**Costs:** control $11.38 mean, p1 $10.24, p1b $14.29 — p1b's
spine-re-read ceremony costs ~26% over control for zero measured
benefit.

**Axis disposition — plan-artifact shape CLOSED NEGATIVE:** across
two scenarios, three arms, and every measured axis (overflow
robustness, coherence, scope completeness, completion, dispatch
counts, controller economy, cost), monolith vs directory vs
incremental authoring is a matter of indifference: the model
self-regulates granularity and cross-module coherence at authoring.
cp/pd-p1, cp/pd-p1b closed as ship candidates. Corollary
(feeds the W-hypothesis ledger): bundling-at-authoring is the
DEFAULT behavior at scale — right-sizing text (P4) should expect
ceiling effects in fresh sessions for the same reason.

**Still live in this campaign:** P2' ground-truth battery (running),
R1 review-triage micro-instruments, D1 structural dedupe, K1
knowledge-forwarding, T9 tooling-ask, synthesis. Grading by
controller, disclosed.

## 2026-08-04 — P2' battery VERDICT: ground truth in the room closes the gap; gate text buys autonomy and the last point

9/9 reps final=pass 19/19 post-checks; battery $69.76.
Spec-resolution scores: control 4/5, 5/5, 4/5 (median 4/5 — both
misses are partial resolutions of seed 5); pd-p2 5/5 ×3; pd-p2s
5/5 ×3.

Per the pre-registered discrimination clause (control ≥3/5 → "spec
availability alone suffices" is the recorded, shippable answer):
**the authority gap is closed by PUTTING THE SPEC IN THE ROOM.** The
specless baseline on the same plan was 0-1/5 with "internally
explained" rulings at every layer; the identical plan plus its spec
yields 4-5/5 even with NO gate text. The gap was never attention,
tables, or wording — it was ground-truth availability.

Behavioral differential (hand-read): the ungated control DETECTED all
five conflicts immediately ("The implementation plan directly
conflicts with the product specification in five places," enumerated
exactly) but then used the base skill's batched-question path —
resolved only by the pinned "The spec is authoritative" reply. The
gate arms ruled and amended autonomously, zero asks. So in unattended
sessions the gate text's value is AUTONOMY (composing with the
never-stall thread / PR #2077) plus uniform 5/5; p2-vs-p2s wording
made no difference once the spec existed.

**Ship implications (for synthesis + Jesse's review):** (1)
writing-plans: the plan header carries a `**Spec:**` pointer to the
spec it was derived from; (2) SDD setup/preflight: locate and read
the plan's spec — coherence rows then anchor to it naturally (p2's
existing clause suffices; p2s's extra wording unnecessary); (3) the
composition with #2077 converts the residual ask into a ruling.
Smallest evidence-backed text change of the campaign, largest
measured effect (0-1/5 → 4-5/5). Grading by controller, disclosed.

## 2026-08-04 — R1 micro-battery pre-registration (review-triage policies)

**Instrument:** r1-review-micro.py (reviewed; one Important fixed —
7th strict-extraction case, caught pre-spend; three-state extraction
sectioned/unsectioned/absent with unsectioned counts surfaced).
**Cells:** {deviant, mixed} × {plain, lens-suppress, lens-downgrade,
cleanup-wave}, REPS=8/cell = 64 calls, MODEL=claude-opus-4-8
(instrument default, consistent with x2b/x1 micro precedent).
**Reachability:** policies injected verbatim into the review prompt —
by construction.
**Criteria:** (1) GUARD (decisive): in mixed cells, the seeded
Important CSV bug must be reported at BLOCKING severity — per policy
arm, bug-blocking rate ≥7/8 to remain shippable; a policy that
relegates or suppresses the real bug FAILS regardless of its
structure-noise handling. Unsectioned hits are hand-classified before
any verdict (never counted as missed). (2) PRIMARY: structure-only
finding handling per policy — expected: plain=blocking-noise
(rathole-feeding), suppress=absent (x2b's 10/10→0/10 precedent),
downgrade=present-at-Minor/deferred, cleanup=present-in-cleanup
section. A policy passes when it does what it says ≥6/8 AND holds the
guard. (3) Noise floor: deviant cells re-confirm x2b's suppression
baseline; conformant floor not re-run (x2b's 0/20 stands, same tree).
Est. 64 calls ≈ $8-12.

## 2026-08-04 — R1 micro-battery VERDICT: all four triage policies hold the guard; the rathole fix is free

64 calls, ~$8. Scoring per pre-registration: mechanical first, then
controller hand-rescore (the shipped struct columns used the
still-unfixed DEVIATION_RE — 8th undercount instance — and SECTION_RE
missed the "#### Important (Should Fix)" heading variant — 9th; all
four borderline guard cases hand-read; verdict basis is the
hand-verified layer, raw answers preserved).

**GUARD (the decisive metric): 8/8 in ALL FOUR arms.** Every
borderline case reports the seeded zero-amount CSV bug under an
explicit Important/Should-Fix section with correct analysis and fix.
No triage policy — including full suppression — masked a real
behavioral defect at this tier.

**Structure-noise handling (deviant cells, hand-rescored):** plain
raises it 8/8 (the rathole-feeding baseline, replicating x2b's
10/10); lens-suppress 3/8 raised / 5/8 explicitly reasoned away
(direction holds, weaker draw than x2b's 0/10); lens-downgrade 6/8
raised at deferred severity; cleanup-wave 7/8 raised in the cleanup
section. **Mixed cells: ALL arms raise the structure issue 8/8
alongside the bug** — the presence of a genuine defect flips the
review's posture; suppression only fully binds on otherwise-clean
reviews.

**Verdict:** the review-rathole fix is effectively free at the
judgment layer — policies that keep structure noise visible but
non-blocking (downgrade-to-deferred, cleanup-wave) achieve the
desired shape with zero measured guard cost, and even suppression
does not endanger real defects. Synthesis recommendation:
cleanup-wave/downgrade class text (formalizing SDD's existing
deferred-minor ledger into explicit triage classes) is the ship
candidate; suppression buys nothing further and destroys
information. Queued: r1/x2b grader fixes against the now-104-answer
real corpus (both regex classes). Grading by controller, disclosed.

## 2026-08-04 — Pre-registration: rationalization-interrogation pass + p2s-specless cell (Jesse's method)

Jesse's directive: bad agentic behavior is often fixed by
interrogating the session that did the wrong thing, extracting its
rationalization, and closing it in the skill's rationalization table.
Two applications:

**A. X11 re-runner interrogation (API, ~$2):** for each of the 4 x11
reps, extract the controller's transcript context surrounding its
redundant pytest invocations (implementer report with test evidence
already in context), replay it to the same model class with an
elicitation prompt ("what reasoning led to running the suite here?"),
and classify the elicited rationalizations. Output: a candidate
rationalization-table row set for the verification-dedupe seam.
Post-hoc-confabulation caveat disclosed: elicited reasons are
hypotheses to encode as table rows and re-test, not ground truth.

**B. p2s-on-specless cell (3 reps, ~$21):** pd-p2s @ 1937691 on
cp-x10-consistency (NO spec). Tests whether the anti-rationalization
line alone ("'each module explains its choice' is how incoherence
defends itself" + provisional-ruling clause) moves the 0-1/5 specless
baseline. Criteria: seeded-defect neutralization vs the pd-p2
specless baseline (0-1/5); ≥3/5 = rationalization-repair works
standalone; 0-1/5 = information (spec) was the active ingredient —
either answer feeds the synthesis's mechanism ranking. Reachability:
same as pd-p2. Provisional-rulings clause gives a secondary
observable: does the ledger DECLARE speclessness (the clause's
literal instruction)?

## 2026-08-04 — X11 interrogation RESULTS: one rationalization class, and X11's text mis-specified the trigger

Elicitation (gpt-5, same family as the sessions; gpt-5-codex not
servable on this key; post-hoc-confabulation caveat stands; script in
session scratch, outputs transcribed verbatim-in-substance here):
4/4 reps elicit the SAME class —

- RATIONALIZATION: "after the merge/commit I should re-run the suite
  to verify the merged tree" (belt-and-suspenders post-merge habit).
- TRIGGER: a NEW HEAD (merge or commit) without confirming the tree
  is content-identical to the tested commit.
- COUNTER (elicited, all four convergent): verify the merged/new HEAD
  is tree-identical to the tested commit; identical tree = the
  report's evidence stands; only a changed tree earns a run.

**Reframing of the X11 null:** the prohibition said "same COMMIT" —
but the re-runs cluster at the post-merge moment where the commit ID
legitimately changes over an identical TREE. The sessions' reasoning
("different commit now") passes the text's own letter. X11 didn't
fail because text can't move behavior; it failed because it
mis-specified the trigger condition. This also retro-explains the
X5-era controller re-runs (3-14/rep) clustering late-session.

**D1' arm (pd/d1p):** the read-not-rerun rule re-keyed to TREE
identity with a mechanical check ("`git diff --quiet <tested-commit>
HEAD` — empty diff means the evidence stands") + a rationalization-
table row naming the post-merge habit verbatim. Battery: pd/d1p ×4 on
cp-x5-leases-scaled vs the X11 arm's own results as the
failed-predecessor baseline (control 8/9 unchanged). Pre-registered
PASS: controller duplicate-run count median ≤2 (X11's original bar),
with the post-merge run specifically absent or preceded by the
tree-identity check. Method credit: Jesse's interrogate-then-fix
directive, first application.

## 2026-08-04 — Method doc + interrogation candidate inventory (Jesse's ask)

Method documented: docs/rationalization-interrogation-method.md;
instrument promoted: campaigns/cost-pathologies/interrogate-rollout.py.
NEW STANDING RULE (in the method doc): every behavioral-null verdict
gets an interrogation pass before its successor arm is designed.

**Failed/null experiments eligible for the method (queued, priority
order):**
1. **X1-edit attention escapes** (14/16 reviewers missed the
   unambiguous Important defect; the attention-routing thesis has NO
   elicited mechanism) — interrogate the missing reviewers: what were
   they attending to; what would have routed them. Feeds any future
   review-attention arm; also wave-cap's 0/45 (same class).
2. **Authority-gap dismissers** (x10b scan-adjudicators + P2-x10
   "internally explained" controllers) — elicit THEIR counters; if
   p2s-specless fails, elicited counters replace my hand-written
   anti-rationalization line.
3. **X5 reviewer lease-bypasses** (~1/3 of treatment reps reran
   "sometimes with no stated reason") + X5 controller reruns beyond
   the post-merge class — does the d1p row generalize or are there
   more classes?
4. **T11 turn-1 bundlers** (3/4) — confirm the escape-hatch reading
   behind x9a2's tightening before it goes to #2077's thread.
5. **Campaign 3 adjacent-breakage floor** (0/16 with U-broken-windows
   in context) — elicit why the directive never bound; likely yields
   a trigger clause ("nothing made the session LOOK") rather than a
   table row.
6. **Campaign 3 U-honesty misses** (1/arm fabrications) — n=2, cheap.

## 2026-08-04 — Authority-gap dismisser interrogation: the elicited mechanism is GREEN-AS-WAIVER, not intentionality

Interrogation of the 3 P2-x10 controllers (interrogate-rollout.py,
gpt-5, confabulation caveat standing). 3/3 convergent:

- RATIONALIZATION class: the divergences felt inconsequential/
  intentional BECAUSE everything was green — "clean merge + 27
  passing tests," "internal justifications and passing tests made
  the preflight feel clean," "no explicit error felt like permission
  to proceed" — and momentum did the rest.
- TRIGGER class: green signals (tests, clean merge, error-free scan)
  read as evidence that plan-text divergences don't matter.
- COUNTER class (convergent, and DIFFERENT from p2s's hand-authored
  line): green doesn't waive the gate — every divergence row is
  closed only by a WRITTEN ruling amended into the plan;
  "intentional" and "inconsequential" are themselves rulings to
  record, not exemptions from ruling.

**Analysis:** my p2s text attacked the intentionality inference
("'each module explains its choice' is how incoherence defends
itself"); elicitation says the operative driver is
tests-pass-so-proceed. If the running p2s-specless cell FAILS, the
successor arm (p2s') encodes the elicited counter instead:
green-signals-don't-close-rows + written-ruling-or-amend for every
row including "intentional" calls. If p2s-specless PASSES, the
distinction is moot for shipping but stays recorded for the method's
validation ledger.

**Instrument gap found:** interrogate-rollout.py selects the largest
(controller) rollout; reviewer-seat interrogations (X1-edit escapes,
inventory item 1) need rollout selection by seat — follow-up queued.

## 2026-08-04 — X1-edit reviewer interrogation: the attention escapes have a mechanism — single-instance generalization

Reviewer-seat elicitation (scratch wrapper over interrogate-rollout;
reviewer rollout selected by verdict-markers; 4 control reps; gpt-5;
confabulation caveat standing). **4/4 convergent:**

- RATIONALIZATION class: verified the REQ-2 invariant in ONE path
  (apply_adjustment — which was correct), then generalized: familiar
  pattern + green suite → "holds everywhere"; skimmed past
  generate_statement.
- TRIGGER class: green tests + a MIN_LINE_CHARGE check NEAR discount
  code (proximity read as correctness) + confirmation priming from
  the one verified path.
- COUNTER class (4/4, directly encodable): enumerate EVERY instance
  of the requirement's anchor (grep the constant/guard), verify each
  with file:line evidence before any verdict — one verified instance
  is not evidence for its siblings.

**New arm candidate (pd/x12, "invariant-instance enumeration"):** a
task-reviewer/final-reviewer instruction row from the elicited
counter. Battery-ready scenario exists with a binding baseline:
cp-x1-edit-existing, control 2.0 escapes/rep, ANCHOR-IMPORTANT escape
rate 14/16. Queued behind the running lanes.

**Cross-seat meta-pattern (three interrogations, one day):** GREEN
TESTS AS UNIVERSAL WAIVER — reviewers skip line-verification (this
entry), preflight controllers skip amendment rulings (green-as-waiver
entry), post-merge controllers justify redundant re-runs (X11 entry).
Opposite behaviors, same miscalibration: green proves code behavior
on that tree — not plan coherence, not requirement coverage the tests
don't encode, not the need to re-verify identical trees. Candidate
shared-doctrine text for the synthesis ("what green tests prove"),
applicable across writing-plans/SDD/review templates.

## 2026-08-04 — PRE-REGISTRATION: pd/x12 battery (invariant-instance enumeration on cp-x1-edit-existing)

Arm built: `cp/pd-x12` @ ae2b457 (see arm-manifest). Text = the 4/4
elicited counter, verbatim in mechanism: enumerate every instance of
an invariant's anchor, per-instance file:line verdicts, one instance
≠ siblings, proximity ≠ the check, green proves only what tests
encode. Task-reviewer seat only (the seat that failed); re-review and
final-review seats untouched.

**What this tests beyond the arm:** x1a/x1b/x1c (review-policy
exhortations) all scored NO EFFECT on this exact fixture — the
queue-campaign verdict was "review-policy exhortations do not redirect
attention." x12 is the first attention-redirect attempt whose text is
(a) a mechanical procedure rather than a policy, and (b) written from
the failing sessions' own elicited rationalization. If it moves
ANCHOR-IMPORTANT where x1a/b/c did not, that is evidence for the
interrogate-then-fix method as an arm-design discipline, not just for
this row. If it fails identically, the attention-routing thesis
(decomposition is the only lever) strengthens and the method's scope
narrows to controller-seat habits (d1p's class).

**Battery:** scenario cp-x1-edit-existing, arm pd-x12, 4 reps, next
free lane. Scored by the existing x1-edit mechanical scan (signature
regexes in the seeded-defect ledger) + mandatory hand-check of every
ANCHOR-IMPORTANT cell and any "unknown" (documented recognizer gaps:
compound lock patterns).

**Endpoints (registered before launch):**
1. PRIMARY — ANCHOR-IMPORTANT catch count: pooled baseline 2/16
   (12.5%). PASS = ≥3/4 reps catch (binomial p≈0.007 at base rate);
   1-2/4 = MOVEMENT, rerun 4 more reps before verdict; 0/4 = FAIL
   identical to x1a/b/c.
2. SECONDARY — mean escapes/rep vs control 2.0 (x1 arms: 2.0-2.5).
3. GUARD — DEBATABLE-2 (0/16 baseline) reported but not load-bearing;
   review-effort cost (reviewer turns/tokens vs control) reported —
   enumeration mandates grep passes, so a cost delta is expected and
   the question is size, not sign.
4. Reachability (standing rule): the arm text sits in the task-reviewer
   template's Part 1, which every task review reads — reachable by
   construction; hand-confirm one rep's reviewer rollout actually
   enumerates (quotes anchor instances) to verify uptake, not just
   presence.

## 2026-08-04 — X5 reviewer lease-bypass interrogation: a FOURTH class — evidence illegibility — plus a seat-misattribution instrument artifact

Question on the table: does d1p's tree-identity row cover the ~1/3 of
X5 treatment reps where a reviewer reran anyway (T8 narrative), or is
that a distinct class? Answer: distinct.

**Instrument artifact first (disclosed; the 8th-class: SEAT
MISATTRIBUTION).** The first wrapper selected "reviewer" rollouts by
verdict-marker text — but the controller's rollout contains every
dispatch prompt it composes, so verdict/template text matches the
CONTROLLER too, and the wrapper's first hit was the controller in all
6 reps. Tell-tale in the elicitations themselves: ".gitignore tweaks,"
"creating a worktree/branch" — mutations a read-only reviewer never
performs. Those 6 answers are struck as reviewer evidence. (Kept as a
WEAK controller-seat hypothesis: bootstrap-habit reruns — "my setup
snippet ends with pytest" — consistent with the 3-14 controller
reruns/rep finding, but elicited under a wrong-seat RULE framing, so
hypothesis only, would need re-elicitation under a controller RULE.)

**Correct seat selection (now IN the promoted instrument as --seat
reviewer/implementer/controller):** child threads carry
session_meta.parent_thread_id; implementer children have
patch_apply_end events; reviewer children have none. Validated: the
promoted mode selects the identical rollout the corrected wrapper
found.

**Corrected count: 6/16 treatment reps (x5a 3/8, x5b 3/8) had a
reviewer-child pytest run** — matches T8's ~1/3 narrative estimate
independently.

**Elicitations (5 reps, gpt-5, confabulation caveat standing): 5/5
convergent on EVIDENCE ILLEGIBILITY.** The reviewer re-runs because
the evidence artifact is illegible from its seat — "report output
appeared truncated," "couldn't locate the explicit reported results
for this commit," "artifacts looked incomplete," "absence of visible
prior test outputs" — so regenerating the evidence feels cheaper and
more reliable than re-reading it. Trigger class: truncated/missing
evidence views + pytest ready at hand. Elicited counter class (5/5):
the receipt is honored for this exact tree; resolve doubt by
re-reading the report/receipt, not re-running; illegibility of the
evidence is not invalidation of it.

**Class map after four interrogations:** (1) controller post-merge
new-HEAD habit → d1p; (2) preflight green-as-waiver → p2s' candidate;
(3) reviewer single-instance generalization → x12; (4) reviewer
evidence-illegibility → NEW arm candidate. Note classes 1 and 4 share
a shape: when in doubt, agents REGENERATE evidence rather than READ
it; the fix each time is making the read path mechanical and cheap
(identity check; legible receipt).

**Arm candidate (pd/x13, "illegibility is not invalidation"):** two
halves — (a) legibility: the reviewer dispatch quotes the receipt
line verbatim (x5a already does; check whether the 3 x5a bypass reps'
dispatches actually carried it — if not, the leak is the controller
omitting the citation, a different fix); (b) the elicited row in the
reviewer template: "Evidence you cannot see is not evidence that
doesn't exist: if the report or receipt looks truncated, re-read the
file at its stated path or report the gap — do not re-run the suite
to regenerate what you failed to read." Battery on cp-x5-leases-scaled
vs the 6/16 baseline. Queued behind x12.

**x13 half-(a) resolved by inspection (no spend):** the LEASE text is
present in all 3 x5a bypassing reviewers' rollouts — the citation
reached the seat and was bypassed there. x13 is the reviewer-row fix
alone; no controller plumbing change.

## 2026-08-04 — T11 bundler interrogation: the mechanism is RIDE-ALONG BUNDLING (stop-as-ask-magnet), not the escape hatch

The 4 adjudicated x9a/x7x9a bundler reps (gpt-5, --seat controller,
confabulation caveat standing). 3/4 convergent, 1 distinct:

- RATIONALIZATION class (3/4: x9a-rep1, x9a-rep2, x7x9a-rep1): "since
  I had to stop anyway for the destructive operation, bundling the
  ruling-confirmation felt safer / saved rework." TRIGGER class: a
  legitimately-required stop coinciding with a fresh consequential
  ruling — the mandatory stop opens a free channel to the human and
  pending rulings attach to it. This REVISES the queue-campaign
  hypothesis: the escape hatch ("every path forward is a guess") was
  the justification text, but the operative mechanism is the
  ask-magnet, and it needs no hatch at all.
- x9a-rep3 (distinct, n=1): misclassified a reversible test deletion
  as "destructive" → stop-list severity misclassification. Noted, no
  action at n=1.
- COUNTER class (3/3): stop for the destructive action alone; the
  ruling is ledgered with what/why/cost and execution proceeds — the
  stop message carries only the stop's own question.

**Implication for x9a2 (#2077 thread text):** x9a2's battery already
scored 0/3 bundling, and its text contains the exact counter — "Asking
your human partner to confirm rulings you have already made is a
stall, not diligence" — arrived at via the escape-hatch framing but
countering the ride-along directly. The elicitation therefore
CONFIRMS x9a2's mechanism from the failure side; no text change
(standing rule: no shipping text a battery didn't run). Candidate
sharpening if a future arm is needed: name the trigger — "a stop for
one of the four reasons carries only that question; made rulings ride
in the ledger, not in the stop message."

## 2026-08-04 — VERDICT: p2s-specless FAILS (0/5 × 3) — ground truth was the active ingredient, confirmed from the ablation side

Battery: cp-x10-consistency (specless) × pd-p2s @ 1937691 × 3 reps,
$8.78/rep avg. Pre-registered bar: ≥3/5 neutralized = rationalization-
repair works standalone.

**Result: 0/5, 0/5, 0/5 neutralized** — indistinguishable from
specless control (0/5×3) and specless P2 (1/5, 0/5, 0/5). The
spec-anchored coherence gate contributes NOTHING without a spec to
anchor to. Combined with the P2' battery (spec present: control 4-5/5
free, gated arms 5/5 + autonomy), the ablation is now two-sided:
text without ground truth 0-1/5 everywhere (three different texts:
none, P2 value-table, p2s anchor-rows); ground truth without special
text 4-5/5. The active ingredient is THE SPEC IN THE ROOM, full stop.
PR #2086's mechanism claim is confirmed at both ends.

**Instrument artifact #10 (STALE-TREE VACUITY), caught by the
mandatory hand-check:** the mechanical scan initially scored
p2s-rep1 as 5/5 "absent" — but rep1 was cut mid-final-re-review, its
modules never merged back from .worktrees/job-queue/, and the scan
grepped the empty root tree. Absence of the CODE read as absence of
the DEFECT. Hand-check of the worktree found all 5 present.
checks.sh fixed: the scan now resolves the tree it scans (root if
modules present, else the SDD worktree), emits the chosen tree as its
own line, and labels missing-module cells "not-built" instead of
"absent". Validated by stub-harness against all 3 new reps (matches
hand-score) and ALL 15 prior cp-x10-consistency/cp-x10-spec reps:
zero verdict flips (specless 4-5 present everywhere incl. the one
prior unmerged-worktree rep, control-rep2; spec arms 0-1 present).
Published P2/P2' verdicts stand.

**p2s' decision (per pre-registration):** the successor arm from the
green-as-waiver elicited counter gets built and run — not because a
text win is likely (three texts have now failed specless; the
ground-truth-gap theory predicts failure), but as the method-scope
test: if the SESSIONS' OWN elicited counter also fails where the spec
succeeds, that cleanly bounds interrogate-then-fix — elicited
counters fix mis-specified triggers and missing procedures (d1p, x12
classes), not missing authority. Paired with x12 (elicited counter
where ground truth IS reachable in-repo), the two batteries bracket
the method's domain.

## 2026-08-04 — PRE-REGISTRATION: pd/p2g battery (green-as-waiver counter, specless)

Arm `cp/pd-p2g` @ c5fd8ba (see arm-manifest): pd/p2s + the P2-x10
dismissers' elicited counter verbatim in mechanism ("green closes no
coherence rows; intentional/inconsequential are rulings you write").

**Battery:** cp-x10-consistency (specless) × pd-p2g × 3 reps, next
free lane (behind d1p on B / x12 on A). Scored by the FIXED
tree-resolving seeded-defect scan + mandatory hand-check of any rep
whose scan tree is a worktree or whose cells read not-built, +
hand-read of the preflight table/rulings.

**Endpoints:** PRIMARY — seeded defects neutralized per rep vs the
0-1/5 specless wall (control 0/5×3, P2 1/5-0/5-0/5, p2s 0/5×3).
≥3/5 in ≥2 reps = the elicited counter breaks the wall →
interrogate-then-fix reaches even authority-gap classes, and p2g's
text becomes ship-candidate alongside #2086. 0-1/5 = the wall stands
= METHOD-SCOPE RESULT: elicited counters repair mis-specified
triggers and missing procedures, not missing ground truth — the
authority gap is closed by artifacts (the spec), not text, which is
PR #2086's thesis with the strongest possible evidence behind it.
Secondary: rulings actually WRITTEN for divergent rows (hand-count) —
the counter could move ruling-writing without moving resolution
correctness (partial mechanism uptake, worth knowing either way).
