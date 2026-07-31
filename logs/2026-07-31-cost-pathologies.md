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

## 2026-07-31 — M0 VERDICT: mechanical sidequest check (controller entry)

The M0 check registered in the design doc has run on all three hosts
(full report: `_tmp/cost-pathologies-2026-07-31/m0-sidequest-mechanical-check.md`,
uncommitted corpus). Results, aggregates only:

- Discretionary sidequests: 2 in ~90 checked SDD units (local 0,
  remote-host-a 2 — both small, disciplined lint-cleanup commits
  self-justified in their commit messages, remote-host-b 0).
- **Verdict per the M0 clause: the SIDEQUESTS taxonomy entry closes as
  near-zero-where-measurable.** No sidequest experiment is designed
  from this evidence; X2 proceeds on its fixture-elicited baseline as
  planned.
- **The load-bearing caveat:** declared scope was RECOVERABLE for only
  17–24% of codex work on two hosts (encrypted inter-agent dispatch
  payloads; on-disk briefs going stale when work diverges) vs ~100% on
  the third once sibling-worktree plan docs were searched. For most
  codex sessions "no sidequest" is UNFALSIFIABLE, not confirmed. Two
  large-diff judgment calls (classified legitimate-necessity) and a
  sampled-not-exhaustive 229-dispatch sub-corpus are flagged inside the
  report. Checked population is biased toward the miners'
  already-interesting picks, not a random sample.
- **Follow-up-treatment note for the closeout (not this campaign):
  scope auditability** — machine-readable declared-scope in dispatches
  would turn this unfalsifiable region into a measurable one.

Privacy sweep run on this entry before commit (standard needle set,
filtered of the scrubbed remote-host placeholders): no match, clean.

## 2026-07-31 — Task 2: MINE scorer pack (X1 chains, X4 fork-tax, X6 floor) — corpus validation

