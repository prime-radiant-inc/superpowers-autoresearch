# Cost-pathologies eval campaign — design

Date: 2026-07-31
Status: drafted for Jesse's review; scope directives given in-session
(focus on cost, not wall-clock; multiple competing hypotheses per
problem; mechanical check for the two corpus-negative pathologies)
Budget: ~$580 remaining of the original $1000 envelope
Evidence base: three-host session mining, 2026-07-17..31 window, reports
in `_tmp/cost-pathologies-2026-07-31/` (local, remote-host-a,
remote-host-b — NEVER committed; aggregates only cross the line), plus
the 2026-07-28 audit and the fix-cycle's own 89-run corpus.

## Goal

Reduce the dollar cost of agent-built software by attacking the measured
cost sinks with competing candidate mechanisms, graded head-to-head by
pre-registered criteria. Wall-clock is explicitly out of scope this
campaign. Every experiment runs MULTIPLE hypotheses as parallel arms —
one-anointed-fix designs are a process failure here.

## Measured cost picture (what the mining established)

1. **Fork-tax / context inheritance**: 76.6% of one host's 11.9B codex
   tokens were full-history child forks replaying parent context
   (sqlite-verified); corroborated independently at 113B cumulative /
   99.2% duplicate content on another corpus. Structural, platform-level.
   The fix cycle's shipped dispatch guidance attacks the SDD slice;
   everything else still forks dirty.
2. **Review loops**: the dominant seat-count pathology on every corpus —
   ≥6 chains with 40+ rounds (9 reviewers on a 4-task plan); a
   32-dispatch unattended overnight chain (19 re-reviews of one file
   against a stale report, 17% clean rate); 65:30 review:impl ratio; a
   9-parallel-review wave. Reviewers do not run dry; convergence must be
   policy.
3. **Verification duplication**: 148 test invocations on one tree, one
   regression suite run 12×.
4. **Micro-dispatch overhead**: persona-style micro-dispatches paying a
   40–560K-token context floor each for tiny tasks.
5. **Invented requirements**: real, modest — 3 root-caused exemplars + 1
   reviewer finding later WITHDRAWN.
6. **Negative results (3 corpora, both harnesses)**: sidequests and
   advisory-detail escalation near-zero AS OPERATIONALIZED — with one
   mechanical check never run (M0 below) and interactive sessions
   undersampled. Jesse reports seeing both; the campaign treats the
   perception gap as a measurement question, not a dismissal.
7. **Out of campaign scope, flagged**: never-reset persistent-agent main
   loops (5.3B tokens / ~80× dominance on one host) — PA infrastructure,
   not superpowers skill text.

## Standing rules (carried from prior campaigns)

Append-only hypothesis log (`logs/2026-07-31-cost-pathologies.md`);
pre-registration before every battery; corpus-validated scorers with
manually inspected matches (non-circular); discrimination rule
(inconclusive-by-zero is a stop, and a control arm that won't fail
stops the battery); raw sessions never committed; correctness rides
beside cost in every verdict (a cheaper arm that parks defects loses);
privacy sweeps with disclosure on every commit; scrubbed hostnames in
everything published.

## M0. Mechanical closure of the negative results (pre-experiment)

Before any treatment work: (a) the sidequest check the mining never
finished — for every SDD-shaped session on all three hosts, diff the
files actually committed against the brief/task-declared file set;
out-of-scope commit ratio is the sidequest rate, with exemplars pulled
for anything >0. (b) Advisory-stall elicitation moves into X2's baseline
(seeded fixtures), since the field corpora cannot falsify it. If both
come back null again, the taxonomy entries close honestly and X2's
contract text is graded purely as a guardrail (must-not-harm), not a
fix.

## The experiments — competing hypotheses per problem

### X1. Review convergence policy (the dominant sink)

Problem: review chains that never converge because strong reviewers
always find something. Arms (each a distinct mechanism, run
head-to-head on identical fixtures):

- **X1-A criterion-backing**: a finding may block only if it cites the
  violated requirement (brief/spec/global-constraint line) or a
  concrete reachable failure path; everything else is advisory and goes
  to the ledger.
- **X1-B rising severity floor**: round N of a fix loop accepts only
  findings at or above a per-round severity floor (round 1: any
  Critical/Important; round 3+: Critical only).
- **X1-C marginal-value verdict**: every review ends with an explicit
  "would another round materially reduce risk? yes/no + what is at
  stake"; the controller stops on "no" regardless of finding count.
- **X1-D control**: current SDD policy (5-round cap + one fix wave) as
  shipped by the fix cycle.
- **X1-AB combined** if A and B both beat control independently.

Grading: rounds-to-terminal, novel-finding rate per round, cost per
task, AND defect-escape rate on fixtures with seeded known defects (the
E5 machinery) — an arm that converges fast by missing real bugs fails.
Tiers: MINE (chain-length / novel-finding-rate / severity-trend scorers
validated on the mined corpora) → MICRO (reviewer-prompt variants on a
fixed diff with known seeded-bug density; measures finding calibration
and stop-recommendation honesty per arm) → FULL (SDD runs on a buggy
fixture per arm).

