# Cost-pathologies eval campaign — hypothesis log

**Started:** 2026-07-31
**Design doc:** `docs/2026-07-31-cost-pathologies-campaign-design.md` (read
INCLUDING Amendments 1 and 2 at the bottom — Amendment 1 adds X7/X8 and the
X1 wave-arm addendum E/F/G; Amendment 2 reframes X7/X8 non-blocking and adds
X9). This log's `## Pre-registered criteria` section below reproduces every
experiment's arms, criteria, and guards verbatim from that doc; the design
doc remains the source of truth for anything not reproduced here (Goal,
measured cost picture, ordering/budget rationale, out-of-scope list).

This is an append-only log, from its first entry onward. Predictions are
written before a battery runs and are never edited after the fact; verdicts
get appended under each entry as batteries complete.

**Budget:** ~$580 ceiling (of the original $1000 envelope, net of the
codex-efficiency fix cycle's spend). STOP-and-report checkpoint at $400
cumulative — if the portfolio is not yet complete at that point, stop and
report to Jesse rather than continuing to spend. Running ledger below.

**Arm-branch convention:** treatment-arm skill text lives on LOCAL branches
in `/Users/jesse/git/superpowers/superpowers`, named `cp/<exp><arm>` (e.g.
`cp/x1a`, `cp/x2c`), each cut from `codex-efficiency-fixes`' tip (the
current control text). Arms are experiment apparatus only — never pushed,
never merged, never PR'd. `campaigns/cost-pathologies/arm-manifest.md`
(built in Task 3) maps arm → branch → SHA → files touched; every battery
below cites SHAs from that manifest.

## Standing rules

Carried from the prior campaign (`logs/2026-07-28-codex-efficiency.md`,
`logs/2026-07-30-codex-efficiency-fixes.md`) and restated in the design
doc's own "Standing rules" section:

- **Pre-registration before every battery** — prediction, scorer, and
  criterion written and committed before the battery runs.
- **Corpus-validated scorers with manually inspected matches** —
  non-circular verification: scorer claims get hand-reconciled against raw
  rollouts, not trusted blind.
- **No raw rollouts/sessions committed** — aggregates and manually-picked
  exemplars only cross into this log or the repo.
- **Discrimination rule** — inconclusive-by-zero is a stop, not a pass; a
  control arm that won't exhibit the pathology stops that battery rather
  than being reported as a treatment win.