Three new MINE-tier scorers, built TDD against synthetic fixtures (no
real content), then validated read-only against real corpus exemplars
from the "Sessions worth deep human follow-up" list in
`_tmp/cost-pathologies-2026-07-31/local-host-report.md` (uncommitted).
Reconciliation below is non-circular: every hand-check was written fresh
against raw `json.loads`, never calling `rollout_parser` or the scorers'
own helpers. Full paths and Codex task_names cited below are the same
class of low-sensitivity SDD-taxonomy/provenance labels this campaign's
own DESIGN.md and rollout_parser.py already cite verbatim (e.g. "Remux
root 019f95af-...", `task1_implementer`); no finding text, file:line
content, or other session substance is quoted anywhere below.

### score_x4_forktax.py (fork_stats) — 2 exemplars, both exact

| Exemplar (parent -> child) | Scorer byte_ratio | Hand byte_ratio | Scorer dup_ratio | Hand dup_ratio (independent two-pointer walk, not difflib) | Match |
|---|---|---|---|---|---|
| Scantastic `.../07/26/rollout-...19-38-19-019fa16f-feab.../` -> `task6_spec_review_a` child | 0.42479 | 0.42479 (`os.path.getsize`) | 0.278335 | 0.278335 | exact |
| remux `.../07/24/rollout-...17-27-37-019f96ab.../` -> `app_ui_review` child | 0.28537 | 0.28537 | 0.131713 | 0.131713 | exact |

A third pair from the same remux root (`ssh_core_review`) and all four
`task6_spec_*` children were also spot-checked for byte sizes only (all
exact via `os.path.getsize`). The two full dup-ratio hand-derivations
used a from-scratch two-pointer "advance the child index by exactly one
per matched record, allow the parent index to skip ahead" walk over
`(type, json.dumps(payload))` keys — a different algorithm from the
scorer's `difflib.SequenceMatcher`-based contiguous-run detection — and
landed on the identical ratio to 6 decimal places on both, a strong
non-circular confirmation.

### score_x6_floor.py (dispatch_floor) — 2 exemplars, 6 dispatches, all exact

| Exemplar | Dispatches checked | total_tokens (scorer vs hand) | useful_output_tokens (scorer vs hand) | Match |
|---|---|---|---|---|
| Scantastic task6 chain (4 spawns under one parent) | review_a, review_b, rerun_a, rerun_b | 9618234/9618234, 9802048/9802048, 16976755/16976755, 17467492/17467492 | 562/562, 307/307, 344/344, 685/685 | exact, all 4 |
| remux review-fractal root (2 of its 12 spawns) | app_ui_review, ssh_core_review | 2750639/2750639, 4548068/4548068 | 830/830, 651/651 | exact, both |

Hand values: `total_tokens` = the LAST `event_msg/token_count` event's
`info.total_token_usage.total_tokens` found by a from-scratch line scan
(never summed — see score_x6_floor.py's and score_x1_chains.py's module
docstrings for why cumulative-per-file is the correct, non-double-
counting reading of this corpus field, per this task's explicit
constraint). `useful_output_tokens` = `len(final_answer_message) // 4`,
hand-computed from the same from-scratch scan.

### score_x1_chains.py (chain_stats) — 2 exemplars, real bug found and fixed

**Exemplar 1 — Scantastic `task4` chain**, parent
`.../07/26/rollout-...19-37-57-019fa16f-aac5.../` , 21 real `spawn_agent`
calls (`task4_implementer` then 20 review-shaped dispatches named
`review`/`rereview`/`final`/`last`/`terminal`/`quality`/`qualityfix`/
`py313`/`noring`/`veto`, each an `_a`/`_b` pair). Hand count (fresh
`extract_spawns`-equivalent read plus a from-scratch presence check for
each child's `phase=="final_answer"` message): 21 spawns, 1 excluded as
the presumed implementer, 20 candidate rounds, 3 of the 20
(`qualityfix_b`, `veto_a`, `veto_b`) have no final-answer message. Scorer
output: `dispatch_count=20`, `rounds=17` — **exact match** on both.

**Exemplar 2 — Scantastic `task6` chain** (the same 4-dispatch chain used
for X6 above), parent `.../19-38-19-019fa16f-feab.../`. Hand count:
`dispatch_count=4` (no implementer entry precedes it under this prefix —
tier-1's "don't drop the first entry if it's already review-shaped" rule
correctly keeps all 4), `rounds=4` (all 4 have a final-answer message).
`tokens_est`: all 4 dispatches show `fork_turns="all"` (hand-checked
against the raw `arguments` JSON string), so the max-not-sum convention
applies; hand max of the 4 cumulative totals above = 17467492. Scorer:
`dispatch_count=4`, `rounds=4`, `tokens_est=17467492` — **exact match**
on all three. `severity_trend="increasing"` and
`novel_finding_rate_per_round=[0.0, 0.0, 0.0, 1.0]` were spot-checked by
hand-reading (not printing) all 4 final-answer messages: the first three
report every severity label as empty/"none", the fourth carries one
substantive Minor-labeled item — consistent with the scorer's output.

**Bug found and fixed during this reconciliation (pre-commit — not a
post-hoc "known limitation" note).** The scorer's first design grouped
review chains purely by `task_name` containing "review", stemmed by a
guessed trailing round-number suffix. Reconciling against the real
`task4` chain showed this design finds only 4 of the 20 real rounds
(`review_a/b`, `rereview_a/b` contain "review"; `final`/`last`/
`terminal`/`quality`/`qualityfix`/`py313`/`noring`/`veto` do not, and are
project-specific words no keyword list could enumerate in advance).
Redesigned to the two-tier `_chain_key()` now in the module (a
`task<N>`-prefixed name groups by that numeric id, with the
chronologically-first entry presumed the implementer and excluded unless
it is itself review-shaped; anything else falls back to the original
review-substring + stem grouping) — re-validated against both exemplars
above with exact matches. A second, smaller gap was found in the same
pass: `_extract_findings()`'s two calibrated formats (this repo's
`task-reviewer-prompt.md` headings and `re-review-prompt.md` inline tags)
matched zero findings on the real `task6` reports, which use a third,
uncalibrated shape — a compact one-line `"Critical: none. Minor: <value>."`
summary with no heading or bullet markup. Added `_bare_label_findings()`
to recognize it (a `none`/`none.` value is correctly zero findings, not
a finding to count). Both fixes are TDD'd (`test_bare_label_format_*`,
`test_two_chains_found_implementer_excluded`, etc.) against synthetic
fixtures, not the real corpus. Documented as an ongoing, honest
limitation in the module docstring: `_extract_findings()` is a
calibrated heuristic over three observed real formats, not a guarantee
of full recall — free-form prose findings with no structural marker at
all remain invisible to it, and a *fourth* real pattern was also found
during this reconciliation (a repeatedly-re-tasked single reviewer via
`NEW_TASK`/`MESSAGE` inter-agent envelopes rather than fresh
`spawn_agent` calls per round — the `fp_task7_review` session named in
`local-host-report.md`) that this MINE-tier scorer does not detect at
all, since it has no fresh spawn per round to key off of. Out of scope
for this task; flagged for whoever extends X1 next.

