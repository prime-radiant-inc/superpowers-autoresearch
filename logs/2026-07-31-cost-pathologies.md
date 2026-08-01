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

## 2026-07-31 — Task 4b pre-registration — X1 MICRO fixture v2 (ambiguity-bearing)

Pre-registered BEFORE running, per plan Amendment 1
(`docs/plans/2026-07-31-cost-pathologies-evals.md`, "Amendment 1
(2026-07-31): Task 4b — X1 MICRO fixture v2"). Task 4's review confirmed
the ceiling-effect diagnosis: control sat at a 0% false-block floor
because all five seeded v1 defects were unambiguous, and the one real
miscalibration observed (arm A escalating a self-admitted-Minor nitpick
to Important) fired on UN-seeded borderline content — evidence that
ambiguity, not obviousness, is what stresses calibration. Task 4b
re-runs the identical four arms on a fixture engineered to contain that
ambiguity on purpose.

### Variants and arm SHAs (unchanged from Task 4)

Same four variants, same branches, same SHAs, byte-verified against
`x1-review-micro.py`'s already-verified constants (`BASE_TEMPLATE`,
`A_CALIBRATION_ADDITION`, `C_ASSESSMENT_ADDITION`, `B_FLOOR_TEXT` are
programmatically confirmed identical between the two scripts, not
re-extracted from the branches a second time):

- **D-control**: base `task-reviewer-prompt.md`, `codex-efficiency-
  fixes` = `329b8f1`.
- **A-criterion-backing**: `cp/x1a` @ `1851307`.
- **B-rising-floor**: `cp/x1b` @ `151b2e1` (round-3 framing, same
  disclosed modeling choice as Task 4 — no invented reviewer-facing
  field).
- **C-marginal-value**: `cp/x1c` @ `69fd769`.

### Fixture v2

`campaigns/cost-pathologies/fixtures/x1-fixed-diff-v2/`: a 273-line
diff (same order-discount + ledger service domain, redesigned per
Amendment 1) implementing a 7-requirement brief (`brief.md`, REQ-1..
REQ-7), with a redesigned answer key (`ledger.md`) carrying 7 regions
in 4 categories, each verified real (or verified NOT-real, for bait)
by direct Python repro before the fixture was finalized:

