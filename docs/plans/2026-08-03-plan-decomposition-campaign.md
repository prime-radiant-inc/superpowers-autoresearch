# Plan-Decomposition Campaign Implementation Plan (2026-08-03)

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development.

**Goal:** Execute the campaign in `docs/2026-08-03-plan-decomposition-campaign-design.md`
(8 competing-hypothesis axes; authoring+execution pipeline fixture; both-axes
metrics with guards).

**Method:** unchanged standing discipline — pre-registration (incl. arm
reachability) before every battery in `logs/2026-08-03-plan-decomposition-campaign.md`,
append-only corrections, guards-as-criteria, pinned deflections, needle sweeps,
no ungraded shipped text, arms local (pd/* branches off sim/dev-postmerge
@ 1fed99d), lanes A+B, micro-instruments before FULL batteries for
judgment-layer questions.

**Budget:** ≈$836; estimate $250-400.

## Tasks

### Task 1: Pipeline fixture `pd-pipeline`
Authoring+execution scenario: spec (multi-module service, 6-10 natural tasks,
3 micro-edit candidates, 1 cross-cutting constant family), story.md pinned
deflections, setup.sh (exec bit), checks.sh measuring plan shape, completion,
and emitting coherence/dispatch observables. Session is asked to brainstorm-
skip (spec is final), write the plan with writing-plans, then execute with
SDD. MICRO validation script proving the checks fire on constructed
plan+tree post-states.

### Task 2: Scorer stack
(a) plan-shape scorer (monolith or directory; task count/sizes; return-window
failure detection from rollout write errors); (b) duplicate-discovery scorer
(generalize the X11 command extractor: same-command-class repeats across
implementer rollouts + controller); (c) coherence wiring (x10-consistency-scan
over final trees, plus over PLAN text for P2 arms); (d) reuse review-round +
escape guards. Corpus-validate (b) against the X5-scaled corpus (known 3-14
controller baseline).

### Task 3: Return-window overflow probe
Spec sized so a monolithic plan exceeds one model write; P1's discriminating
scenario. Small fixture variant of Task 1's scenario.

### Task 4: P1 + P2 arms + battery
Controller drafts pd/p1 (plan-as-directory: writing-plans emits per-task files
+ plan.yaml manifest + shared constraints doc; SDD consumes manifest instead
of brief extraction) and pd/p2 (plan-time coherence gate: preflight + scanner
on plan, findings ruled as plan amendments). Battery on pd-pipeline + overflow
probe: control ×3, p1 ×3, p2 ×3, p1+p2 composed ×3.

### Task 5: R1 review-triage micro-instruments
x2b-review-micro variants: lens-suppress vs lens-downgrade-to-deferred vs
cleanup-wave instruction; graded on severity/verdict language vs the
controls' noise floor. ~$15 total. FULL R1 battery only if micro shows a
usable policy separation.

### Task 6: D1 structural-dedupe arm + battery
pd/d1: remove the controller/reviewer test-run steps from dispatch + reviewer
templates (structural removal, not prohibition; report carries test
transcript artifact). Battery on cp-x5-leases-scaled (existing baseline):
d1 ×4 + contemporaneous control ×2. Primary: controller duplicate-run count
(X11 scorer, corrected extractor).

### Task 7: K1 knowledge-forwarding arm + battery
pd/k1: append-only handoff.md per task carried into later dispatches. Battery
on pd-pipeline: k1 ×3 vs Task 4's control cells. Primary: duplicate-discovery
count + plan-correction rework.

### Task 8: P3 + P4 arms + battery
pd/p3 (walking-skeleton ordering rule in writing-plans) and pd/p4 (radical
right-sizing/simplest-thing task shaping). Battery on pd-pipeline: p3 ×3,
p4 ×3 vs existing controls. P4 scored against X6-A's shipped batching
(marginal-value question).

### Task 9: T1 tooling-setup ask triggering eval
Draft the ask text; placement A (brainstorming) vs B (writing-plans);
headless triggering-harness style eval (does the ask fire; does it fire
before code), not a FULL battery.

### Task 10: Synthesis + composed battery + closeout
Compose winning arms into one writing-plans + SDD revision set; composed
battery ×3; closeout report; PR set for Jesse.

## Order
T1 → T2 (serial, same repo) → T3 → T4 (battery early) → T5/T6 (lanes+API
overlap) → T7 → T8 → T9 → T10.