### tokens_est / total_tokens convention (per this task's explicit constraint)

Both `score_x1_chains.tokens_est` and `score_x6_floor.total_tokens` read
a rollout's cumulative `token_count` counter (confirmed monotonically
increasing within one file against multiple real rollouts during this
validation) and never present it as exclusive per-turn spend. X6 scores
one dispatch = one rollout, so "last cumulative value" is simply that
dispatch's total cost, safe by construction. X1 scores a multi-round
chain spanning multiple rollout files; summing each round's cumulative
counter would double-count whenever a round inherited a prior round's
history on fork (confirmed happening in both real exemplars above — all
`task4`/`task6` review dispatches use `fork_turns="all"`), so
`tokens_est` takes the MAX single-round cumulative total across the
chain instead of the sum whenever any round shows inheritance — a
documented, deliberately conservative floor (see score_x1_chains.py's
module docstring for the full rationale).

### Test suite

`python3 -m pytest campaigns/ -q`: 341 passed before this task, 377
passed after (36 new: 24 X1 + 6 X4 + 6 X6). The pre-existing
codex-efficiency suite (341) is unchanged and stayed green throughout.

**Privacy sweep:** the standing needle set from Task 1's report (the
mining codenames and ticket-ID pattern), case-insensitive, run against
this entry and the staged diff before commit, filtered of the scrubbed
remote-host placeholders — no match, clean. Nothing from
`_tmp/cost-pathologies-2026-07-31/` was committed; the rollout paths and
task_names cited above point to the user's own local `~/.codex/sessions`
tree and are the same class of citable provenance label DESIGN.md and
rollout_parser.py already use.

## 2026-07-31 — Task 4: X1 MICRO pre-registration — reviewer-arm calibration

Pre-registered BEFORE running (per the standing rule). This is the
MICRO tier of X1's three-tier plan (MINE done in Task 2 → **MICRO,
here** → FULL). Purpose: prune X1's review-policy arms before the FULL
battery — at most 2 + control advance, per the design doc's X1 section.

### Variants and arm SHAs

All four variants review the SAME fixed diff. Each treatment arm's
reviewer-facing text is quoted VERBATIM from its branch in
`/Users/jesse/git/superpowers/superpowers` (never pushed/merged/PR'd —
local experiment apparatus only) and byte-verified against the branch
before this entry was written (`raw_X == extracted_template.txt` for
each of D/A/C; `B_FLOOR_TEXT == git show`'d SKILL.md lines, both exact
matches, checked programmatically, not by eye):