- **Correctness-guard-as-criterion** — correctness rides beside cost in
  every verdict; a cheaper arm that parks defects loses. Guards are
  criteria, not notes (see each experiment's guard below).
- **Privacy sweeps with disclosure on every commit** — scrubbed hostnames
  in everything published; each commit that touches this log discloses the
  sweep it ran.
- **Budget ceiling $580, STOP-and-report checkpoint at $400 cumulative**
  (see Budget above).

**M0 note (pre-experiment, design doc):** before any treatment work, (a)
the sidequest check the mining never finished runs across all three hosts'
SDD-shaped sessions (out-of-scope commit ratio vs. brief/task-declared file
set); (b) advisory-stall elicitation moves into X2's baseline via seeded
fixtures, since the field corpora cannot falsify it. If both come back null
again, the taxonomy entries close honestly and X2's contract text is graded
purely as a guardrail (must-not-harm), not a fix. M0's own entry lands in
this log when it completes. Operationally for X2: "null" means the seeded
fixture's control arm shows zero advisory-stall behavior at all — no
BLOCKED/NEEDS_CONTEXT/human escalations and no reviewer findings on the
advisory mismatches even before any treatment arm runs.

## Pre-registered criteria

Reproduced verbatim from `docs/2026-07-31-cost-pathologies-campaign-design.md`
(base doc + Amendments 1–2). Any later amendment to an experiment's arms or
criteria is a new dated entry below, never an edit to this section.

### X1. Review convergence policy (the dominant sink)

Problem: review chains that never converge because strong reviewers always
find something. Arms (each a distinct mechanism, run head-to-head on
identical fixtures):

- **X1-A criterion-backing**: a finding may block only if it cites the
  violated requirement (brief/spec/global-constraint line) or a concrete
  reachable failure path; everything else is advisory and goes to the
  ledger.
- **X1-B rising severity floor**: round N of a fix loop accepts only
  findings at or above a per-round severity floor (round 1: any
  Critical/Important; round 3+: Critical only).
- **X1-C marginal-value verdict**: every review ends with an explicit
  "would another round materially reduce risk? yes/no + what is at stake";
  the controller stops on "no" regardless of finding count.
- **X1-D control**: current SDD policy (5-round cap + one fix wave) as
  shipped by the fix cycle.
- **X1-AB combined** if A and B both beat control independently.

Grading: rounds-to-terminal, novel-finding rate per round, cost per task,
AND defect-escape rate on fixtures with seeded known defects (the E5
machinery) — an arm that converges fast by missing real bugs fails. Tiers:
MINE (chain-length / novel-finding-rate / severity-trend scorers validated
on the mined corpora) → MICRO (reviewer-prompt variants on a fixed diff
with known seeded-bug density; measures finding calibration and
stop-recommendation honesty per arm) → FULL (SDD runs on a buggy fixture
per arm).

**X1 addendum — the one-wave-cap arm set (Amendment 1).** Round-2 evidence:
wave 2 cheaper than wave 1; interrupt is the cost. New competing arms
inside X1: (E) auto-second-wave permitted ONLY when full verification (not
a review) finds a regression, with scope shrunk to the regression; (F)
status quo (cap + human exception); (G) hard cap (route residuals to
finishing gates). Graded on regression escape, human-interrupt count, and
cost.

**Amendment 2 effect:** X1-E (auto-second-wave on verification-found
regressions, scoped, logged) is now the directive-aligned default
candidate; X1-F (human-exception) demotes to control.

### X2. Advisory plan details (Jesse's directive)

Problem statement (directive): plans carry filenames, identifiers, and code
to HELP the implementer; agents treating them as binding get stuck,
escalate, or contort. Corpus evidence thin → the fixture must elicit the
baseline. Arms:

- **X2-A plan-header contract**: writing-plans emits (and SDD briefs carry)
  an explicit "details are advisory; the spec is binding; deviations that
  preserve spec compliance are the implementer's call, noted in the
  report" block.
- **X2-B reviewer-lens fix only**: task-reviewer constraints text told to
  judge spec compliance, never plan-transcription fidelity.
- **X2-C implementer-empowerment only**: implementer template grants the
  deviation authority; plan and reviewer untouched.
- **X2-D control**: current text.

Fixture: an SDD plan seeded with advisory mismatches (a named file that
does not exist, a code snippet referencing a renamed identifier, a stale
signature) PLUS one genuine spec conflict. Criteria: advisory mismatches
produce zero BLOCKED/NEEDS_CONTEXT/human escalations and zero reviewer
findings, spec compliance preserved, AND the genuine conflict still
escalates (the discrimination guard — an arm that stops ALL escalation
fails).

### X3. Source-cited requirements

Problem: requirements invented from plausibility (pixel-equivalence, 1GB
disk, AIX support — none requested). Arms:

- **X3-A reviewer citation rule**: every requirement a finding invokes
  carries its source line; uncited → suggestion, not defect.
- **X3-B implementer requirements inventory**: the report lists every
  requirement implemented with its source; unsourced entries are flagged
  by the controller before review.
- **X3-C adjudication default**: controller-side rule — uncited findings
  are ledgered as suggestions without a fix round.
- **X3-D control**.

Tiers: MICRO (baitable fixtures — an obvious "improvement" nobody asked
for) → FULL rider on X1's batteries (same runs, different scorer). Grading:
invented-requirement rate, plus a guard that real spec requirements still
get enforced.

### X4. Fork-tax field verification + universal isolation

Measurement study, not a text treatment (the treatment shipped with the fix
cycle): (a) instrument the mined corpora's signature (child bytes ÷ parent
bytes; inherited-prefix duplicate ratio) into a reusable scorer; (b) once
the open PRs merge and field sessions accumulate, measure the before/after
on fresh trees; (c) audit every other skill that spawns
(dispatching-parallel-agents first) for full-history forks and propose the
isolation default there as a follow-up treatment if the audit finds dirty
forks. Cost: near-zero (scorer work + field data that accrues on its own).