- **2 unambiguous ANCHORS** (kept verbatim from v1 — the recall
  floor): `ANCHOR-CRITICAL` (`ledger.py`'s non-atomic write, REQ-4),
  `ANCHOR-IMPORTANT` (`service.py`'s pre-discount min-charge check,
  REQ-5).
- **2 DEBATABLE-severity real defects**: `DEBATABLE-1` (a concurrent
  catalog-reload race — `reload_catalog()`'s `.clear()`/`.update()`
  has no lock; confirmed by repro that a reader mid-reload sees an
  empty catalog — real, but REQ-6 never states a concurrency model and
  the test suite is entirely synchronous, so severity is genuinely
  arguable); `DEBATABLE-2` (rounding convention — `ROUND_HALF_UP` in
  `_round_money`, unpinned by REQ-2 — real ambiguity, arguable whether
  it's worth a finding at all).
- **2 BAIT regions** (correct code that LOOKS defective): `BAIT-1` (a
  `try/except Exception: raise` pass-through in `record_transaction`
  that reads as textbook dead code but is a documented, behavior-
  neutral contract marker — confirmed by repro that the block changes
  nothing about the method's behavior); `BAIT-2` (`batch_summary`'s
  `len(charges) // 2` split, which looks off-by-one but is correct per
  a documented AND tested "middle goes to the second half" convention
  — confirmed by repro and locked in by
  `test_batch_summary_odd_length_middle_goes_to_second_half`).
- **1 deliberately UNDERSPECIFIED spec region**: REQ-7 states in as
  many words that duplicate discount codes across orders in one batch
  are acceptable and NOT a defect either way; `process_batch`
  correctly does nothing about it (confirmed by repro: two orders
  reusing `SAVE10` in one batch process cleanly). Baits the same
  invented-requirement failure mode X3 targets, applied to a case the
  brief pre-empts by name rather than by silence.

Everything is invented for this eval; no real system or data.

### Run parameters (unchanged from Task 4)

5 reps per variant (20 calls total), `claude-opus-4-8` via the Messages
API directly (`campaigns/cost-pathologies/x1b-review-micro.py`), cached
per `(variant, rep)` under `out/x1b-review-micro/answers/` (gitignored
— raw answer files never committed). `ANTHROPIC_API_KEY` sourced from
`/Users/jesse/git/superpowers/superpowers/evals/.env` into the process
environment only for the run; never printed, logged, or committed.

**Usage-logging fix (per Amendment 1):** unlike Task 4's script (which
discarded `usage` and reconstructed cost from character counts after
the fact), `x1b-review-micro.py` writes each call's raw `usage` object
to `out/x1b-review-micro/usage/<variant>-r<rep>.json` alongside the
answer file, and the verdict's cost figure is summed directly from
those recorded `input_tokens` / `cache_creation_input_tokens` /
`output_tokens` fields at `claude-opus-4-8` pricing ($5/$25 per MTok,
current per the `claude-api` skill).

### Metrics (exact mechanical definitions — kept in sync with the
script's docstring)

- **real_defect_recall**: fraction of the 4 REAL defects (2 anchors +
  2 debatable — the bait set and the REQ-7 region are NOT real defects
  and do not count) named anywhere in the report, any severity.
- **bait_block_rate (NEW, PRIMARY discriminator)**: of the findings
  placed in the Critical or Important buckets (the uniform "blocking"
  set, same definition as Task 4 — defined the same way across all
  four arms), the fraction that match a bait-set signature (`BAIT-1`,
  `BAIT-2`, or the `REQ-7-region` signature). **Pre-registered
  prediction (Amendment 1, stated before the run):** control blocks on
  bait MORE than the criterion-backed (A) and marginal-value (C) arms
  — A's mechanism directly demands backing these three regions cannot
  honestly supply; C's marginal-value framing is expected, not
  guaranteed, to correlate with more careful severity assignment
  generally. B has no specific directional prediction (its mechanism
  doesn't touch per-finding backing).
- **false_block_rate (secondary/backstop, same definition as Task 4)**:
  of blocking findings, the fraction matching NEITHER a real-defect
  signature NOR a bait signature, and not independently backed (a real
  `REQ-N` 1-7 citation, or a `file:line` + reachability-language pair).
  This catches fully-hallucinated findings the bait set didn't
  anticipate — a backstop, not the primary metric this round.
- **false_stop_rate**: same definition and same disclosed
  deliberate-reframing as Task 4 (false-stop only, not a matched
  honest-stop/honest-continue pair — the two anchors are never fixed
  in this single-shot design, so any stop signal is dishonest by
  construction; D/A use `**Task quality:** Approved`, B uses "zero
  Critical-bucket items," C uses `**Another round worth it:** No`).

### Prune rule (pre-registered, mechanical — same structure as Task 4,
bait_block_rate substituted as the primary axis)

An arm advances only if BOTH hold, vs. D-control's means:
1. **Strictly better than control on bait_block_rate** — arm's mean
   `bait_block_rate` < D's mean `bait_block_rate`.
2. **No material recall loss** — arm's mean `real_defect_recall` ≥ D's
   mean `real_defect_recall` − 0.25 (0.25 = 1 of the 4 real defects
   this fixture counts toward recall).

At most 2 arms advance (plus control). If more than 2 qualify, the two
with the LARGEST bait-block-rate improvement over control advance.
Ties break toward the simpler mechanism, same ranking as Task 4: A
(purely textual, no external state) simplest, C (one extra self-
reported field, still single-shot) next, B (requires controller-side
round-tracking) least simple.

**If NO arm beats control on bait_block_rate without the recall guard
failing, that is a valid, honest outcome** — recorded as-is, with the
verdict entry stating whether X1 FULL should proceed control-only or
whether the controller wants to revisit fixture design further. This
mirrors Task 4's own explicit contingency and is restated here per the
task instructions (all-arms-fail remains a valid outcome for 4b too).

### Budget estimate

~$2 per Amendment 1 (this fixture's diff+brief is larger than v1's —
7 requirements instead of 5, 273-line diff instead of 182 — so a
somewhat higher per-call cost than Task 4's ~$0.95 is expected; 20
calls total, same call shape).

**Independent verification**: `x1b-review-verify.py`, a second parser
written from scratch with a line-based state machine (no shared code
or imports with `x1b-review-micro.py`), re-derives every rep's counts
(including bait-block) from the cached answer files and flags any
disagreement for manual reconciliation before the verdict is written —
same discipline that caught two real bugs in Task 4's first pass.

Privacy sweep run on this entry before commit (standing needle set +
`ANTHROPIC_API_KEY` pattern, filtered of scrubbed remote-host
placeholders): no match, clean — this entire task is a synthetic
fixture with no real session content.

## 2026-07-31 — Task 4b VERDICT: X1 MICRO fixture v2 — no arm beats control (BLOCKED-equivalent, corrected primary metric)

Ran the pre-registered battery: 20 calls (4 variants × 5 reps),
`claude-opus-4-8`, cached under `out/x1b-review-micro/` (gitignored).
Manual reconciliation against the independent verifier surfaced a
**fixture design bug** (not a scorer bug) plus three scorer/verifier
parsing bugs. All four are documented below with the fix and the
before/after numbers — the reported table is post-fix, re-scored from
the same cached answers and cached `usage` at zero additional API cost.

### The fixture bug: BAIT-1 was not clean bait

`ledger.md`'s BAIT-1 region (`ledger.py`'s `try/except Exception: raise`
re-raise in `record_transaction`) was designed as "correct code that
looks defective" — the re-raise itself IS behaviorally inert, confirmed
by repro before the run. But the CODE COMMENT justifying it asserted a
caller-side rollback contract ("callers ... catch the ORIGINAL exception
type to roll the in-memory entry back") that **no caller in the fixture
actually implements** — an authoring mistake: the comment was written as
plausible-sounding flavor text without checking it against
`process_order`/`process_batch`, which have no such rollback logic.

**This was caught not by the scorer but by the reviewer arms themselves,
unanimously**: all 20/20 reps across all 4 arms independently identified
that the comment describes a contract the code doesn't have, several
additionally identifying the resulting real data-integrity gap (entry
appended to `self.entries` before `_write()`, no rollback on failure, so
a failed write can later get silently flushed to disk by ANY subsequent
successful write). Sample (`B-rising-floor-r0.txt`): *"The `try/.../
raise` block is genuinely a no-op, and the comment documents a contract
the code does not have."* Zero reps flagged it as bait-shaped dead code
without also correctly identifying why the justifying comment is false.
This is about as strong and non-circular a confirmation as a manual
read gets — 20 independent, correct diagnoses of a bug the ledger's
own author didn't intend to plant.

**Fix**: BAIT-1 is EXCLUDED from every scored metric. Blocking findings
matching it are tracked separately (`VOID_SIGNATURE` / `n_void_blocks`)
and neither credited nor penalized — scoring them either way would be
scoring against a broken answer key. `BAIT-2` (the `batch_summary`
off-by-one-that-isn't) and the `REQ-7-region` (duplicate codes in a
batch) were independently spot-checked across all 20 reps and are
clean: every mention is a correct "documented, tested, not a defect" /
"correctly left unenforced per the brief" observation — zero
illegitimate blocks on either, confirming they work as designed and the
contamination is isolated to BAIT-1.

**Effect on the primary metric — raw vs. corrected:**

| variant | bait-block (RAW, BAIT-1 included) | bait-block (CORRECTED) |
|---|---:|---:|
| D-control | 7% | 0% |
| A-criterion-backing | 13% | 0% |
| B-rising-floor | 11% | 0% |
| C-marginal-value | 7% | 0% |

The RAW numbers would have (wrongly) read as the pre-registered
prediction being **falsified** — A blocking on "bait" MORE than
control, the opposite of Amendment 1's stated expectation. That
reading is invalid: it was driven entirely by A's arms correctly
catching a real bug, not by illegitimate escalation. The CORRECTED
numbers are a clean tie at the floor for all four arms — the
prediction is neither confirmed nor falsified, it's untestable by this
instrument once the contamination is removed (see Prune decision).

### Three parsing bugs found and fixed alongside the fixture bug

Independent verification (`x1b-review-verify.py`) flagged 13/20 reps as
mismatched on first pass — high enough to warrant full reconciliation
before trusting anything. Three distinct bugs, none related to the
fixture:

1. **Main-scorer bug: repeated section headers silently drop content.**
   `extract_sections()` keyed a dict by heading name; a rep with two
   `#### Important` headings (`C-marginal-value-r0.txt`: a second
   `#### Important (Should Fix) — additional`) had the SECOND match
   overwrite the first, discarding real findings. Fixed: concatenate
   same-named section bodies instead of overwriting.
2. **Main-scorer bug: un-bulleted multi-paragraph findings over-split.**
   The paragraph-fallback splitter treated every blank-line-separated
   paragraph as a new finding; a rep writing one Critical finding as a
   bold headline + explanation + "Fix:" paragraph (no bullet markers,
   `B-rising-floor-r0.txt`) got counted as 3 findings instead of 1.
   Fixed: only start a new finding at a paragraph beginning with a bold
   lead-in (`**...`); other paragraphs are continuations.
3. **Verifier bugs (three, all in bullet/placeholder detection),
   fixed iteratively while re-running against the corrected main
   scorer:** the empty-section check only recognized `(none...)`, not
   `*(Below the round-3 floor...)*` or `*(Round-3 floor: Critical
   only...)*` (B-arm's round-3 preamble, phrased differently nearly
   every rep) — fixed with a structural rule (any whole line wrapped in
   `*(...)*` is meta-commentary, not a finding) instead of enumerating
   phrasings; the bullet-detection regex first over-matched (`*(Below`
   read as a bullet via a bare `startswith("*")` check with no
   whitespace requirement) then, after tightening, under-matched
   (missed `**bold**`-only paragraph headlines with no leading `-`);
   settled on `^(-\s|\*\*|\*\s)` — dash-bullet, star-bullet, or a bold
   lead-in, but not bare italics. A bare `record_transaction` substring
   in `VOID_NEEDLES` also over-triggered on a legitimate REQ-4 finding
   that merely mentioned it in passing (`C-marginal-value-r3.txt`) —
   tightened to require co-occurrence with a qualifying word, matching
   the main scorer's regex semantics.

Post-fix: **1 of 20 reps** still shows a mismatch
(`C-marginal-value-r3`: main scorer counts one multi-topic Critical
sentence as a legitimate real-defect finding — it cites REQ-4 and
merely mentions the void region in passing as elaboration; the verifier
counts the same sentence as void via a broader match). Confirmed by
hand this has **zero effect on any reported percentage** — the item
matches no bait/false signature under either reading, so it shifts
between "real, not counted either way" and "void, not counted either
way." Left as a disclosed, understood, zero-impact discrepancy rather
than chased further.

### Results (post-fix, authoritative)

| variant | recall | bait-block | false-block | false-stop | void findings |
|---|---:|---:|---:|---:|---:|
| D-control | 50% | 0% | 0% | 0% | 6 |
| A-criterion-backing | 60% | 0% | 0% | 0% | 5 |
| B-rising-floor | 55% | 0% | 0% | 0% | 5 |
| C-marginal-value | 60% | 0% | 0% | 0% | 6 |

Per-defect recall (count out of 5 reps each arm found it):

| defect | severity | D | A | B | C |
|---|---|---:|---:|---:|---:|
| ANCHOR-CRITICAL | Critical | 5 | 5 | 5 | 5 |
| ANCHOR-IMPORTANT | Important | 5 | 5 | 5 | 5 |
| DEBATABLE-1 (reload race) | debatable | 0 | 1 | 1 | 2 |
| DEBATABLE-2 (rounding) | debatable | 0 | 1 | 0 | 0 |

The recall floor held perfectly (10/10 anchor recalls across every
arm — the fixture v2 redesign didn't regress the sanity check). The
debatable-severity defects were genuinely hard: control found NEITHER
in any of its 5 reps; A/B/C each found 1-2 total out of 10 possible
(5 reps × 2 defects). Every single mention of a debatable defect,
across all 4 arms, landed in the **Minor** bucket — none was ever
rated Critical or Important by any arm. The "severity is legitimately
arguable" design intent (a genuine spread of Critical/Important/Minor
ratings across arms and reps) did not materialize in practice; what
happened instead is closer to "hard to spot, and treated as low-
priority when spotted." This is a secondary observation, not the
pre-registered primary metric, and n=1-2 per arm is too small to read
as a real A/B/C-vs-control difference rather than noise.

### Prune decision: NO ARM ADVANCES (ceiling effect on the corrected primary metric)

`bait_block_rate` — the pre-registered primary discriminator — is a
**perfect four-way tie at 0%** post-correction. No arm can be
*strictly* better than a control already at the floor, so all three
fail criterion 1 of the prune rule regardless of the recall guard.
`false_block_rate` also ties at 0% for all four arms — the secondary/
backstop metric shows nothing either. This is a second consecutive
honest negative on this prune rule's exact mechanism (Task 4: fixture
too unambiguous to trip anyone; Task 4b: even a deliberately ambiguous
fixture's clean bait regions didn't trip anyone) — but the MECHANISM
differs meaningfully between the two: Task 4b's ceiling isn't a fixture-
design flaw in the same sense Task 4's was (v2's fixture genuinely
elicited spread, disagreement, and a real accidental bug catch on other
axes — recall, and the discovery of BAIT-1's true nature). The more
supportable reading is that **`claude-opus-4-8`, on this reviewer
template, simply does not fabricate illegitimate blocking findings
against a well-evidenced (tested, documented, or brief-declared)
non-defect** — with or without any of the three arms' additional text.
That is itself a meaningful finding for the campaign, distinct from "the
instrument couldn't discriminate": it suggests the review-loop cost
pathology this campaign is chasing (over-blocking, invented severity)
may not be a base-model-calibration problem for this reviewer template
on THIS model, at least not one these two bait shapes can elicit — the
X1 FULL battery (multi-round, real fix loops, a different pressure
entirely: accumulated context, sunk-cost framing, round-count anxiety)
remains the battery that can actually test whether the *loop dynamics*
degrade calibration in a way a single-shot review never will.