- **D-control**: the base `task-reviewer-prompt.md` template, unmodified,
  at `codex-efficiency-fixes` = `329b8f1` (arm-manifest.md: "Controls are
  the unpatched base (329b8f1): X1-D...").
- **A-criterion-backing**: D + the verbatim paragraph `cp/x1a` @
  `1851307` inserts into the Calibration section ("A finding is Critical
  or Important only when you can back it: name the requirement line it
  violates ... or name a concrete failure path a caller can reach ...").
- **B-rising-floor**: `cp/x1b` @ `151b2e1` touches only `SKILL.md` (a
  controller-side mechanism) — `task-reviewer-prompt.md` is byte-identical
  to the control on this branch. There is no multi-round loop to replay
  in a single-shot MICRO, so the reviewer is told it is round 3 of the
  fix loop (the floor's maximally-discriminating case — rounds 1-2 are
  behaviorally identical to control) and given SKILL.md's "The floor
  rises each round" paragraph verbatim as context. The scorer then
  derives round-3 blocking mechanically (Critical only) from the
  reviewer's own self-reported severities — no invented reviewer-facing
  output field. **This is a disclosed modeling choice, not a literal
  replay of the real dispatch** — B's mechanism is fundamentally
  controller-side, and the MICRO can only probe whether knowing the
  floor context changes the reviewer's calibration/behavior.
- **C-marginal-value**: D + the verbatim "**Another round worth it:**
  [Yes | No] — would one more fix-and-review round materially reduce the
  risk this task carries? ..." field `cp/x1c` @ `69fd769` appends to the
  Output Format's Assessment section.

### Fixture

`campaigns/cost-pathologies/fixtures/x1-fixed-diff/`: a synthetic
182-line diff (one coherent feature, 3 source files + 1 test file: an
order-discount + append-only-ledger service) implementing a 5-requirement
brief (`brief.md`, REQ-1..REQ-5), with an implementer report
(`task-report.md`) and a seeded-defect answer key (`ledger.md`, never
shown to the reviewer) of 5 real defects at graded severity:

- **D1 (Critical)**: `ledger.py`'s `_write` opens the ledger file in `"w"`
  mode (truncating) before `json.dump` — an interrupted/failing write
  destroys every prior transaction. Violates REQ-4 (durability). Confirmed
  by direct repro (a simulated `json.dump` failure leaves the file empty).
- **D2 (Critical)**: `discount.py`'s `DISCOUNT_CODES[code]` lookup is an
  unguarded dict subscript — an unknown/expired code raises `KeyError`
  uncaught through `process_order`/`process_batch`. Violates REQ-1.
  Confirmed by direct repro.
- **D3 (Important)**: the minimum-charge floor in `service.py` is checked
  against the pre-discount subtotal, not the post-discount charged
  amount, contradicting REQ-5's explicit text. Confirmed by direct repro
  (a $5 subtotal with 90%-off charges $0.50 and is not rejected).
- **D4 (Important)**: REQ-3's idempotency requirement is implemented
  correctly but has zero test coverage — no test in the diff calls
  `process_order` twice with the same `order_id`.
- **D5 (Minor)**: `get_discount_percent` returns a fraction, not a
  percent — a naming/readability issue with no correctness impact.

Everything in the fixture (names, amounts, service, requirements) is
invented for this eval; no real system or data.

### Run parameters

5 reps per variant (20 calls total), `claude-opus-4-8` via the Messages
API directly (`campaigns/cost-pathologies/x1-review-micro.py`), cached
per `(variant, rep)` under `out/x1-review-micro/answers/` (gitignored —
raw answer files never committed). `ANTHROPIC_API_KEY` sourced from
`/Users/jesse/git/superpowers/superpowers/evals/.env` into the process
environment only for the run; never printed, logged, or committed.

### Metrics (exact mechanical definitions — see the script's docstring
for the same text, kept in sync)

- **real_defect_recall**: of D1..D5, the fraction named ANYWHERE in the
  reviewer's Critical/Important/Minor sections (a per-defect regex
  signature in `ledger.md`), regardless of which bucket. Blocking status
  does not gate recall — a defect mentioned as Minor still counts as
  found.
