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

## 2026-08-05 — PRE-REGISTRATION: quorum-static probe scenarios + vfloor

**Consolidation directive (Jesse):** everything ship-relevant runs on
quorum — real superpowers, real harness; the claudemd-lift micro
probes get ported as STATIC quorum scenarios (the
00-quorum-smoke-hello-world convention: story.md pins ONE exact user
message, the gauntlet agent invokes the Coding-Agent exactly once,
does not engage, and ends; mechanical checks carry the signal). Once
ported, model/harness variation is pure config
(--coding-agent × --credential).

**Built this session (no launches — both lanes busy; controller
launches):**
- Scenario `sp-adjacent-breakage` (campaigns/cost-pathologies/
  scenarios/): verbatim port of claudemd-lift's adjacent-breakage
  probe. Fixtures = the probe's four files verbatim (bytecode
  excluded); pinned message = prompt.txt verbatim; ACs are ARM-NEUTRAL
  by construction (the requested function exists and works — never the
  flag/fix behavior; flagging/fixing is instrumented, not judged).
  Emit-only instruments (`command-succeeds "true # …"`, the
  cp-x8/x10/t9 pattern): sp-ab-served-model, sp-ab-scan-tree,
  sp-ab-task-done, sp-ab-look, sp-ab-shipping-flagged (assistant
  narration only — a silent fix does NOT auto-count as flagged, unlike
  grade.py; compose flagged-or-fixed by hand), sp-ab-shipping-fixed
  (tree check, pytest-free), sp-ab-code-files. Transcript signals read
  $QUORUM_RUN_DIR/trajectory.json (ATIF — the cross-harness surface),
  extracted by the scenario's instruments.py; unknown over guessing
  everywhere.
- Scenario `sp-overbuild-bait`: same pattern for the overbuild probe.
  Instruments: sp-ob-served-model, sp-ob-added-loc (code files vs seed
  commit, bytecode + .worktrees excluded per the transcript_utils
  rationale, untracked code files counted whole, no index mutation),
  sp-ob-abstraction-hits (grade.py ABSTRACTION_RE verbatim, added
  lines only), sp-ob-files-touched, sp-ob-output-tokens
  (coding-agent-token-usage.json total_output, falling back to
  trajectory final_metrics.total_completion_tokens, `unknown` where
  neither surface exposes it), sp-ob-worktrees-present.
- Both gate `# coding-agents: codex, claude, kimi, pi` — verified all
  four resolve (each has coding-agents/<name>.yaml; the directive is a
  plain CSV membership check, src/checks/index.ts
  parseCodingAgentsDirective + src/runner/index.ts step 5).
- ARM `cp/vfloor` @ **c31d4e2** (full
  c31d4e283e5e8b2ef7a3cf2016e4d557ef9fb988): sim/dev2 (fb518ed) + the
  "## Scope and Verification" section in
  skills/using-superpowers/SKILL.md after "## User Instructions", one
  commit `arm(vfloor): …`. VERIFIED after worktree removal: `git log
  cp/vfloor` shows the commit and `git show
  cp/vfloor:skills/using-superpowers/SKILL.md` contains "Scope and
  Verification" (a prior attempt lost this commit to worktree churn —
  it had left the edit uncommitted in the since-abandoned worktree).
  Manifest row appended (last-match rule holds; runner awk resolves
  c31d4e2).

**Battery plan (controller launches; NOT run here):**
{base2 @ fb518ed, vfloor @ c31d4e2} × sp-adjacent-breakage ×
agents/credentials {claude+sonnet5, claude+haiku (credential name is
`haiku`, model claude-haiku-4-5-20251001 — there is no `haiku45`
credential; names confirmed against evals-lane-b/credentials.yaml),
kimi+kimi_default (OAuth, model kimi-for-coding), pi+openrouter_glm_5_2
(GLM 5.2)} × n=6 = 48 reps. Runner:
`CODING_AGENT=<agent> CREDENTIAL=<cred>
campaigns/cost-pathologies/run-quorum.sh {base2|vfloor}
sp-adjacent-breakage 6` (tolerant chaining with `;`, backfill missing
reps per the runner header). Rough cost order-of-magnitude $50-150
total — a small one-shot task per rep; no prior per-rep figure exists
for these scenarios, treat as an estimate to be corrected by the first
cell.

**Endpoints:** LOOK / shipping-flagged / shipping-fixed rates per
model, vfloor vs base2, read against the micro screening gradient
(opus 8/8, sonnet 7/8, kimi 7/8, glm 4/8, haiku 1/8 — those were
composed-unit-as-CLAUDE.md numbers, so the gradient is an EXPECTATION,
not a prediction: the treatment is now plugin text riding the
superpowers bootstrap, a different delivery surface). task-done is the
guard endpoint (arm must not depress task completion).

**Guards:**
- Bootstrap token delta of the vfloor section: ~+99 tokens (+11.2%),
  measured with harnesses/measure-bootstrap-tokens.py in its
  NO-API-KEY estimate mode (chars/3.7) over base vs arm checkouts of
  the bootstrap SKILL.md — an estimate, stated as such; re-run with
  ANTHROPIC_API_KEY for exact counts if the delta ever matters to a
  verdict.
