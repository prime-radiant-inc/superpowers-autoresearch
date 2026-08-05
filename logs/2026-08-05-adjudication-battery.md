# Adjudication Battery Log (2026-08-05)

Append-only; standing disciplines per the plan-decomposition log header,
plus: per-rep recorded served model is a mandatory covariate (census
correction, 2026-08-05).

## 2026-08-05 — PRE-REGISTRATION: r1t / rebut / composed on the retargeted base

**Directive (Jesse, this morning):** run the R1 triage sentence and the
serf after-action package (park-with-experiment, convergence tracking,
re-flag stop) together and see how they interact; retarget the base to
current dev with the merged stack.

**Base:** sim/dev2 @ fb518ed (origin/dev with #2059-2062, #2077, #2078,
#2080, #2090). Prior 1fed99d-era baselines DO NOT transfer — the merged
stack changes SDD behavior (batching, evidence-bearing preflight,
rule-and-continue). This battery carries its own controls.

**Provenance note:** the rebut package has REAL-SESSION provenance
(~/after-action-rebut-with-evidence.md, serf Roborev remediation,
2026-08-04/05: rounds 6-9 cost ~1M subagent tokens; two evidence
rebuttals held; the pattern's guards are encoded in the arm text). The
r1t sentence has micro provenance (R1: guard 8/8 under every policy).

**Arms × scenario:** cp-x1-edit-existing (real seeded defects incl. two
debatable classes; review dynamics measurable via chain stats):
- base2 control ×4 (`cp/base2` @ fb518ed)
- r1t ×3 (@ 08972e6), rebut ×3 (@ 52df997), composed ×3 (@ 77ec054)
13 reps ≈ $110 est. Lane B first (control chain), lane A joins when the
sonnet cell frees it.

**Reachability disclosure (standing rule):** rebut's breaker path
(park-with-experiment at the cap) may go unexercised — prior-base
x1-edit reps rarely hit the cap. Its always-reachable surfaces: the
per-round ledger class/severity tags, the early-adjudication clause on
flat repetition, and evidence-standard language for any parked/⚠️
ruling. If no rep exercises the cap path, the battery grades the
reachable surfaces and says so — the cap path then needs either a
rathole-inducing fixture variant or stays argued-from-provenance.

**Endpoints:**
1. GUARD (decisive): seeded-defect escapes vs base2 control — arms must
   not exceed control escapes (prior-era pooled 2.0/rep; base2 rate
   measured fresh here). ANCHOR-IMPORTANT/CRITICAL cells hand-checked
   per the scan's known limits; per-rep model recorded.
2. RATHOLE (r1t's axis): fix rounds + dispatches per rep (chain stats)
   and hand-read: do structure-conformance findings block loops in
   control but ride the ledger under r1t/composed?
3. ADJUDICATION QUALITY (rebut's axis): hand-read every parked/⚠️/ruled
   finding — does the ruling cite a run or observable under rebut vs
   argument-only in control? Count rulings-with-runs / total rulings.
4. INTERACTION: composed vs each solo — additive, interfering, or
   redundant (the two texts touch different moments: reviewer
   calibration vs controller adjudication; interference would surface
   as changed guard or round counts).
5. Cost/rep + convergence-tagging uptake (are per-round ledger lines
   actually class/severity-tagged — the doctrine predicts yes for
   rebut's ledger-line surface, it rides an existing attended moment).

## 2026-08-05 — PRE-REGISTRATION: T9 interactive tooling-ask cell

**Directive (Jesse, this morning):** the project-quality-tooling ask —
linting/auto-formatting, unit-test infrastructure, e2e test
infrastructure, possibly fuzz/mutation — is an ask-the-user question,
never decided silently. This cell A/Bs two placements of that ask
against a control: does the ask fire, does it fire BEFORE any code is
written, and does its answer land in the spec/plan's Global
Constraints.

**Base:** sim/dev2 @ fb518ed (same retargeted base as the r1t/rebut
pre-registration above; this cell reuses cp/base2 as its control).

**Arms × scenario:** t9-tooling-ask (new interactive scenario: fresh
git repo with only a README — genuinely no tooling configured; naive
"build a reading-list CLI" opening; x9-style pinned generic replies
carry the session through brainstorming's question loop; one pinned
tooling answer used ONLY if the session asks — "Yes — linting,
auto-formatting, and unit tests please. Skip fuzz testing."; reply cap
8, then a proceed-with-your-recommendations closer):
- base2 control ×3 (`cp/base2` @ fb518ed)
- t9a ×3 (@ c02e67b — Draft A, brainstorming design-presentation
  bullet), t9b ×3 (@ f242ae6 — Draft B, writing-plans Tooling Check
  before File Structure)
9 reps ≈ $50-70 est. Runner: campaigns/cost-pathologies/run-quorum.sh
{base2|t9a|t9b} t9-tooling-ask 3. Codex lane. NOT launched by this
session — both lanes busy; controller launches.

**Endpoints:**
1. PRIMARY: tooling-ask-fired rate (t9-tooling-ask-fired instrument +
   hand-read) and ask-before-code (t9-ask-before-code: ask's first
   occurrence vs first patch_apply_end code-file write, .md and
   docs/ excluded; tooling CONFIG files deliberately don't count as
   code — writing them is the Task-0 setup the ask licenses). Control
   expected ~0 fired; t9a should fire during brainstorming's design
   presentation (user still in the loop, pre-spec); t9b at plan time
   (post-spec, pre-task). The placement comparison is WHEN the ask
   fires relative to code and whether the user was still in the loop —
   not merely whether it fires.
2. constraints-landed rate (t9-constraints-landed: a Global
   Constraints/equivalently-named section under docs/ whose own block
   names the chosen tooling; the plan template's bare heading does not
   count).
3. GUARD: sessions still complete their brainstorm→spec→plan flow — no
   derailment attributable to the added text (compare stage reached +
   gauntlet AC verdict vs control; the scenario's ACs are arm-neutral
   by construction, the tooling ask is never an AC).
4. Per-rep served model recorded (t9-served-model instrument; census
   rule per this log's header).
5. HAND-READ of every instrument line labeled `unknown` — the
   mechanical layer is conservative by design (strong ask detection =
   lint-term + test-term + question mark in one assistant message;
   everything weaker is `unknown`, never auto-claimed).

**Reachability caveat (honest, standing rule):** the scripted replies
are content-light deflections ("Whatever you'd recommend — keep it
simple." / "Yes, that design looks right — go ahead."), generic enough
for unpredictable question order but with no real content to give. A
brainstorming loop that insists on substantive answers may never reach
design presentation, and the 8-reply cap will then truncate the
session. If control reps show sessions not reaching design
presentation / spec / plan, the cell is INCONCLUSIVE-BY-FIXTURE — the
verdict must say so rather than reading non-firing arms as nulls, and
the fixture needs a richer scripted user before a rerun.

**Instrument validation (no spend):** bash -n clean on checks.sh;
`bun run quorum check` reports `ok t9-tooling-ask` (the scenario was
rsynced into the evals checkout's scenarios/ the same way run-quorum.sh
does at launch, git-excluded; the 4 pre-existing FAILs — cp-x10-spec,
pd-overflow, pd-overflow-xl, pd-pipeline — are the known helper-function
/ heredoc lint findings on scenarios that already ran fine); post()
dry-run against a real prior run's artifacts
(results/cp-x2-advisory-x2b-rep1, stubbed prelude verbs) exercised all
six emit lines on real rollout jsonl — timestamps extract and order,
patch_apply_end paths parse, served-model resolves, and the unrelated
scenario correctly grades `unknown` not `yes` on ask-fired. All six
instruments are emit-only `command-succeeds "true # …"` lines (the
cp-x8-approvals-v2 pattern) — they can never gate a verdict.