- **false_block_rate**: of the findings placed in the Critical or
  Important buckets (the "blocking" set — defined UNIFORMLY across all
  four arms; an arm's own mechanism changes whether a block is
  legitimate, not what counts as a block, so the four arms are graded on
  the same scale), the fraction that (a) match no D1..D5 signature AND
  (b) are not "criterion-backed" — a real `REQ-N` (1-5) citation, or a
  `file:line` reference paired with reachability language ("reach",
  "trigger", "caller", "calling", "invoke"). **Disclosed limitation**:
  this is a generous mechanical proxy — it credits any citation of a
  REAL requirement number without verifying the citation actually
  applies to that finding. Any false-block-rate difference the prune
  decision leans on gets a manual spot-check of the flagged findings
  before it's trusted (not blind regex trust), same as this campaign's
  other scorer validations.
- **false_stop_rate**: whether the arm's derived stop signal claims
  "done" on this dirty, never-fixed diff (D1/D2 are Critical-shaped and,
  by construction, never resolved in this single-shot design). Per arm:
  D and A use `**Task quality:** Approved`; B uses "zero items in the
  Critical bucket" (the round-3 floor); C uses `**Another round worth
  it:** No`. **Deliberate reframing of the brief's "state once the
  ledger is exhausted" phrasing**: the 20-call budget (5 reps × 4 arms)
  cannot afford a matched clean-diff/dirty-diff pair, so this measures
  only the harm-relevant direction — false stops, which hide real bugs —
  not false continues, which merely cost one extra round. Since the
  fixture's ledger is never exhausted here, the mechanically honest
  answer is always "not done"; ANY stop signal in a rep is therefore a
  false stop. An arm that never stops here is unfalsifiable on
  *honest*-stop calibration by this MICRO alone — that gap is explicitly
  NOT claimed as tested and is left to the FULL battery (which runs a
  real multi-round loop to a real terminal state).

### Prune rule (pre-registered, mechanical)

An arm advances only if BOTH hold, vs. D-control's means:
1. **Strictly better on false_block_rate** — arm's mean
   `false_block_rate` < D's mean `false_block_rate`.
2. **No material recall loss** — arm's mean `real_defect_recall` ≥ D's
   mean `real_defect_recall` − 0.2 (0.2 = 1 of 5 ledger defects; "no
   recall loss greater than 1 ledger defect" per the design doc).

At most 2 arms advance (plus control, which always advances as the
baseline for FULL). If more than 2 qualify, the two with the LARGEST
false-block-rate improvement over control advance. Ties break toward the
simpler mechanism, ranked by what the mechanism requires outside the
reviewer's own single-shot judgment: **A** (purely textual calibration
guidance, no external state) is simplest, **C** (adds one self-reported
output field, still single-shot) is next, **B** (requires the controller
to track and communicate a round number — genuinely multi-round
infrastructure, unlike A/C) is least simple.

If NO arm beats control on false_block_rate without the recall guard
failing, that is a valid, honest outcome: it gets recorded as-is and the
verdict entry says whether X1 FULL should proceed control-only pending
further design work, rather than force-advancing an arm that didn't
clear its own bar.

### Budget estimate

~$15-20 for the MICRO run (20 opus-4-8 calls; each prompt is
~1,600-1,900 words of system instructions + ~1,900 words of inlined
brief/report/diff, generating a structured multi-section review — actual
cost recorded in the verdict entry's budget ledger row).

**Independent verification**: `x1-review-verify.py`, a second parser
written from scratch with a line-based state machine (no shared code or
imports with `x1-review-micro.py`'s DOTALL-regex section extraction),
re-derives every rep's counts from the cached answer files and flags any
disagreement for manual reconciliation before the verdict is written.

Privacy sweep run on this entry before commit (standing needle set,
filtered of scrubbed remote-host placeholders): no match, clean — this
entire task is a synthetic fixture with no real session content.

## 2026-07-31 — Task 4 VERDICT: X1 MICRO — reviewer-arm calibration

Ran the pre-registered battery: 20 calls (4 variants × 5 reps),
`claude-opus-4-8`, cached under `out/x1-review-micro/` (gitignored, not
committed). Two scorer bugs were found and fixed during manual
reconciliation (below) — the reported table is post-fix, re-scored from
the same cached answer files at zero additional API cost.

### Results

| variant | recall | false-block | false-stop | n |
|---|---:|---:|---:|---:|
| D-control | 76% | 0% | 0% | 5 |
| A-criterion-backing | 76% | 4% | 0% | 5 |
| B-rising-floor | 68% | 0% | 0% | 5 |
| C-marginal-value | 72% | 0% | 0% | 5 |

Per-defect recall (count out of 5 reps each arm found it, anywhere in
the report):

| defect | severity | D | A | B | C |
|---|---|---:|---:|---:|---:|
| D1 non-atomic write | Critical | 5 | 5 | 4 | 5 |
| D2 unhandled KeyError | Critical | 5 | 5 | 5 | 5 |
| D3 min-charge pre-discount | Important | 5 | 5 | 5 | 5 |
| D4 idempotency untested | Important | 4 | 4 | 3 | 3 |
| D5 misleading name | Minor | 0 | 0 | 0 | 0 |

### Prune decision: NO ARM ADVANCES — control-only per the strict rule

Pre-registered rule: an arm advances only if (1) strictly better than
control on `false_block_rate` (arm's mean < control's mean) AND (2) no
recall loss greater than 1 ledger defect (arm's mean recall ≥ control's
− 0.2). Applied literally:

- **A**: false-block 4% is worse than control's 0% (control already at
  the floor — A's addition introduced the only illegitimate escalation
  in the whole battery). **Fails (1).**
- **B**: false-block 0% ties control's 0% — not *strictly* better.
  **Fails (1)** (recall 68% vs 76% would pass the −0.2 guard on its
  own, moot given (1) fails).
- **C**: false-block 0% ties control's 0% — not *strictly* better.
  **Fails (1)** (recall 72% vs 76% would also pass the guard).

Per the pre-registration's explicit contingency: **this is a valid,
honest negative outcome, not a scoring failure.** No arm is force-
advanced. Reporting BLOCKED-equivalent status: **X1 FULL should proceed
control-only pending further design work**, or the controller can
decide to loosen the tie-break (0% vs 0% counted as "not worse" rather
than "not strictly better") and admit B and C on that relaxed reading —
that is a controller call this task does not make unilaterally.

### The diagnostic finding: a ceiling-effect fixture, not calibrated arms

The more useful result is *why* nothing won. D-control already scores a
**perfect 0% false-block and 0% false-stop** on this fixture — both
metrics are pinned at their floor before any arm's mechanism gets a
chance to show improvement. Two seeded Critical defects (data loss,
unhandled crash) are severe and unambiguous enough that Opus 4.8 never
fabricated an illegitimate block against clean code, and never
signalled "done" while they sat unfixed, **under any of the four
prompts**. The MICRO's false-block and false-stop axes were built to
catch premature convergence and fabricated severity — this fixture
never gave any arm the opportunity to fail either way. A false-block
axis with a control at the floor cannot discriminate treatment arms; it
can only make a treatment arm look worse (which is exactly what
happened to A). **This is a fixture-design finding for whoever designs
X1 FULL**, not evidence the mechanisms don't work: a MICRO with more
borderline/gray-area content (a defensible-but-debatable design choice,
a Critical-adjacent-but-arguably-Important call) is needed to actually
stress false-block calibration.

The one real signal: **A's own text (require a citable requirement or
concrete failure path) did not stop the model from filing an unbacked
style nitpick as an Important finding** — manually inspected
(`A-criterion-backing-r0.txt`): *"hand-rolled try/except/`assert False`
instead of `pytest.raises`... Minor mechanically, but flagged because
the current tests give false confidence..."* — the model's own words
call it Minor, then files it under Important anyway. This is a genuine,
if small, instance of the exact miscalibration X1-A is meant to
prevent, caught by a human-manual read, not just the regex.

B's mild recall dip (D1 4/5, D4 3/5 vs 5/5 and 4/5 for control) is
plausibly noise at n=5 (one rep short by exactly one defect each,
twice) — not treated as a finding, flagged for a larger FULL sample if
B is revisited.

D5 (the seeded Minor defect, a misleading function name) was **never
recalled by any arm across all 20 reps** — a uniform floor effect on
the fixture's own weakest-severity defect, not an arm difference.

### Bugs found and fixed during manual reconciliation (pre-commit)

Independent verification (`x1-review-verify.py`, a from-scratch
line-based state machine, no shared code with the main scorer) flagged
2 of 20 reps as mismatched against the main scorer's first-pass output.
Manually reading both:

1. **Main-scorer bug (real, fixed)**: `split_findings()`'s empty-
   section check (`^\**none\b`) didn't match B-arm-style parenthetical
   floor-deferral markers — `B-rising-floor-r1.txt`'s Important bucket
   contained only `(none above the round-3 floor — deferred items
   below)`, which the splitter treated as one real finding, inflating
   that rep's false-block count by 1 (the null-marker matched no ledger
   defect and cited nothing, so it scored as a false block). Fixed:
   `re.match(r"^\(?\**\s*none\b", ...)`. This changed B's reported
   `false_block_rate` from 5% to 0% (the number in the table above is
   post-fix). Verified the fix does NOT swallow real findings that
   happen to start with a similar prefix — `B-rising-floor-r2.txt` and
   `-r4.txt` both have substantive Important-bucket items prefixed
   `"(Deferred — below the round 3 floor.) Tests assert real
   behavior..."`, which still parse as real findings (they don't match
   `^\(?\**\s*none\b`, which requires "none" specifically, not
   "Deferred").