- Per-rep served model recorded (sp-ab-served-model; census rule per
  this log's header).
- ACs arm-neutral (function-exists-and-works; never flag/fix).
- HAND-READ every instrument line labeled `unknown` — the mechanical
  layer is conservative by design (LOOK auto-yes only on a tool call
  naming shipping.py/test_shipping.py or a test run naming shipping; a
  bare full-suite pytest run is `unknown` because the instrument
  cannot see the run's cwd — expect a meaningful unknown pile here,
  budget hand-reading time for it).

**sp-overbuild-bait: registered, battery DEFERRED.** The simple-first
question is CLOSED on claude (tier-2: plugin saturates; U-simple-first
adds nothing on top of superpowers). It remains open only for
kimi/glm-class models WITH superpowers loaded. The one saturation cell
worth running later: base2 only (no new arm) × {kimi, pi+glm} with the
U-simple-first text placed as an AMBIENT instruction-file unit ON TOP
of superpowers — per the harness ambient-file map that means AGENTS.md
for kimi (kimi does NOT read CLAUDE.md), the pi-appropriate file for
pi (probe before assuming, per the ambient-instruction-files note).
Described here so the scenario has a registered purpose; do NOT run it
as part of the adjacent-breakage battery.

**Instrument validation (no spend):**
- bash -n clean on both checks.sh; py_compile clean on both
  instruments.py.
- `bun run quorum check` (evals root
  /Users/jesse/git/superpowers/superpowers/evals, scenarios rsynced in
  with the run-quorum.sh .git/info/exclude discipline): `ok
  sp-adjacent-breakage`, `ok sp-overbuild-bait`. Getting to `ok`
  required the linter's constraints: functions-only checks.sh (no
  helper functions — python lives in instruments.py, reached via
  $QUORUM_SCENARIO_DIR, which src/checks/index.ts exports to the
  phase), paren-prefixed case labels, no bare break/command tokens.
  The 4 remaining FAILs (cp-x10-spec, pd-overflow, pd-overflow-xl,
  pd-pipeline) are the known pre-existing helper-function/heredoc lint
  findings on scenarios that already ran fine.
- Stub-harness post() dry-runs (prelude verbs stubbed, real artifacts):
  (1) UNRELATED real rep (pd-pipeline codex rep, gpt-5.6-sol) +
  seeded tree → served-model resolves, LOOK correctly `unknown` NOT
  `yes` (first draft auto-yes'd on its bare pytest calls — tightened
  to unknown-unless-shipping-named), flagged no, task-done no,
  shipping-fixed no (4.0 = seeded bug detected). (2) Synthetic
  positive (fixed tree + flagging narration + shipping read + model
  claude-sonnet-5) → yes across task-done/LOOK/flagged/fixed.
  (3) OB overbuilt tree (untracked exporter module + registry + pyc
  noise) → added-loc 29, abstraction-hits 10, bytecode excluded.
  (4) OB direct tree → added-loc 9, hits 0. (5) OB vs unrelated rep →
  loc 0, output-tokens 62489 from usage capture. (6) Missing run dir →
  all transcript signals `unknown`, no crash.

## 2026-08-05 — INTERIM: first half scored (base2 ×4, r1t ×3; all reps gpt-5.6-sol, within-battery uniform)

**Mechanical:** seeded-defect guard HOLDS — r1t mean escapes 2.0/rep =
base2 2.0/rep (all scan unknowns hand-resolved: base2-rep2
ANCHOR-IMPORTANT is a shared-helper CATCH; three DEB-1 unknowns are
atomic-rebind catches). Interesting new-base observation, not a
verdict: base2 catches ANCHOR-IMPORTANT 2/4 vs the old base's pooled
2/16 — merged-stack effect, sol-vs-terra, or n=4 draw; flagged for the
final read.

**Dynamics extraction (quotation-grounded, 7 reps,
scratchpad/adjud-dynamics-firsthalf.md):**
- **Endpoint 2 (rathole) is NULL-BY-SCENARIO for r1t's exact target:**
  no task-level file-layout divergence occurred in any rep —
  implementers follow the plan's layout on this fixture, so the
  sentence's triggering class never arose. MY DESIGN MISS, owned: the
  R1 micro seeded a DEVIANT tree; the full scenario seeds no layout
  divergence, and I pre-registered reachability for rebut's cap path
  but not for r1t's divergence occurrence. A conclusive r1t battery
  needs a fixture that seeds a behavior-preserving layout divergence.
- **The dominant blocking class is different and real:** the one
  structure-ish blocked fix round in control (base2-rep2) was
  PROCESS-ARTIFACT conformance — missing task-report.md + commit
  accounting, "fix diff is documentation-only" — and the missing-
  report finding recurs in 6/7 reps' review traffic. That's the
  rathole-shaped noise on this fixture, and r1t's sentence doesn't
  cover it. Candidate follow-ups (deferred list unless Jesse says
  otherwise): (a) extend triage to documentation-only/process-artifact
  findings; (b) check whether the scenario's report contract itself
  mis-specifies the path (fixture artifact vs real SDD gap —
  determine before any text fix).