### X2. Advisory plan details (Jesse's directive)

Problem statement (directive): plans carry filenames, identifiers, and
code to HELP the implementer; agents treating them as binding get stuck,
escalate, or contort. Corpus evidence thin → the fixture must elicit the
baseline. Arms:

- **X2-A plan-header contract**: writing-plans emits (and SDD briefs
  carry) an explicit "details are advisory; the spec is binding;
  deviations that preserve spec compliance are the implementer's call,
  noted in the report" block.
- **X2-B reviewer-lens fix only**: task-reviewer constraints text told
  to judge spec compliance, never plan-transcription fidelity.
- **X2-C implementer-empowerment only**: implementer template grants the
  deviation authority; plan and reviewer untouched.
- **X2-D control**: current text.

Fixture: an SDD plan seeded with advisory mismatches (a named file that
does not exist, a code snippet referencing a renamed identifier, a
stale signature) PLUS one genuine spec conflict. Criteria: advisory
mismatches produce zero BLOCKED/NEEDS_CONTEXT/human escalations and
zero reviewer findings, spec compliance preserved, AND the genuine
conflict still escalates (the discrimination guard — an arm that stops
ALL escalation fails).

### X3. Source-cited requirements

Problem: requirements invented from plausibility (pixel-equivalence,
1GB disk, AIX support — none requested). Arms:

- **X3-A reviewer citation rule**: every requirement a finding invokes
  carries its source line; uncited → suggestion, not defect.
- **X3-B implementer requirements inventory**: the report lists every
  requirement implemented with its source; unsourced entries are
  flagged by the controller before review.
- **X3-C adjudication default**: controller-side rule — uncited
  findings are ledgered as suggestions without a fix round.
- **X3-D control**.

Tiers: MICRO (baitable fixtures — an obvious "improvement" nobody
asked for) → FULL rider on X1's batteries (same runs, different
scorer). Grading: invented-requirement rate, plus a guard that real
spec requirements still get enforced.

### X4. Fork-tax field verification + universal isolation

Measurement study, not a text treatment (the treatment shipped with the
fix cycle): (a) instrument the mined corpora's signature (child bytes ÷
parent bytes; inherited-prefix duplicate ratio) into a reusable scorer;
(b) once the open PRs merge and field sessions accumulate, measure the
before/after on fresh trees; (c) audit every other skill that spawns
(dispatching-parallel-agents first) for full-history forks and propose
the isolation default there as a follow-up treatment if the audit finds
dirty forks. Cost: near-zero (scorer work + field data that accrues on
its own).

### X5. Verification leases (phase-2 item, now properly baselined)

Problem: identical suites re-run at identical tree state (12× worst
case). Arms:

- **X5-A receipts in report**: implementer report carries
  command+tree-SHA+result; reviewers and finishing honor receipts at
  unchanged SHA.
- **X5-B machine-checkable receipt file**: same, but as a workspace
  artifact the next seat verifies mechanically.
- **X5-C control**.

Prerequisite scorer work: the substring-aware duplicate-command counter
(the known `score_e3` upgrade). Guard: the invalidation probe — mutate
the tree mid-flow and the suite MUST re-run (an arm that skips a
required re-run fails regardless of savings).

### X6. Micro-dispatch floor

Problem: dispatching an agent costs a context floor regardless of task
size. Arms:

- **X6-A batching rule**: N small same-shape edits go to ONE subagent
  as a batch brief.
- **X6-B inline-when-trivial**: controller text — work that fits in a
  couple of tool calls is done inline, not dispatched (with an explicit
  boundary so it cannot swallow real tasks).
- **X6-C control**.

Tiers: MINE (dispatch-floor distribution from the mined corpora) →
FULL (fixture with a dozen small edits, cost per completed edit per
arm; quality guard: all edits reviewed and correct).

## Ordering and budget

1. M0 mechanical check (mining follow-up; ~$0 API, subagent time only)
2. X1 MINE + MICRO (~$30) → X1 FULL (~$150, the priority battery)
3. X2 fixture + baseline + arms (~$80)
4. X3 MICRO + rider (~$15)
5. X5 scorer upgrade + battery (~$60)
6. X6 MINE + battery (~$40)
7. X4 instrumentation (rides along; field data accrues post-merge)

Estimated total ≈ $375, reserve ≈ $200 for re-runs and surprises.

## Success criteria

- Every experiment ships either (a) a winning arm with pre-registered
  criteria met and correctness guards intact, or (b) an honest
  negative/inconclusive verdict in the log.
- Scorers validated against the mined corpora before grading any fresh
  run.
- No treatment ships text that a battery did not run (the fix cycle's
  433184c lesson, now a standing rule).
- Cross-arm comparisons reported even where all arms pass — the point
  is which mechanism wins, not whether any works.

## Out of scope

- Wall-clock/parallelism work (deferred portfolio exists).
- PA persistent-session hygiene (separate track, flagged to Jesse).
- RoboRev, token telemetry (still separate codebases).
- Adopting Drew's stack text (his PR evals proceed independently).