2. **Verifier-only bug (fixed, never affected the reported table)**:
   the independent verifier's own D4/D5 needle lists were too loose
   (`"get_discount_percent"` alone, `"no test for"` alone) and
   over-credited `D-control-r3` to a false 1.0 recall against the main
   scorer's correct 0.6. Manually read `D-control-r3.txt`: it genuinely
   does not flag D4 (says idempotency "✅... correctly implemented,"
   no coverage-gap finding) or D5 — the main scorer's 0.6 was right.
   Tightened both needle lists to require co-occurrence (e.g.
   `"no test for idempot"`, `"get_discount_percent.*misleading"`).

Post-fix, `x1-review-verify.py` reports **zero mismatches** against the
final `results.json` across all 20 reps.

### Cost

No token usage was logged during the run (the script discarded
`usage` from each response — a gap for any future rerun of this
script). Reconstructed from cached prompt/answer text: ≈82,050 input
tokens (4,013–4,192 per call depending on variant, ×5 reps) and
≈21,730 output tokens (measured from the 20 cached answer files,
87,542 chars ÷ 4) at `claude-opus-4-8` pricing ($5/$25 per MTok,
thinking never enabled — this call never set `thinking`, and Opus 4.8
runs thinking-off by default when it's omitted, so the cached answer
text is the full billed output with nothing hidden). **≈$0.95 total** —
well under the $15-20 pre-registered estimate (the fixture's diff and
brief turned out shorter in tokens than the estimate's word-count
assumed) and far under the $580 campaign ceiling. Budget ledger row
below.

### Privacy sweep

Standard needle set + `ANTHROPIC_API_KEY` pattern grep, run against
this entry and the staged diff before commit: no match, clean. The key
was sourced into the process environment for the run only, never
printed, logged, or committed; raw answer files live under the
gitignored `out/x1-review-micro/` and were not staged.

| Date | Battery | $ cost | Notes |
|---|---|---|---|
| 2026-07-31 | X1 MICRO (reviewer-arm calibration, 20 calls) | ~$0.95 | No arm strictly beat control's 0% false-block floor; BLOCKED-equivalent, X1 FULL control-only pending redesign |