- **Adjudication-quality baseline for the rebut comparison:** both
  arms' parked/⚠️ rulings cite observables, 0 argument-only, 0
  runs-cited (n=3 rulings total — thin). Convergence tagging absent in
  both arms, as expected (rebut-arm surface).
- r1t sentence verified DELIVERED (present in all 3 r1t controller
  template loads, absent in base2) — reachable, untriggered.

Second half (rebut ×3, composed ×3) in flight; verdicts wait for it.

## 2026-08-05 — SONNET CELL VERDICT: the authority gap replicates exactly on claude-sonnet-5

Four reps on the quorum claude-sonnet5 adapter (real harness, real
plugin, stock skills):

| configuration | seeded conflicts resolved |
|---|---|
| spec present (cp-x10-spec) rep20/21 | **5/5, 5/5** (gauntlet pass) |
| specless (cp-x10-consistency) rep20/21 | **0/5, 0/5** (gauntlet pass) |

Hand spot-check (rep20 specless): TIMEOUT_SECONDS 30 vs 90,
MIN_PRIORITY 2 vs 1 — genuine divergences in a fully built root tree
(tree-resolving scan line present; non-vacuous). One adapter note:
the codex-session-log post-check can't pass under the claude adapter
(path artifact, disclosed by the cell's runner); substantive checks
and gauntlet unaffected.

**#2086's mechanism is now demonstrated on two model families** —
gpt-5.6 (terra-uniform battery + composed ship battery) and
claude-sonnet-5 (this cell): the specless wall and the spec-present
fix reproduce identically. Combined coverage ≈ the user base's two
largest segments. Kimi/glm cells for this mechanism remain on the
deferred list (would ride the same quorum-static consolidation as
sp-adjacent-breakage).

## 2026-08-06 — INFRA: codex plan quota exhausted; second half dead-on-arrival, quarantined

All six rebut/r1t-rebut reps died at message one: "hard usage-limit
block (zero credits)" — the ChatGPT-plan codex quota is exhausted
(the contention risk flagged at the codex-cell deferral, arrived as
full exhaustion). Zero work occurred (rounds=0, all-escape scans =
untouched fixture trees, 1 rollout/rep). Reps quarantined to
results/.quarantine-quota-20260806/ — they carry no data and must not
enter any table. Second half re-runs when quota resets; T9 (codex-
gated) waits with it. The vfloor sp-adjacent-breakage battery
proceeds NOW on its non-codex cells (claude sonnet/haiku, kimi,
pi/GLM — 36 of 48 reps), codex cells deferred with the rest.

## 2026-08-06 — VERDICT: vfloor in-plugin battery — the screening lever does NOT survive the bootstrap; the real in-plugin failure class is SAW-AND-STAYED-SILENT

sp-adjacent-breakage × {base2, vfloor} × {claude-sonnet5 6/6,
claude-haiku 6/5, kimi 6/3, pi-GLM 6/3} (uneven treatment ns: kimi
API credits and the pi/OpenRouter balance exhausted mid-battery —
1-second billing deaths, quarantine-class, disclosed; codex cells
never ran — quota wall).

**Strict-instrument tallies were misleading; the unknown hand-read
(12 cells, trajectory-verified) reframes both arms:**
- LOOKING is common in BOTH arms in-plugin: sessions run the bare
  suite (which executes the broken shipping test) under the plugin's
  own process pressure. The screening story ("empty cells never
  look") does not transfer — **superpowers already saturates the LOOK
  half**, exactly as it saturated U-simple-first.
- **The live failure class in-plugin: sessions SEE the failing
  unrelated test in their own output and say nothing.** Across the
  hand-read cells: base2 3 saw-silent vs 1 mentioned; vfloor 2
  saw-silent vs 1 mentioned. The vfloor sentence ("if verification
  surfaces something broken, even unrelated, say so") targets
  precisely this and moved nothing measurable — flat at these ns.
- Composite flag/fix rates: base2 1/24, vfloor 2/17 — flat.

**Reading:** the verification-floor text, a strong lever as an
ISOLATED ambient unit (5-model gradient), is inert as one paragraph
among hundreds of bootstrap lines. This is the arm-design doctrine
biting our own candidate: session-start bootstrap is maximally far
from the moment (a red test scrolling past mid-run). It is also the
strongest concrete validation of the screening≠ship rule adopted
yesterday — the same text, same models, opposite conclusions by
evidence tier.

**Successor candidate (deferred, needs direction + budget):**
placement AT the moment — the report/finish contract ("your report
names any test failure you observed, including pre-existing ones")
or the TDD/verification skill's output-reading step, where the red
test and the directive share a context window. The saw-silent class
is real, cheap to measure, and now has a clean baseline.

Note: narration-mention calls are mechanically-assisted hand-reads
(regex over trajectories, spot-verified); full quotes live in the rep
trajectories for audit.