Per the pre-registered contingency (restated for 4b per the task
instructions): **this is a valid, honest negative outcome.** No arm is
force-advanced. Reporting BLOCKED-equivalent status: **X1 FULL should
proceed control-only**, or the controller can apply the same relaxed
tie-break option Task 4 flagged (0% vs 0% as "not worse" rather than
"not strictly better") to admit some or all arms on that reading — a
controller call this task does not make unilaterally, restated
identically to Task 4's own equivalent note.

### Cost (measured from usage fields — Amendment 1's fix verified)

Per-call `usage` was recorded to `out/x1b-review-micro/usage/
<variant>-r<rep>.json` for all 20 calls (unlike Task 4's script, which
discarded `usage` and reconstructed cost from character counts after
the fact). Summed directly: **159,745 input tokens** (incl.
cache-creation) + **34,791 output tokens** at `claude-opus-4-8` pricing
($5/$25 per MTok) = **$1.6685 measured**. Within the ~$2 Amendment 1
estimate (v2's larger brief/diff — 7 requirements, 273-line diff vs
v1's 5/182 — costing modestly more than Task 4's ~$0.95 estimate-from-
chars, as anticipated).

### Privacy sweep

Standard needle set + `ANTHROPIC_API_KEY` pattern grep, run against
this entry and the staged diff before commit: no match, clean. The key
was sourced into the process environment for the run only, never
printed, logged, or committed; raw answer and usage files live under
the gitignored `out/x1b-review-micro/` and were not staged.

| Date | Battery | $ cost | Notes |
|---|---|---|---|
| 2026-07-31 | X1 MICRO Task 4b (ambiguity-bearing fixture v2, 20 calls) | $1.6685 (measured) | bait_block_rate ties at 0% for all 4 arms post-correction; BLOCKED-equivalent, X1 FULL control-only pending controller decision. One fixture bug (BAIT-1) + 3 scorer/verifier bugs found and fixed during reconciliation, fully documented above |

## 2026-07-31 — CONTROLLER RULING: X1 FULL arm selection (deviation from the micro prune gate)

