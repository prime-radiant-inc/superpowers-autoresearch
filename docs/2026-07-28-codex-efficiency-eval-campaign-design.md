# Codex efficiency eval campaign — design

Date: 2026-07-28
Status: approved by Jesse (verbal, in-session); budget $1000 total
Source: `superpowers/docs/superpowers/research/2026-07-28-codex-efficiency-audit.md`

## Goal

Build the evaluation matrix for the six Superpowers-skill experiments from the
2026-07-28 Codex efficiency audit, so that (a) each documented pathology has a
validated, discriminating eval that fails on current `dev`, and (b) later fix
work can be graded against pre-registered success criteria. Fixes themselves
are out of scope for this campaign, with one exception: `codex-spinout-fixes`
already exists and gets graded as E1's treatment arm.

## Scope decisions (settled with Jesse)

- **Six skill experiments only.** RoboRev reliability and Codex token
  telemetry are excluded; they are separate codebases with their own fix
  cycles (audit P2).
- **Tier ladder per experiment.** MINE (existing corpus, free) → MICRO
  (single-API-call phrasing sweeps) → FULL (drill-driven real Codex runs,
  ~$7–15 each). FULL only where live routing/recursion behavior must be
  observed.
- **Corpus-validated scorers.** Every scorer is validated against the audit's
  historical corpus — where ground truth is already established — before it
  grades any fresh run.
- **Budget: $1000 total**, tracked and reported; no per-battery approval
  gate.

## Campaign shape

- Home: `campaigns/codex-efficiency/`
- Hypothesis log: `logs/2026-07-28-codex-efficiency.md` — one pre-registered
  entry per experiment (prediction, scorer, success criterion) written before
  any run.
- Shared rollout-parser module in the campaign dir: parses Codex rollout
  JSONL into spawn tuples (`fork_turns`, model), session census and tree
  depth, wait calls, compactions, skill/memory reads, exec'd test commands,
  `task_complete` presence, instruction-line offset, bytes. Each experiment's
  scorer is a thin layer on this module.
- Ground-truth labels: the audit's own artifacts under
  `~/.codex/visualizations/2026/07/28/019fa9a2-87b7-73b1-a76a-efb9f14abbea/`
  (`session-manifest.json`, `deduped-summary.json`, `spawns-window.json`) and
  its scanner scripts, reused as the parser's starting point.
- Fresh-run rig: drill driving real Codex sessions, containerized
  (evals-container pattern; host runs are confounded by global CLAUDE.md),
  headless Codex auth.

### Standing rules (encoded in the campaign runner)

1. **Discrimination:** an eval counts only once its baseline on current `dev`
   exhibits the documented pathology. Inconclusive-by-zero is a stop, not a
   pass.
2. **Raw rollouts never enter the repo** — they contain client project
   content. Only scorers, aggregates, and distilled synthetic scenarios are
   committed.
3. Every scorer's matches are manually inspected before its first verdict
   (three scoring bugs in one prior campaign).
4. Correctness measures ride beside cost measures in every experiment: a
   cheaper run that parks a load-bearing defect is a regression.

## The six experiment packages

Each package: pathology signature → scorer metrics → distilled scenario →
tier plan → pre-registered success criterion (from the audit).

### E1. Codex fork hygiene (Finding 1, P0)

- **Scorer:** per-spawn tuple — `fork_turns` value, explicit-model presence,
  instruction-line offset, child rollout bytes, child skill re-reads.
- **Corpus ground truth:** 1,098 recorded spawns; 52.3% full / 13.4% partial
  / 32.7% isolated; 925 omitted models.
- **Scenario:** small SDD plan (3–4 tasks) run by a Codex controller.
- **Tiers:** MINE → FULL baseline on `dev` → FULL treatment on
  `codex-spinout-fixes`.
- **Success:** 100% isolated spawns, 100% explicit models, no loss of task
  completion.

### E2. Reviewer recursion (Finding 2, P0)

- **Scorer:** subtree census per dispatched reviewer — descendants, max
  depth, thread-limit failures, sessions missing `task_complete`, wait-call
  volume.
- **Corpus ground truth:** 129-session Remux review tree (depth 12);
  31-session Serf tree.
- **Scenario:** one branch review dispatched over a prepared
  moderately-complex branch.
- **Tiers:** MINE → MICRO (non-delegation-contract phrasing sweep, reusing
  the reviewer-directive-micro pattern) → FULL baseline.