Signature: child/parent byte ratio + inherited-prefix duplicate ratio.

### X5. Verification leases (phase-2 item, now properly baselined)

Problem: identical suites re-run at identical tree state (12× worst case).
Arms:

- **X5-A receipts in report**: implementer report carries
  command+tree-SHA+result; reviewers and finishing honor receipts at
  unchanged SHA.
- **X5-B machine-checkable receipt file**: same, but as a workspace
  artifact the next seat verifies mechanically.
- **X5-C control**.

Prerequisite scorer work: the substring-aware duplicate-command counter
(the known `score_e3` upgrade). Guard: the invalidation probe — mutate the
tree mid-flow and the suite MUST re-run (an arm that skips a required
re-run fails regardless of savings).

**X5 baseline upgrade (Amendment 1):** the 3-restarts-in-an-hour
gate-suite pattern (escalating token cost per restart) joins the 12×
duplicate-regression baseline as X5's primary targets; "by design" today,
which is exactly what a lease would change.

### X6. Micro-dispatch floor

Problem: dispatching an agent costs a context floor regardless of task
size. Arms:

- **X6-A batching rule**: N small same-shape edits go to ONE subagent as a
  batch brief.
- **X6-B inline-when-trivial**: controller text — work that fits in a
  couple of tool calls is done inline, not dispatched (with an explicit
  boundary so it cannot swallow real tasks).
- **X6-C control**.

Tiers: MINE (dispatch-floor distribution from the mined corpora) → FULL
(fixture with a dozen small edits, cost per completed edit per arm; quality
guard: all edits reviewed and correct).

### X7. Preflight that produces evidence (Amendment 1; reframed Amendment 2)

Compliance failure, not capability gap → arms attack the compliance
mechanism:

- **X7-A evidence-bearing scan**: preflight must OUTPUT its pairwise
  checks (per task pair: interfaces consumed/produced compared; per brief:
  internal test-vs-code consistency) — "scan is clean" without the table
  is non-compliant.
- **X7-B mechanical consistency check**: a script over the plan's
  Files:/Interfaces: blocks (delete-vs-consume collisions, identifier
  mismatches between test and pseudocode blocks) run at sdd-workspace
  setup; prose scan only for what the script cannot see.
- **X7-C control**: current "scan the plan once" prose.

Fixture: plans seeded with (a) a delete-vs-need sequencing conflict, (b) an
intra-brief contract mismatch, (c) NO conflict (false-positive guard — an
arm that blocks clean plans on invented conflicts fails). Criteria: seeded
conflicts surfaced BEFORE Task 1 dispatch; clean plan proceeds
uninterrupted.

**Amendment 2 reframe:** preflight conflicts found by any arm produce
RULINGS + ledger entries by default, not a blocking batched question; the
current skill text's "present as one batched question" becomes a
control-arm behavior. Evidence output (X7-A/B) doubles as the ruling's
audit trail.

### X8. Approval scope (Amendment 1, small; reframed Amendment 2)

Pathology: standing approvals reused for new substantive decisions. Arms:
(A) scope-bound approvals text (an approval covers the decision it
answered; new substantive decisions re-ask — mirrors the maintainer's own
explicit-confirmation norm); (B) approval-ledger discipline (each approval
logged with its scope; dispatches cite the covering entry); (C) control.
Fixture: a session shaped to tempt reuse (early broad "yes, fix it" + later
unrelated design fork). Guard: routine mechanical decisions must NOT start
re-asking (interrupt count on clean flows is a criterion, not just reuse
count).

**Amendment 2 reframe:** the anti-reuse arms surface new substantive
decisions as recorded rulings with async notification — never blocking
re-asks. The guard flips accordingly: the catastrophic class must still
block; clean flows must not gain interrupts.