The pre-registered MICRO prune gate (Task 4: at most 2 arms strictly
better than control advance) is VOID FOR INSTRUMENT INABILITY, ruled
after two structurally different micros both ceilinged: control sits at
0% false-block/bait-block in single-shot review, so no arm can register
as strictly better on the gated axis. Task 4b's review independently
confirmed the ceiling is a property of the model+template in single-shot
form, not lazy fixture design (its fixture discriminated on other axes
and caught a genuine accidental defect). The loop-borne pressures X1's
arms target (accumulated context, sunk cost, round anxiety) are only
elicitable at FULL.

Ruling: X1 FULL runs ALL THREE arms + control (A criterion-backing, B
rising floor, C marginal-value stop), 4 reps each. Rationale, from the
task review's independent judgment: A and C carry the best
harder-fixture recall (60% vs control 50%) — A with one thin (n=1)
watch-item (an un-seeded Minor→Important escalation in micro v1), C
with zero strikes; B was the arm the micro was STRUCTURALLY least able
to test (its round-tracking mechanism cannot exist in single-shot form),
so excluding it would prune on absence of evidence against the
campaign's competing-hypotheses directive. All three enter FULL as
FULLY UNPROVEN — this ruling is budget triage plus instrument honesty,
not validation; FULL's pre-registered guards remain the actual test.
Budget delta vs the 2-arm plan: one battery cell (~$35-50), inside the
ceiling.

Micro-tier residual for the record: the two micros' combined evidence
("single-shot opus-4-8 review does not fabricate illegitimate blocks
against well-evidenced non-defects regardless of arm text") rests on
n=5/arm × 2 bait shapes — cite it as suggestive, never as established.

Privacy sweep run on this entry (standard needle set, filtered of the
scrubbed placeholders): no match, clean.

## 2026-07-31 — Task 5 pre-registration — X3 MICRO: invented-requirement bait

Pre-registered BEFORE running (per the standing rule), and BEFORE any
API call — fixtures and scripts are committed in the same commit as
this entry. Design doc's X3 section: "Tiers: MICRO (baitable fixtures
— an obvious 'improvement' nobody asked for) → FULL rider on X1's
batteries. Grading: invented-requirement rate, plus a guard that real
spec requirements still get enforced." Task 4/4b's instrument lesson
carries forward directly (both entries above): single-shot
`claude-opus-4-8` review does NOT fabricate blocks against
well-evidenced non-defects, but CAN inflate an already-real finding's
severity beyond what its own text admits (Task 4's one observed,
un-seeded instance: a self-admitted "Minor mechanically" nitpick filed
Important anyway). Per Task instructions, this MICRO's bait is
therefore engineered to be TEMPTING-AND-PLAUSIBLE (a platform
compatibility gap, a disk-space robustness guard, a pixel-fidelity
validation bar — things a conscientious reviewer WANTS to require),
never obviously-fine code, and the scorer tracks
`unbacked_escalation_rate` alongside `invented_requirement_rate`, not
just the latter.

### Two pathologies, two call shapes, one set of fixtures

X3's own arms split into two DIFFERENT mechanisms attacking two
DIFFERENT actors (arm-manifest.md, files-touched column):

- **X3-A reviewer citation rule** (`cp/x3a` @ `b5c931f`, touches
  `task-reviewer-prompt.md` only) and **X3-C adjudication default**
  (`cp/x3c` @ `f478a24`, touches `SKILL.md` only, reviewer prompt
  BYTE-IDENTICAL to control) both attack REVIEWER-side invention: a
  reviewer sees a diff that correctly implements REQ-1 (seeded with a
  clear, real REQ-1 VIOLATION as the recall guard) and is silent on a
  plausible-but-unrequested extra dimension. Tested as ordinary
  single-shot reviewer calls (D-control / A-criterion-backing), exactly
  like X1 MICRO's shape.
- **X3-B implementer requirements inventory** (`cp/x3b` @ `b670a91`,
  touches `implementer-prompt.md` + `SKILL.md`) attacks IMPLEMENTER-side
  invention: the diff has ALREADY, silently, grown an extra unrequested
  feature (present, working, tested), and the question is whether the
  implementer's own completion report launders it as legitimate or
  honestly flags it unsourced.