- **Success:** zero reviewer descendants in the default case; findings
  quality preserved.

### E3. Evidence receipts / duplicate gates (Finding 3, P1)

- **Scorer:** identical-command-at-identical-tree-state detection across a
  workflow's sessions (implementer → task review → finishing).
- **Corpus ground truth:** Remux 903-unit gate run twice at `51f0f7e`; July
  14 six RED-suite reps.
- **Scenario:** SDD plan carried through finishing-a-development-branch with
  no intervening commits; count duplicate full-suite runs. Paired probe:
  mutate the tree mid-flow and assert the gate reruns (invalidation
  correctness).
- **Tiers:** MINE → FULL baseline. No treatment yet.

### E4. Proportional workflow ceremony (Finding 4, P1)

- **Scorer:** ceremony census before first code — design docs written,
  approval gates, questions asked, tool calls.
- **Corpus ground truth:** Arq cleanup helper and Remux palette follow-up
  sessions.
- **Scenario set:** three task classes — feasibility spike, bounded change in
  an existing flow, architectural change. Baseline expectation: identical
  ceremony for all three.
- **Tiers:** MINE → MICRO (path-choice classification under variant
  entry-decision guidance) → FULL baseline for ceremony counts. No treatment
  yet.

### E5. Review scope and accretion (Finding 6, P1)

- **Scorer:** seeded-defect recall by intended scope + scope-accretion
  (post-completion commits/lines attributable to review findings;
  unadjudicated new scope).
- **Corpus ground truth:** Serf project 2 (+75 commits post-completion);
  Scantastic A/B waves.
- **Scenario:** plan with four planted defects — local bug, cross-task race,
  dependency/clean-checkout break, repair-induced regression — each
  catchable only by its intended scope.
- **Tiers:** MINE → FULL baseline. Most expensive; runs last.

### E6. Context diet / compaction recovery (Finding 8, P2 but cheap to score)

- **Scorer:** post-compaction skill re-read count, bootstrap/routing
  retention (do isolated-fork rules survive compaction?), controller input
  growth.
- **Corpus ground truth:** 19,317 corpus compactions; nine direct tasks with
  111 SKILL.md reads; one root re-reading brainstorming 4× in 8 minutes.
- **Scenario:** long controller session with induced compaction, then a
  post-compaction dispatch.
- **Tiers:** MINE → FULL. The compaction hook rides along with E1's
  `codex-spinout-fixes` runs (same branch); `exp/controller-diet` is graded
  in the later fix cycle.
- **Infra risk:** deterministically forcing compaction in drill is the one
  rig unknown.

## Ordering

1. Shared rollout-parser, validated against corpus ground truth (MINE tier;
   free; unblocks everything).
2. E1 and E2 scorers + baselines (P0; E1 also grades its existing
   treatment).
3. E6 (rides on E1 infrastructure; compaction rig work).
4. E3 (duplicate-gate detection is mostly parser work).
5. E4 (micro sweep is cheap; FULL baseline small).
6. E5 (most expensive; benefits from all prior rig maturity).

## Out of scope

- RoboRev pipeline changes and evals.
- Codex token-telemetry improvements.
- Fixes for E2–E6 (follow-on cycles, graded by these evals).
- Claude Code / Gemini harness variants — this campaign is Codex-only.

## Campaign success criteria

- Six scorers validated against corpus ground truth with manually inspected
  matches.
- Six baselines on current `dev` exhibiting their documented pathology (or an
  honest inconclusive-by-zero stop recorded in the hypothesis log).
- Pre-registered success criteria on file for every future treatment.
- E1 treatment verdict on `codex-spinout-fixes` (with the compaction hook's
  E6 metrics captured from the same runs).
- Total spend ≤ $1000, itemized in the hypothesis log.

## Risks

- **Drill/Codex spawn-tree fidelity:** drill drives the root session; child
  sessions are Codex-internal. The parser must find children via rollout
  files and `thread_spawn_edges` inside the container, not via drill.
- **Forced compaction** may need prompt-padding tricks or a Codex config
  knob; budgeted as rig work in E6.
- **Baseline drift:** Codex model updates between audit window and campaign
  runs could soften pathologies; the discrimination rule catches this
  honestly.
- **Scenario realism:** distilled scenarios must be generated with the
  system under test where possible (fixture-realism rule).