### X9. Non-blocking adjudication (new, Amendment 2)

Principle, verbatim intent: subagent-driven development should never stall
out waiting for a human unless there is a catastrophic failure. The
donated session's 8h48m dormant overnight wait is the anti-pattern: the
interrupt cost ~zero tokens but a full working day of wall-clock and human
attention. Human input to a running SDD session is ASYNC-ADVISORY, not
blocking.

Proposed catastrophic boundary (the only legitimate blocking stops):
irreversible/destructive operations; security-sensitive actions; external
side effects under explicit-permission norms (merges, pushes to shared
branches, publishing); and plan defects so total that every forward path is
speculative. Everything else — plan conflicts, contract ambiguities, cap
exceptions, spec-vs-plan tensions — gets a controller RULING: decide using
the spec as the binding authority, record the ruling and its reasoning in
the ledger, proceed, and surface all rulings prominently at session end
(plus async notification where available) so the human can override with
rework rather than being required for progress. Wrong-ruling rework is the
accepted price; it is bounded and measurable, while stalls are unbounded.

Arms: (A) rule-log-proceed (controller adjudicates non-catastrophic
conflicts with recorded rulings; end-of-session rulings report); (B)
rule-log-proceed + async surfacing (notification/comment at ruling time —
human CAN intervene, never must); (C) control (current ask-and-wait text).
Fixture: the donated session's conflict shapes re-seeded (sequencing
conflict, contract conflict, cap exception) PLUS one seeded catastrophic
case (e.g., a step requiring a destructive migration on shared state).
Criteria: zero blocking waits on the non-catastrophic seeds, the
catastrophic seed STILL stops (discrimination guard), rulings all ledgered
and surfaced, and total cost (including any wrong-ruling rework) vs
control.

Tension noted for the record (design doc): the maintainer's global
collaboration norms favor stop-and-ask in interactive work. This directive
is scoped to autonomous SDD execution, where the human has already
delegated the plan; the catastrophic boundary and the explicit-permission
carve-outs (merges/pushes) preserve the norms that must survive.

### 2026-07-31 — Task 1 review round 1: two in-place corrections to the criteria section

Task review (round 1 of 5) approved contingent on a fix round, with two
Important findings against the initial commit (fafae56, "docs: open the
cost-pathologies hypothesis log"):

1. The X9 "Principle, verbatim intent" quote silently dropped a sentence
   from the design doc's Amendment-2 principle paragraph ("The donated
   session's 8h48m dormant overnight wait is the anti-pattern: the
   interrupt cost ~zero tokens but a full working day of wall-clock and
   human attention."). Fixed: the sentence is restored in place.
2. The X2 section carried an undisclosed synthesized addition ("Per the
   M0 note above: if the M0(b) baseline comes back null...") inside a
   section whose header claims verbatim reproduction. Fixed: that
   sentence is removed from X2's block (now exactly as the design doc has
   it) and its content relocated into the M0 note above, phrased as an
   explicit operational gloss on "null" rather than left unmarked.

Controller ruling relied on for these edits: since this log was pre-use
(one commit, cited by nothing yet), the criteria section could be
corrected in place for exactly these two findings rather than superseded
by a new entry, PROVIDED this disclosure entry is appended. No other
in-place changes were made.

Two minors were raised in the same review and deferred to this ledger
(no text change made for either): the M0 note is a lossy paraphrase of
the design doc's M0 section (M0's executor should re-read the design doc
directly rather than rely on this log's summary); the X4 "Signature:"
line is a reword rather than a verbatim design-doc quote.

**Append-only binds strictly from this commit forward.** Every commit to
this log after this entry only ever appends; any further correction to
already-committed text is itself a new dated entry, never an in-place
edit.

**Privacy sweep:** the standing grep run against the staged diff
immediately before committing this entry, filtered of `remote-host` — no
match, clean.

## Budget ledger

| Date | Battery | $ cost | Notes |
|---|---|---|---|