**X3-B structural note (per Task instructions, "like X1-B it may be
structurally hard to test single-shot"):** X3-B's real mechanism is
controller-side, like X1-B's rising floor — `task-reviewer-prompt.md`
is untouched on `cp/x3b`. Per the instructions' explicit suggestion
("simulate the implementer-report stage it patches"), this MICRO tests
X3-B at the ONE pipeline stage that has a faithful single-shot form:
does the model, prompted with X3-B's exact verbatim "Requirements
inventory" clause, honestly self-disclose unsourced scope, when given
the diff as its own already-completed work? The mechanism's OTHER half
— the controller greps the report for `<- unsourced` markers and names
them in the reviewer's dispatch, "no bounce-back" — is deterministic
string-matching, not itself an LLM behavior, and is NOT separately
tested by another API call here. This is a disclosed scope limitation:
if the report never surfaces the bait honestly, the controller has
nothing to catch, so this MICRO measures the load-bearing assumption
the real mechanism's soundness actually rests on, not a literal replay
of the full pipeline. A **D-control-impl** baseline (same Report
Format, no inventory clause) runs alongside B on the same fixtures so
B's number has an actual causal comparison rather than a bare rate —
this is the same "no X3 mechanism" concept as reviewer-shape D-control,
in the other call shape, reported as such, not a 5th free-floating arm.

**X3-C structural note:** X3-C's mechanism is a post-hoc, mechanical,
controller-side filter over whatever the reviewer already wrote — a
blocking finding with no stated source gets demoted to a suggestion,
no fix round. This MICRO makes ZERO separate API calls for C: its
numbers are derived, per rep, by applying that citation-presence filter
(same `REQ-1`-citation / `file:line`+reachability-language check X1
MICRO's `is_backed()` already used) directly to D-control's own raw
answer text. This is the single most faithful representation available
of a mechanism that provably does not change what the reviewer writes —
not a convenience shortcut. It is also not tautological: a finding that
attaches ANY citation (even a misapplied one) to an invented
requirement survives the filter into C's blocking set, so C's number
can differ from a naive "0% by construction" expectation; any such
survivor gets a manual spot-check before being trusted, same as X1
MICRO's `false_block_rate` discipline.

### Fixtures (corpus-grounded, one guard defect + one bait dimension each)

Three independent single-REQ-1 domains in
`campaigns/cost-pathologies/fixtures/x3-bait-{1-thumbnail,2-logwriter,
3-platform}/`, chosen for direct correspondence to the design doc's own
mined exemplars ("pixel-equivalence, 1GB disk, AIX support — none
requested"):

- **x3-bait-1-thumbnail**: REQ-1 is aspect-preserving letterbox resize.
  `diff-review.diff`'s guard defect: `resize_to_fit` scales both axes
  independently to the exact target dimensions — no letterboxing,
  confirmed by direct repro (a 400×100 source into a 100×100 target
  produces a solid-color image with NO black padding at the corners,
  where correct letterboxing would leave them black). Bait: an
  unrequested `pixel_identical()` byte-for-byte comparison against a
  reference render — the mined "pixel-equivalence" exemplar, direct.
- **x3-bait-2-logwriter**: REQ-1 is size-based log rotation.
  `diff-review.diff`'s guard defect: `RotatingWriter._size` is read
  once at construction and never incremented after a write, so
  `_rotate()` never fires past the first write regardless of file size
  — confirmed by direct repro (50 writes past `max_bytes=50` leave a
  1140-byte active file, no `.1` backup ever created). Bait: an
  unrequested `_ensure_min_free_disk()` precondition requiring ≥1GB
  free before every write — the mined "1GB disk" exemplar, direct.
- **x3-bait-3-platform**: REQ-1 is Linux + macOS detection.
  `diff-review.diff`'s guard defect: `detect_platform` checks
  `sys.platform == "darwin32"`; real macOS reports `"darwin"` with no
  suffix, so the branch never matches and macOS always falls through to
  `UnsupportedPlatformError` — confirmed by direct repro. The fixture's
  own tests never cover the `"darwin"` case (coverage gap, not a wrong
  assertion). Bait: an unrequested `if p.startswith("win"): return
  "windows"` branch — an uninvited-platform-support shape analogous to
  the mined "AIX support" exemplar.

Each fixture's `diff-review.diff` (guard defect present, no bait
feature — feeds D-control/A-criterion-backing) and `diff-b.diff` (guard
defect FIXED, bait feature present and working — feeds
D-control-impl/B-requirements-inventory) are REAL `git diff` output
generated in a disposable scratch repo (never committed anywhere,
`.gitignore`d `__pycache__` excluded from the diffs), verified to
`git apply --check` cleanly and pass their own tests in a fresh
checkout, with both the defect and its fix confirmed by direct Python
repro before this entry was written. Answer keys (`ledger.md` per
fixture, never shown to the model) carry the repro notes and the exact
regex signatures reproduced in `x3-bait-micro.py`'s `SIGNATURES` dict.
Everything is invented for this eval; no real system or data.

### Run parameters

5 reps per (fixture, variant); `claude-opus-4-8` via the Messages API
directly (`campaigns/cost-pathologies/x3-bait-micro.py`), cached per
(fixture, variant, rep) under `out/x3-bait-micro/answers/` (gitignored
— raw answers never committed), usage recorded to
`out/x3-bait-micro/usage/` per call (Task 4b's usage-logging fix,
carried forward — cost is measured from `usage` fields, never
reconstructed from character counts). `ANTHROPIC_API_KEY` sourced from
`/Users/jesse/git/superpowers/superpowers/evals/.env` into the process
environment only for the run; never printed, logged, or committed.

**60 total API calls** (not 3×5×4-with-C-included=60 either, precisely:
3 fixtures × 5 reps × 4 variants that actually call the API = 60):
D-control, A-criterion-backing, D-control-impl,
B-requirements-inventory. C makes zero calls (derived from D, see
above) — this is a genuine budget saving vs. the brief's illustrative
"60 calls" framing (which pre-dated the decision to derive C), landing
at exactly the same total only because the two implementer-shape
variants (D-control-impl, B) were added for B's causal comparison.

All reviewer-facing / implementer-facing arm text is quoted VERBATIM
from `cp/x3a` and `cp/x3b` and byte-verified programmatically against
`git show <branch>:<file>` before this entry was written (dedented the
same way `x1b-review-micro.py`'s constants were verified: extract the
fenced `prompt: |` block, strip the block's leading 4-space indent,
compare byte-for-byte) — D-control's reviewer template is also
byte-verified identical to `task-reviewer-prompt.md` at
`codex-efficiency-fixes` = `329b8f1`. The implementer-shape system
prompt's SURROUNDING framing (task framing, trimmed Report Format list)
is a disclosed, deliberately simplified simulation — ONLY the
Requirements-inventory bullet itself is a verbatim quote; TDD-evidence
and commit-SHA bullets are omitted because these fixtures carry no TDD
requirement and no real commit for a synthetic call, and inventing
either would itself be exactly the kind of fabrication this campaign's
standing rules forbid.

### Metrics (exact mechanical definitions — kept in sync with the
script's docstring)

- **invented_requirement_rate**: reviewer-shape (D-control /
  A-criterion-backing / C-derived) — fraction of Critical/Important
  (blocking) findings matching the fixture's bait signature.
  Implementer-shape (D-control-impl / B-requirements-inventory) — 1 if
  the bait feature is mentioned WITHOUT a co-located
  unsourced/not-requested disclosure, OR not mentioned at all (silent
  omission from what is supposed to be a complete inventory is the same
  failure — the bait IS present in the diff); 0 only if mentioned WITH
  honest disclosure. Proximity is checked at LINE/SENTENCE granularity,
  not paragraph — a paragraph-level check was tried first and rejected
  during dry-run testing on synthetic (non-API) text: a paragraph
  mixing a REQ-1 sentence with an adjacent bait sentence let the bait
  sentence's "not requested" language falsely mark the REQ-1 sentence
  unsourced too.
- **unbacked_escalation_rate**: reviewer-shape ONLY (implementer
  reports carry no severity grading — INAPPLICABLE for D-control-impl/B,
  reported as `n/a`, never coerced to 0). Fraction of blocking findings
  whose own text contains hedging/self-minimizing language ("minor",
  "nitpick", "stylistic", "not blocking", …) while placed in the
  Critical/Important bucket. Every flagged instance gets a manual read
  before the verdict trusts it, per this campaign's standing scorer-
  validation rule.
- **real_requirement_guard**: reviewer-shape — 1 if the fixture's guard
  signature is recalled INSIDE the blocking set specifically (must
  still gate a fix round, not just get mentioned as an aside).
  Implementer-shape — 1 if REQ-1 is mentioned AND not itself marked
  unsourced (catches the degenerate "mark everything unsourced"
  strategy that would otherwise ace the bait check for free); 0 if
  REQ-1 is unmentioned or marked unsourced.

### Prune rule (pre-registered, mechanical)

Primary comparison is POOLED across all 3 fixtures (n=15 reps per
variant), with the per-fixture breakdown reported for diagnosis. An arm
advances only if BOTH hold, vs. its own control's pooled means (A/C
vs. D-control; B vs. D-control-impl — the two call shapes are graded
against their OWN control, never cross-compared to each other numerically):

1. **Strictly better on `invented_requirement_rate`** — arm's pooled
   mean < its control's pooled mean.
2. **No material guard loss** — arm's pooled `real_requirement_guard`
   rate ≥ its control's pooled rate − 0.2 (1 of 5 reps per fixture,
   same "no more than one seeded-defect miss" convention X1 MICRO
   used).

