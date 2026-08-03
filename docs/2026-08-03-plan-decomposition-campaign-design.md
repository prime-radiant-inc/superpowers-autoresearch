# Plan-Decomposition Campaign — Design (2026-08-03)

Campaign 2 of the 2026-08 program. Directive (Jesse, 2026-08-02): redo
writing-plans in the direction of radical task decomposition, the
simplest thing that could possibly work, up-front derisking, and full
vertical slices first (walking skeleton); give subagent-driven-
development a way for implementers to forward a body of knowledge to
future implementers; fix review guidance so non-catastrophic issues
stop rathole-ing task loops (cleanup-wave ledger); stop re-running the
same tests/linters on the same code across agents; consider per-phase
or per-task plan files (observed return-window overflow failures); and
add a tooling-setup ask (linting/auto-formatting before code) —
placement in brainstorming vs writing-plans to be determined. Goals:
save tokens AND dramatically increase performance, with guards so
neither buys the other.

## Empirical foundation (three campaigns, all published in this repo)

1. **The authority gap** (backlog X10): mechanical scanning closes the
   reviewer ATTENTION gap, but plan authority dismisses 100% of
   surfaced cross-module inconsistencies — each side is individually
   plan-mandated. Coherence is a PLAN-time property; post-hoc review
   cannot recover it.
2. **Attention-routing thesis** (queue X1-edit + wave-cap): review
   attention follows diff+task routing, not policy text; unambiguous
   defects escape 14/16 while routed judgment-cases are caught 14/16.
3. **Structural-dedupe constraint** (X5-A/B + X11): three informational
   treatments failed to change re-verification; duplication is
   controller-seated (3-14 reruns/rep). Only removing the run from the
   action space is left standing.
4. **Review-lens effect size** (X2-B micro): the substance-over-
   structure lens suppresses structure-only findings 10/10→0/10 at
   zero false-positive cost. Plain reviewers escalate structure
   conformance to the controller — the rathole ask-class.
5. **Cost anchors** (cost-pathologies): median dispatch floor-ratio
   79,504×; 2.7M-token never-compacted orchestrator = 66% of a
   session's spend; 42k-char dispatch prompt pathology; X6-A batching
   (shipped, PR #2078) cut 73% cost/87% dispatches where it binds.
6. **Fresh-session localization**: fresh sessions don't over-ask,
   over-invent, or deviate; late/aged-session claims need the replay
   harness (designed, not yet built).

## The redesign axes, as competing hypotheses

Every axis gets a control (current skill text) and one or more
treatment arms. Batteries run on an AUTHORING+EXECUTION pipeline
fixture — the session receives a spec, writes the plan with
writing-plans, then executes it with SDD in the same run. This is the
fixture class the W hypothesis has always needed: authoring-side arms
can finally act.

- **P1 — plan-as-directory** (per-task files + `plan.yaml` manifest
  (files, deps, interfaces, scope) + shared constraints doc) vs
  monolithic plan file. Predicts: return-window failures eliminated;
  brief-extraction obsolete; mechanical preflight and scope audit
  become possible. Directly tests Jesse's per-task-files direction.
- **P2 — plan-time coherence gate**: X7-A evidence-bearing preflight +
  the consistency scanner run against the PLAN's own specified
  constants/interfaces before Task 1, findings ruled by the controller
  as plan AMENDMENTS (authority applied at the right layer). Predicts:
  X10's seeded-defect classes die at plan time. The authority-gap fix.
- **P3 — walking skeleton**: plan orders a full end-to-end vertical
  slice first, then widens; vs layer-by-layer. Predicts: integration
  defects surface in Task 1-2 instead of final review; earlier
  fail-fast on spec misunderstanding.
- **P4 — radical right-sizing at authoring** (the W hypothesis):
  simplest-thing task shaping, micro-tasks merged at plan time;
  measured against X6-A's execution-side batching (already shipped) —
  both-ship is the expected outcome, the question is marginal value.
- **K1 — knowledge-forwarding**: a `handoff.md` per task (append-only:
  discoveries, environment quirks, plan corrections, interface
  decisions) carried into every later dispatch; vs today's
  interfaces-only forwarding. Predicts: repeated-discovery cost drops
  (measure: duplicate exploration commands across implementers);
  plan-defect rework drops.
- **R1 — review triage / cleanup wave**: findings classed
  {catastrophic, blocking, deferrable}; deferrable findings ledgered
  and fixed in one wave at a stopping point, task loop proceeds; plus
  the x2b lens question as policy sub-arms (suppress vs
  downgrade-to-deferred). Predicts: fix-loop rounds per task drop
  without defect-escape growth (escape guard binds — X1-edit fixture
  class re-used).
- **D1 — structural dedupe**: the implementer's report carries a test
  transcript artifact; the controller's dispatch templates and
  finish checklist get NO test-run step (removed, not prohibited) and
  the task-reviewer template's verification step points at the
  transcript. If text-removal still fails, harness-level (deny the
  controller the runner) is the follow-up. Tests the last standing
  dedupe mechanism class.
- **T1 — tooling-setup ask**: one question offering
  linter+formatter+hook setup before code; placement A (brainstorming,
  with git-init) vs placement B (writing-plans header step). Cheap
  triggering-style eval, not a FULL battery.

## Fixtures and instruments to build (in order)

1. **Pipeline fixture** `pd-pipeline`: a spec (multi-module service,
   ~6-10 natural tasks, includes 3 micro-edits and 1 cross-cutting
   constant family) + scripted deflections + checks measuring: plan
   shape (file count/sizes, task sizes), execution outcome
   (post-checks), dispatch counts, coherence defects in final tree
   (scanner), duplicate exploration/verification counts. One fixture
   serves P1-P4/K1/D1 arms.
2. **Return-window overflow probe**: a spec sized so a monolithic plan
   exceeds one write (reproduces Jesse's observed failure); P1's
   discriminating scenario.
3. **Scorers**: plan-shape scorer (parses plan dir or file), duplicate-
   discovery scorer (command dedup across implementer rollouts —
   score_x11 machinery generalized), coherence scorer (scanner on
   final tree), review-round/escape guards (existing).
4. **Micro-instruments first** where the question is judgment-layer:
   R1's lens-policy sub-arms run as x2b-review-micro variants (~$5
   each) before any FULL battery.

## Metrics and guards (both axes, per directive)

Cost axis: total $/rep, dispatch count, tokens per completed task,
duplicate-verification count, duplicate-discovery count. Performance
axis: post-check completion, defect-escape guard, coherence-defect
count, fix-loop rounds, wall-clock. A treatment ships only if it wins
an axis without losing a guard.

## Order of work

1. Instruments + pipeline fixture (build + review + MICRO validation).
2. P1 + P2 battery (the two most load-bearing, shared fixture).
3. R1 micro-instruments; D1 battery on the X5 fixture (existing
   duplicate-count baseline); K1 on the pipeline fixture.
4. P3/P4 battery; T1 triggering eval.
5. Synthesis: compose winning arms into one writing-plans + SDD
   revision set; composed-arm battery (X7+X9 precedent); PRs.

Budget: ≈$836 available; estimate $250-400 batteries + micro spend.
Standing discipline unchanged (pre-registration, reachability
statements, pinned deflections, guards-as-criteria, needle sweeps,
no ungraded shipped text, arm branches local-only).