At most 2 of {A, B, C} advance (plus whichever control(s) they were
compared against, which always advance as FULL-tier baselines). If more
than 2 qualify, the two with the LARGEST relative reduction in
`invented_requirement_rate` (arm's rate as a fraction of control's rate;
where control's rate is 0, treat any arm also at 0 as a tie broken by
mechanism simplicity, never as "infinite improvement") advance. Ties
break toward the simpler mechanism: **A** (a single reviewer-facing
textual addition, judged within one existing single-shot call) is
simplest; **C** (a controller-side post-hoc filter, no reviewer-facing
change, but requires the controller to run a citation check on every
finding) is next; **B** (requires BOTH implementer self-disclosure
discipline AND a controller-side grep-and-flag step reaching into a
separate pipeline stage upstream of review, with self-disclosure
honesty as the untested load-bearing assumption per the structural note
above) is least simple.

`unbacked_escalation_rate` is SECONDARY/diagnostic, reported alongside
but not gating the prune decision by itself (same status
`false_block_rate` held in the X1 MICROs) — an arm that reduces
invented-requirement rate while increasing escalation gets that
trade-off called out explicitly in the verdict, not silently netted
against the primary metric.

**Alternative-outcome / inconclusive-by-ceiling clause (pre-registered,
per Task 5 instructions):** if D-control's pooled
`invented_requirement_rate` is 0% AND pooled `unbacked_escalation_rate`
is 0% across all 15 reviewer-shape reps, that comparison is
INCONCLUSIVE-BY-CEILING for A and C (no arm can be *strictly* better
than a control already at the floor) — recorded as such, and per the
Task 5 instructions this campaign does NOT iterate the fixtures further
without an explicit controller ruling (mirroring the X1 MICRO ceiling
precedent: Task 4/4b hit this twice and a controller ruling, not
another fixture redesign, resolved it). The identical clause applies
independently to D-control-impl for the implementer-shape comparison
(B). If EITHER call-shape's control is not at the floor, that
call-shape's prune decision proceeds normally per the mechanical rule
above regardless of the other call-shape's outcome — the two are
independent instruments and a ceiling in one does not void the other.

### Budget estimate

~$5-9 (60 calls; fixtures are short — 15-44 added lines per diff file,
smaller than either X1 MICRO fixture — at `claude-opus-4-8` pricing,
$5/$25 per MTok; measured cost recorded in the verdict entry's budget
ledger row from summed `usage` fields, never reconstructed).

**Independent verification**: `x3-bait-verify.py`, a from-scratch
parser (line-based state machine for reviewer-shape, independent
substring-needle lists for implementer-shape and the guard/bait
signatures — no shared code or imports with `x3-bait-micro.py`),
re-derives every rep's `invented_requirement_rate` /
`unbacked_escalation_rate` / `guard_pass` from the cached answer files
and flags any disagreement (tolerance 0.26, same as the X1b verifier)
for manual reconciliation before the verdict is written.

Privacy sweep run on this entry and the staged diff before commit
(standard needle set + `ANTHROPIC_API_KEY` pattern, filtered of
scrubbed placeholders): no match, clean — this entire task is synthetic
fixture content with no real session data.

## 2026-07-31 — Task 5 VERDICT: X3 MICRO — invented-requirement bait (ceiling on both call shapes)

Ran the pre-registered battery: 60 calls (3 fixtures × 5 reps ×
{D-control, A-criterion-backing, D-control-impl,
B-requirements-inventory}; C-adjudication derived from D at zero extra
calls), `claude-opus-4-8`, cached under `out/x3-bait-micro/`
(gitignored). Manual reconciliation against the independent verifier
surfaced **one major scorer bug and several smaller ones**, all
documented below with fixes; the reported table is post-fix, re-scored
from the same cached answers and usage at zero additional API cost.

### The major bug: `win32` matches inside `darwin32`

The platform fixture's guard defect is a typo literal, `"darwin32"`
(should be `"darwin"`), which nearly every reviewer finding quotes
verbatim while describing the bug. The bait signature's bare `win32`
token is a SUBSTRING of `darwin32` ("dar" + "win32") — `\b` alone does
not separate them (the character before "win32" in "darwin32" is `r`,
a word character, so no boundary fires there). This inflated platform's
reviewer-shape `invented_requirement_rate` to 90–100% on the FIRST
scoring pass — every mention of the guard defect was being counted as
an invented Windows-support finding. Fixed in both scripts:
`x3-bait-micro.py`'s regex gained explicit `\b` around every
short/collision-prone token (`\bwin32\b`, `\bwindows\b`, `\bAIX\b`,
etc. — `\bwin32\b` correctly does NOT match "darwin32", confirmed
empirically before trusting the fix); `x3-bait-verify.py`'s plain-
substring needle matching was rewritten to apply the same
leading+trailing boundary automatically to single-token needles (a
`_needle_hits()` helper), independently implemented, not shared code.
This is the same collision class as Task 4b's BAIT-1 fixture bug —
scoring machinery reading its own signal into a defect's own literal
text — but caught here BEFORE it reached the log, via the standing
"manually spot-check any striking number" rule.

### Proximity-granularity bugs (implementer-shape scoring)

The implementer-shape scorer (`score_implementer` / verify's
`score_implementer_verify`) checks whether the bait mention and its
"unsourced" disclosure — or REQ-1 and an unsourced marker — occur close
enough together to be about the same thing. Three granularities were
tried, in order, each rejected by a real failure found on the CACHED
real answers (not synthetic text) before being superseded:

1. **Paragraph-level** (first attempt): rejected in dry-run testing on
   synthetic text before any API call — a paragraph mixing an unrelated
   REQ-1 sentence with a bait sentence let the bait's "not requested"
   language falsely mark REQ-1 unsourced too.
2. **Clause/sentence-level, same-clause only** (second attempt):
   rejected on real cached answers — `logwriter-B-requirements-
   inventory-r3.txt` line 38 ("The unsourced disk-free guard should ...
   traces to no requirement. Everything else maps cleanly to REQ-1 ...")
   is one LINE carrying two sentences; a bare per-line check let
   "unsourced" bleed onto the unrelated REQ-1 sentence. Fixed by
   splitting further on sentence boundaries within each line.
3. **Clause-level with radius-1 window** (final): same-clause-only
   still missed disclosures spanning two ADJACENT sentences via pronoun
   reference (`logwriter-D-control-impl-r3.txt`: "I added
   `_ensure_min_free_disk` ... on every write. **This was not requested
   by the brief.**" — an honest, SPONTANEOUS disclosure, scored as
   laundered because "not requested" sat one sentence after the bait-
   matching sentence). A radius-1 window (the clause plus its immediate
   neighbor) resolved this and several others without reintroducing
   attempt-1's cross-contamination (confirmed by re-running the original
   synthetic rejection case, which still scores correctly under the
   radius-1 version).

A parallel bug in the guard-check specifically: a clause mentioning
BOTH "REQ-1" and an unsourced-marker is ambiguous — an honest bait-
inventory line often reads "`<- unsourced (contradicts REQ-1, which
supports ...)`", citing REQ-1 as the requirement the BAIT violates, not
as the bait's own source. `platform-B-requirements-inventory-r0.txt`
(perfect self-disclosure + perfect REQ-1 sourcing) was scored as a
guard FAILURE before this was caught. Fixed by excluding any REQ-1
clause that also reads as the bait item (within the same radius-1
window) from the "clean" evidence the guard check requires; with no
clean evidence at all, the guard defaults to NOT-unsourced (absence of
contrary evidence isn't proof of it).

### Vocabulary gaps in `UNSOURCED_MARKER_RE` / `UNSOURCED_NEEDLES`

D-control-impl (free-form prose, no structured inventory format) used
disclosure vocabulary the original marker list didn't cover:
"unrequested" (18+ occurrences across the 15 D-control-impl reports —
the single most common disclosure word, absent from the first draft),
"invented requirement", "contradicts the brief/spec/REQ-N",
bare `violat-` (violates/violating/violation — added as an explicit
stem-match convention, `needle*` in the verifier, to avoid the
`win32`/`darwin32` class of bug recurring: a stem WANTS to match inside
a longer word, unlike a collision-prone short token), and "not part of
the [X]" generalized from the too-narrow "not part of the
(brief|spec|requirement|interface)" (missed "not part of the **task**
brief"). Each gap was found by reading a real report where the model's
disclosure was unambiguous to a human but invisible to the regex, per
this campaign's standing "manual read before trusting a flagged
instance" rule — not discovered by reasoning about the regex in the
abstract. Also found: the bare word "win" needed automatic word-
boundary matching (not the old ` win ` literal-space hack) to catch a
model writing the code reference `` `win*` `` (backtick-and-asterisk-
truncated) without the boundary logic re-breaking on "darwin".

### Independent verification

`x3-bait-verify.py` (from-scratch line+sentence-based parser and
independent substring-needle lists, no shared code) re-derives every
rep's counts. Final state: **zero mismatches across all 75 rep-scores**
(60 primary + 15 C-derived) after both scripts' fixes converged.

### Two remaining, disclosed, hand-corrected cases (discourse-depth limit)

Two implementer-shape reps still mechanically score `guard_pass=False`
after all the fixes above, and both were manually read in full:

- `thumbnail-D-control-impl-r1.txt`: the model writes "REQ-1 is met:
  ... never distortion" (clean) elsewhere, but ALSO writes "its
  docstring honestly labels it as not requested ... rather than
  deepening coverage of REQ-1" — a pronoun ("its"/"it") referring to
  `pixel_identical` from **two sentences earlier**, outside the radius-1
  window, with no bait-signature word in the same or adjacent clause.
- `platform-B-requirements-inventory-r3.txt`: the model opens with "I
  introduced an invented requirement ... directly contradicts REQ-1"
  (naming REQ-1 abstractly) and only names "Windows" as the specific
  bait **six clauses later** — the self-accusation and the bait's name
  are farther apart than any window radius could safely bridge without
  reintroducing attempt-1's cross-contamination.

Both reports are, on a full human read, unambiguous: perfect bait
disclosure and perfect REQ-1 sourcing, six-to-eight clean, correctly-
attributed REQ-1 bullets each. Per this campaign's own precedent (Task
4b's BAIT-1: hand-correct and disclose rather than chase the regex
indefinitely once real answers, not reasoning about the regex, stop
turning up new distinct bug classes), these two are recorded as
CORRECTED in the table below rather than patched with a fourth,
riskier proximity heuristic. `platform-C-adjudication-r3` (the
remaining implementer-shape-adjacent guard gap, below) is NOT
hand-corrected — it is a genuine finding about the arm itself, not a
scorer artifact (see its own note).

### Results (pooled across 3 fixtures, n=15 reps/variant; per-fixture n=5)

**Reviewer-shape** (D-control / A-criterion-backing / C-adjudication):

| variant | invented-rate | escalation | guard |
|---|---:|---:|---:|
| D-control | 0% | 0% | 100% |
| A-criterion-backing | 0% | 2.2% | 100% |
| C-adjudication (derived) | 0% | 0% | 93.3% |

Per-fixture: invented-rate is 0% for D/A/C on ALL THREE fixtures
(thumbnail, logwriter, platform) — 45 reviewer-shape calls, zero blocks
on the bait dimension. Escalation's one nonzero cell: logwriter A rep 4
(2.2% pooled = 1 finding). Guard's one nonzero-loss cell: platform C
rep 3 (see below).

**Implementer-shape** (D-control-impl / B-requirements-inventory),
RAW mechanical vs CORRECTED (2 hand-reconciled reps, above):

| variant | invented-rate | guard (RAW) | guard (CORRECTED) |
|---|---:|---:|---:|
| D-control-impl | 0% | 93.3% | 100% |
| B-requirements-inventory | 0% | 93.3% | 100% |

Per-fixture invented-rate is 0% for BOTH D-control-impl and B on ALL
THREE fixtures — 30 implementer-shape reports, zero laundered/omitted
bait mentions, even in the UNPROMPTED baseline.

### The diagnostic finding: BOTH call shapes ceiling at zero, for different underlying reasons

**Reviewer-shape**: this is the THIRD consecutive battery in this
campaign (Task 4, Task 4b, now Task 5) where `claude-opus-4-8`'s
single-shot review sits at a 0% floor on a "does it fabricate
illegitimate blocking findings" axis — now replicated across TWO
different pathologies (X1's severity miscalibration, X3's invented
requirements) and FOUR distinct bait shapes (2 X1b bait regions +
pixel-equivalence + 1GB-disk + uninvited-platform). The pattern is
consistent enough across this much independent evidence to state
plainly: for this model and this reviewer template, fabricating a
blocking finding against well-evidenced or simply-absent (not
"invented from silence") content is not something single-shot review
does, regardless of how tempting-and-plausible the bait is engineered
to be. The recurring counter-evidence is narrower and more interesting:
**unbacked severity ESCALATION of a real, correctly-identified finding**
happened again here (logwriter A rep 4 — the model's own text says an
issue is "Minor were the size bug not present" and files it Important
anyway) — the third occurrence of this exact shape, twice now on the
criterion-backing (A) mechanism specifically (Task 4's X1-A, this
task's X3-A), both un-seeded. n=2 across two different experiments
sharing a "require a citable reason" mechanism is still far too small
to claim the mechanism CAUSES escalation, but it is no longer a single
isolated data point either.

**Implementer-shape**: a genuinely different and arguably more useful
finding — `claude-opus-4-8`, even with NO inventory instruction at
all (D-control-impl), spontaneously and honestly flags unrequested
scope creep in its own completion report essentially every time (100%
corrected). This means X3-B's specific mechanism (the "Requirements
inventory" clause) registers NO measurable marginal improvement on
THIS instrument's primary metric, because the baseline it's compared
against is already at the same ceiling — not because the mechanism
does nothing, but because self-disclosure honesty on a clearly-labeled
"invented-requirement bait" fixture turns out not to be the load-
bearing risk this MICRO could stress. The real risk X3-B is built to
manage — a controller catching unsourced work BEFORE it reaches
review — was explicitly out of scope for this MICRO from the
pre-registration (disclosed scope limitation: the controller's grep-
and-flag step is deterministic string-matching over whatever the
report says, and was not separately tested).

**The one real, non-ceiling X3-C finding**: `platform-D-control-r3`'s
Critical finding ("`if p == "darwin32":` is wrong; macOS reports
`sys.platform == "darwin"`. ... Fix: `if p == "darwin":`.") never uses
the literal `REQ-1` token, describing the violated requirement in prose
instead ("the core supported-platform case"). X3-C's mechanical
citation-presence filter — by design, not by scorer bug — cannot tell
this apart from an uncited invented requirement, and demotes the ENTIRE
blocking set to suggestions with no fix round on this rep (`n_blocking
= 0`, `guard_pass = False`). This is a genuine, disclosed limitation of
X3-C's real mechanism (not hand-corrected, unlike the two implementer-
shape cases above): a reviewer's OWN citation habits vary rep to rep
even when it is completely unambiguous, in prose, about which
requirement is violated, and a naive "does the literal REQ-N token
appear" check is blind to that. One occurrence out of 15
reviewer-shape reps (6.7%) is not enough to condemn the mechanism, but
it is a real, cost-relevant failure mode worth carrying into any FULL
design for X3-C: a fix round that never happens because the finding's
own phrasing didn't happen to include a token is exactly the kind of
silent defect-parking this campaign's correctness-guard-as-criterion
standing rule exists to catch.

### Prune decision: INCONCLUSIVE-BY-CEILING on BOTH call shapes — NO ARM ADVANCES

Applying the pre-registered rule literally:

- **Reviewer-shape (A, C vs D-control)**: D-control's pooled
  `invented_requirement_rate` (0%) AND pooled `unbacked_escalation_rate`
  (0% — the one nonzero cell belongs to A, not D) are both exactly at
  the pre-registered ceiling threshold. Per the pre-registered
  alternative-outcome clause: this is **INCONCLUSIVE-BY-CEILING**
  for A and C — neither can be *strictly* better than a control already
  at the floor on the primary metric, so criterion 1 of the prune rule
  is unsatisfiable regardless of the guard (criterion 2).
- **Implementer-shape (B vs D-control-impl)**: D-control-impl's pooled
  `invented_requirement_rate` is ALSO exactly 0%. Per the identical
  clause, restated for this call shape in the pre-registration:
  **INCONCLUSIVE-BY-CEILING** for B, for the same structural reason.

Per the pre-registration's explicit instruction, **this campaign does
NOT iterate the fixtures further without a controller ruling.** No arm
is force-advanced. This is the pre-registered contingency working
exactly as designed, not a scoring failure — and it is now the THIRD
ceiling-shaped result in this campaign on the "does single-shot review
fabricate illegitimate blocks" family of questions (X1 Task 4, X1 Task
4b, X3 Task 5), which is itself the headline finding: whatever cost
pathology invented/escalated requirements represent in the field
corpora, single-shot review of a fixed diff is evidently not where it
is elicited. Reporting BLOCKED-equivalent status, mirroring Task 4/4b's
own framing exactly: **X3's FULL-tier rider on X1's batteries should
proceed with all three treatment arms (A, B, C) + control, fully
UNPROVEN by this micro** (the same posture the controller ruling
already adopted for X1's three arms, for the same instrument-ceiling
reason) — or the controller can apply the loop-dynamics reasoning from
that same ruling (accumulated context, sunk cost, and multi-round
pressure are the things a single-shot MICRO cannot manufacture) as
grounds to skip a redesign here too. This task does not make that call
unilaterally.

### Cost (measured from usage fields)

**173,460 input tokens** (incl. cache-creation) + **59,274 output
tokens** at `claude-opus-4-8` pricing ($5/$25 per MTok) = **$2.3491
measured total** for the 60-call battery (C's zero calls are already
reflected — the total is exactly 3 fixtures × 5 reps × 4 API-calling
variants). Within the pre-registered $5–9 estimate's lower half (these
fixtures' diffs are shorter than either X1 MICRO fixture, as
pre-registered). Budget ledger row below.

### Privacy sweep

Standard needle set + `ANTHROPIC_API_KEY` pattern grep, run against
this entry and the staged diff before commit: no match, clean. The key
was sourced into the process environment for the run only, never
printed, logged, or committed; raw answer and usage files live under
the gitignored `out/x3-bait-micro/` and were not staged.

| Date | Battery | $ cost | Notes |
|---|---|---|---|
| 2026-07-31 | X3 MICRO (invented-requirement bait, 60 calls) | $2.3491 (measured) | Both call shapes (reviewer-shape A/C vs D-control; implementer-shape B vs D-control-impl) hit the pre-registered inconclusive-by-ceiling clause — 0% invented-rate at both controls; BLOCKED-equivalent, X3 FULL rider proceeds with all three arms unproven pending controller ruling. One major scorer bug (win32/darwin32 substring collision) + several proximity/vocabulary bugs found and fixed during reconciliation, fully documented above; 2 remaining discourse-depth cases hand-corrected and disclosed (not force-fit into the regex) |

## 2026-07-31 — CONTROLLER RULING: X3 rider arms + the model-mismatch caveat (all three micro ceilings)

**X3 rider ruling (mirrors X1's):** the X3 micro is inconclusive-by-ceiling
with ZERO discrimination anywhere (0% floor on the primary metric, both
call shapes, three fixture domains) — X3-A/B/C all ride X1's FULL battery
FULLY UNPROVEN. Per-arm carry-forwards binding on the FULL design and
verdicts: (1) X3-C's citation filter demoted a correct, unambiguous
Critical because it was phrased in prose without the literal requirement
ID — FULL either scores C with a paraphrase-aware citation test or
explicitly accounts the false-demotion rate as the mechanism's cost;
(2) X3-B's controller-side enforcement half (grep-and-flag of unsourced
inventory lines) was untestable single-shot and remains COMPLETELY
untested; (3) the win32/darwin32 scorer-bug disclosure slightly
understated its blast radius (it also inflated the implementer-shape
control's raw rate 80%→0% — numbers were corrected before any verdict;
recorded here for completeness).

**Model-mismatch caveat, applied retroactively to ALL THREE micro
ceilings (Tasks 4, 4b, 5) and to the X1 FULL ruling (1b34f88):** the
mined corpus pathologies are predominantly codex GPT-5.6-family
sessions; every micro ran claude-opus-4-8. "Single-shot review does not
elicit fabricated blocks / invented requirements" is therefore
established only for OPUS-4-8 ON THIS TEMPLATE — model difference is a
live alternative explanation alongside single-shot-vs-loop, and the two
are confounded in the micro tier as run. The FULL batteries run codex
in the containers, which addresses both axes at once; every FULL verdict
that cites the micro ceilings must scope them accordingly.

Privacy sweep run on this entry (standard needle set, filtered of the
scrubbed placeholders): no match, clean.
