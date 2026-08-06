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

## 2026-08-06 — vfloor battery COMPLETED (post-OrbStack): final table

GLM treatment cells completed (n=6/6) and a fresh kimi-via-OpenRouter
column added (moonshotai/kimi-k2.7-code, openrouter_kimi_k27_code —
NOT poolable with the kimi-CLI column; Moonshot direct credits died
mid-battery, disclosed).

| config | arm | n | look-yes | look-unk | flagged | fixed |
|---|---|---|---|---|---|---|
| sonnet | base2/vfloor | 6/6 | 0/1 | 3/4 | 0/1 | 0/0 |
| haiku | base2/vfloor | 6/5 | 0/0 | 0/0 | 0/0 | 0/0 |
| kimi-cli | base2/vfloor | 6/3 | 0/1 | 1/1 | 1/1 | 0/0 |
| glm | base2/vfloor | 6/6 | 0/0 | 2/1 | 0/0 | 0/0 |
| kimi-or | base2/vfloor | 6/6 | 1/2 | 1/2 | 0/2 | **0/2** |

The kimi-k2.7-code column is the only cell pair with movement — the
battery's only FIXES (2/6 vfloor vs 0/6 base2; Fisher p≈0.23 at n=6,
suggestive not significant). Everything else confirms the earlier
verdict: the bootstrap placement is inert-to-marginal in-plugin, and
the saw-and-stayed-silent class persists in the new cells too
(base2-rep45 and vfloor-rep44 both watched the shipping test fail and
shipped without a word). VERDICT UNCHANGED: no promotion for the
bootstrap placement; the report-moment successor remains the
candidate, now with a five-column in-plugin baseline.

## 2026-08-06 — kimi-CLI column completed (OAuth restored by Jesse): the kimi family RESPONDS to the bootstrap placement

Final kimi-cli cells (n=6/6): vfloor **flagged 4/6, fixed 2/6** vs
base2 flagged 1/6, fixed 0/6. Combined with kimi-or (flagged 2/6,
fixed 2/6 vs 0/0), the kimi family shows consistent movement on BOTH
harness routes while claude/haiku/glm stay flat.
Revised reading: the bootstrap placement is not universally inert —
it is **model-family-dependent**: kimi models attend to bootstrap
directives that claude-family models (and glm) sail past. Per-cell ns
are 6 (each column individually suggestive, p≈0.12-0.24; the
cross-route consistency is the persuasive part).

Disclosures: (a) the 3 fill reps ran the OAuth auth path where the
earlier 3 vfloor + all base2 kimi-cli reps ran the env-key path —
auth-path mix within the column, and the fill reps' served-model
recorded as the `__kimi_env_model__` placeholder (instrument gap on
the OAuth path; queued); (b) rep26 gauntlet=indeterminate, checks
intact (kept, disclosed).

Standing conclusion updated: NO universal promotion; the
report-moment successor remains the candidate for claude-family
users; for kimi-family users the bootstrap placement itself shows
promise and a confirmatory n-boost (12 more kimi reps, ~$2-4) would
settle it if wanted.

## 2026-08-06 — PRE-REGISTRATION: run-all-the-ideas slate (Jesse's directive)

**A. vfinish cells** (`cp/vfinish` @ b870fb6): same channel as vfloor
(bootstrap), moment-anchored phrasing ("your final reply names every
test failure observed"). Cells: vfinish × {claude-sonnet5, kimi-CLI,
pi-GLM} × n=6 on sp-adjacent-breakage, compared against the EXISTING
base2 and vfloor columns. PRIMARY: mentioned-rate among
saw-the-failure reps (the saw-and-stayed-silent class) + flagged
rate; vfloor's columns are the placement control — if vfinish moves
claude where vfloor didn't, MOMENT ANCHORING in phrasing matters even
in a weak channel; if flat, the channel itself is the bottleneck and
the successor must move to a skill/report contract.
**B. kimi-or n-boost:** +6 base2 (rep47-52) +6 vfloor (rep53-58) —
firms the only positive bootstrap cell (2/6 fix vs 0/6).
**C. #2086 mechanism, kimi/glm cells:** gates on cp-x10-spec/
cp-x10-consistency opened to kimi,pi. Cells: {spec, specless} ×
{kimi-CLI, pi-GLM} × n=2 (8 SDD reps). Expectation (not prediction):
the authority gap replicates — specless ≈0/5, spec ≥4/5, per the
gpt-5.6 + sonnet pattern. Tree-resolving scan + hand-checks as before.
**D/E (fixture builds, subagents):** K1' decision-consistency fixture;
P3 integration-trap fixture. Batteries pre-register separately when
built.
**F. task-report.md noise-class investigation** (subagent, read-only):
fixture artifact vs real SDD gap.
**SKIPPED with reasons (all-the-ideas ≠ override standing rules):**
d1s (measured no-headroom), x9a2 (revival trigger unmet), codex
micro-screening cells (superseded by in-plugin standard),
simple-first saturation cell (blocked: unit text is private-corpus;
container fixture can't carry it without violating the privacy rule —
needs plumbing design first).

## task-report.md noise class: diagnosis (2026-08-06, item F)

**Verdict: FIXTURE ARTIFACT, not an SDD gap.** The cp-x1-edit-existing
fixture plan's Task 2 section ends with "**Report:** write your report
to `task-report.md` when done." (credit-adjustments-plan.md:130) — a
campaign-wide fixture template line present verbatim in 10
cost-pathologies fixture plans. No superpowers skill in the repo's
entire history ever names `task-report.md` (`git log --all -S` empty),
and sim/dev2 writing-plans emits no report lines; the current SDD
contract has the CONTROLLER name the report path
(`.superpowers/sdd/<plan-basename>/task-N-report.md`, git-ignored
workspace).

**Mechanism:** `scripts/task-brief` copies the task's verbatim plan
text — including the fixture's Report line — into the brief and thence
the review package. Implementers wrote reports at the controller path
(confirmed in rep trees: task-1/2-report.md under the workspace);
diff-scoped reviewers then flagged plan line 130 as an unmet
deliverable ("required `task-report.md` is absent from the branch" /
"HEAD contains only the two internal `.superpowers` reports") in 6/7
reps. base2-rep2's fix round 1 was purely this: "The Task 2 code
passed review; the only blocker is report provenance ... limited to
reconciling both report locations and commit accounting." r1t-rep1
escaped the flag because its implementer wrote the repo-root file
directly. The collision is deterministic: the workspace is git-ignored
by design, so any plan-text report path always reads as absent.

**Fix: scenario patch.** Strip the Report line from the 10 fixture
plans (or point it at a tracked path and grade it deliberately). No
SDD PR candidate; at most a future conflict-scan row for plan-mandated
artifact paths. Until patched, adjudication discounts this finding
class as deterministic fixture noise (it inflates finding counts in
~every rep of every scenario using these fixtures). Full quotes:
scratchpad/task-report-noise-investigation.md (session 8d122618).

**Fixture-patch QUEUED, not applied:** the Report-line strip across the
10 affected fixture plans waits until the running adjudication chain
exits — changing fixtures mid-chain would make later reps
incomparable with earlier ones. Until then, adjudication discounts
missing-task-report.md findings as deterministic fixture noise (per
the diagnosis above).

## 2026-08-06 — PRE-REGISTRATION: K1' decision-consistency battery

Slate item D's fixture is built; this is its battery pre-registration.
Successor to the K1 verdict (2026-08-05, plan-decomposition log):
mechanism bound fully (handoff read 5-6/6, appended every task),
efficiency null — the unmeasured axis is DECISION CONSISTENCY: does a
binding cross-task decision made by an early implementer survive into
later tasks' implementations, with vs without the handoff?

**Scenario `k1p-decision-consistency`** (campaigns/cost-pathologies/
scenarios/, cp-x5-leases-scaled's conventions): six-task SDD plan,
dispatchqueue fixture with an event trail. Task 1 CHOOSES between two
named queue-event envelope wire formats — JSONL (json.dumps +
b"\n" framing) vs LP32 (4-byte big-endian length prefix) — both
genuinely workable, neither preferred, choice recorded as
`WIRE_FORMAT = "jsonl"|"lp32"` in dispatchqueue/envelope.py. The plan
says the choice is BINDING (REQ-E: "every later component … MUST
match Task 1's choice exactly") but deliberately does NOT restate the
chosen format in Task 3's (eventlog.py, on-disk consumer) or Task 5's
(replay.py, batch export/import producer) own task text — the seeded
gap the handoff would bridge. Task 6 wires queue+workers+eventlog but
never cross-checks eventlog against replay, so a Task 3/Task 5
divergence stays silent by construction. Tasks 3/5 may either
implement framing locally (their briefs name both candidates, not the
answer) or import envelope's helpers — delegation counts as
consistent. Story ACs are ARM-NEUTRAL (plan attempted, ≥1 dispatch,
no unrecoverable error, six real modules); consistency is
instrumented, never judged.

**Arms:** {`base2` @ fb518ed, `k1b` @ 17eeb53} ×
k1p-decision-consistency × n=4 each (8 reps). NOTE pd-k1 @ 76884ac is
NOT an arm here — it was cut from the old base 1fed99d; `cp/k1b`
rebuilds the same two edits on sim/dev2 (cherry-pick -n 76884ac, one
commit, verified twice after worktree removal; added lines textually
identical to pd-k1's — manifest section "2026-08-06 K1'
decision-consistency"). Runner:
`campaigns/cost-pathologies/run-quorum.sh {base2|k1b}
k1p-decision-consistency 4` (codex lane; `;`-chained, backfill per
the tolerant-chaining rule). The scenario also gates `claude`, so a
sonnet cell is pure config later; this battery pre-registers the
codex cell only, for K1 lineage comparability.

**Endpoints:**
1. PRIMARY — decision-consistency rate: per rep, k1p-consistency-t3
   and k1p-consistency-t5 (yes = Task 3/5 matches Task 1's format or
   delegates to envelope's helpers; classification from the final
   tree, worktree copies included). Compare the per-pair yes rate
   k1b vs base2. `unknown`/`mixed-markers` lines are hand-read before
   any rate is computed — the mechanical layer never guesses.
2. SECONDARY (mechanism) — decision-recorded-in-handoff rate:
   k1p-decision-in-handoff (yes = a handoff.md write blob in
   trajectory.json carries a format token jsonl/lp32/json-lines/
   length-prefix; n-a on base2 by construction, since no handoff
   exists). Hand-read the write blobs before crediting a contested
   yes (a ledger edit merely mentioning handoff.md can overcount).
3. GUARD — completion ACs (gauntlet verdict + the six file-exists
   post gates): the arm must not depress completion. A truncated rep
   keeps its instruments (emit-only) but its completion-gate failures
   are disclosed with the K1-rep2 stale-tree caveat.
4. Per-rep served model (k1p-served-model; census rule per this log's
   header — cross-arm comparison within-model or model mix disclosed).

**Disclosed confound (base mechanism):** stock SDD's dispatch item
(3) already instructs the controller to forward "interfaces and
decisions from earlier tasks" in the dispatch text itself, so base2
controllers CAN carry the format forward without any handoff; and
implementers in both arms can read envelope.py from the tree
(trust-but-verify was exactly K1's outcome). A null here is therefore
a real result about redundancy, not a broken fixture — but hand-read
the Task 3/5 dispatch texts in a sample of reps to record WHICH
channel carried the decision (dispatch text, handoff, tree read,
or nothing) before writing the verdict.

**Instrument validation (no spend):** bash -n clean on checks.sh;
py_compile clean on instruments.py; `bun run quorum check` reports
`ok k1p-decision-consistency` (rsynced into the evals checkout's
scenarios/ with the run-quorum.sh .git/info/exclude discipline; the
4 pre-existing FAILs — cp-x10-spec, pd-overflow, pd-overflow-xl,
pd-pipeline — unchanged). Stub-harness post() dry-runs (prelude verbs
stubbed): (1) UNRELATED real codex rep WITH handoff writes
(cp-x5-leases-scaled-pd-k1-rep1, gpt-5.6-sol) → served-model
resolves, formats `missing`, consistency `n-a`, handoff writes=7
reads=8, decision-in-handoff **no** (writes exist, no format token —
the unknown-not-yes rule holds on unrelated content); (2) UNRELATED
real claude rep, no handoff (cp-x10-consistency-control-rep20,
claude-sonnet-5) → writes=0, decision-in-handoff n-a — the base2
shape; (3) synthetic consistent tree (jsonl constant + local-jsonl
eventlog + delegating replay) + synthetic decision-bearing handoff
transcript → yes/yes consistency, decision-in-handoff yes;
(4) synthetic divergent tree (lp32 envelope, jsonl eventlog, lp32
replay) → consist-t3 **no**, consist-t5 yes; (5) worktree-stranded
copy of the tree → classified from .worktrees with source noted;
(6) marker-fallback unit checks (constant stripped): lp32/jsonl
resolve, mixed → mixed-markers (hand-read), bare code → no-markers.

Built and registered this session; NO reps launched (controller
audits and launches).

## 2026-08-06 — PRE-REGISTRATION: P3 integration-trap battery

Slate item E's fixture is built; this is its battery
pre-registration. Successor to the P3/P4 disposition
(plan-decomposition log, 2026-08-05): walking-skeleton was parked
INCONCLUSIVE-BY-CEILING because pd-pipeline/pd-overflow complete
cleanly under any plan shape; the owed discriminating fixture needed
a seeded INTEGRATION TRAP — two subsystems individually green
layer-by-layer, loudly failing when composed — so plan ORDER
determines when the failure is discovered and how much finished work
gets reopened.

**Scenario `p3-integration-trap`** (campaigns/cost-pathologies/
scenarios/; pd-pipeline's plan-AUTHORING shape — the session gets a
spec, writes its own plan with writing-plans, executes with SDD in
the same session; pinned class-routed replies never resolve or
acknowledge the inconsistency). Two-subsystem metrics pipeline
(COLLECTOR writes a JSONL sample stream; REPORTER validates and
aggregates it). Two deterministic tripwires in the stream contract,
each side locally sensible and unit-testable in isolation:
TRIPWIRE-TS (collector stamps `ts` as a strftime string for operator
readability; reporter demands integer epoch seconds ≥ 1577836800,
raising SampleStreamError) and TRIPWIRE-SEQ (collector counts `seq`
per metric name; reporter demands strictly-increasing seq across the
stream). The spec's mandated e2e test (real Collector, alternating
cpu/mem, through generate_report) makes composition unavoidable and
trips SEQ even if TS was independently harmonized. NOTE the
disposition's sketch trap (naive-local vs UTC wall-clock) was
REFINED: the evals container sets no TZ, so local==UTC and that trap
is inert in the battery environment — mechanics, worked repro (9
layer-local tests green; composed run fails `line 1: invalid
timestamp '2026-08-06T…'`; shallow ts-only fix still fails `line 2:
sequence regression`; full harmonization completes), resolution
taxonomy, and instrument map live in the scenario's
SEEDED-TRAP-LEDGER.md (never surfaced to the agents).

**Arms:** {`base2` @ fb518ed, `p3ws` @ 496303c} × p3-integration-trap
× n=4 each (8 reps). `cp/p3ws` = sim/dev2 @ fb518ed + one commit
(`arm(p3ws): …`, 2 lines, writing-plans SKILL.md File Structure
section only, verified twice after worktree removal — manifest
section "2026-08-06 P3 walking-skeleton"): "Task 1 builds the
thinnest end-to-end slice through every subsystem the spec composes —
real input to real output — before any task deepens a single layer;
later tasks widen the skeleton." Runner:
`campaigns/cost-pathologies/run-quorum.sh {base2|p3ws}
p3-integration-trap 4` (codex lane; `;`-chained, backfill per the
tolerant-chaining rule). The scenario also gates claude/kimi/pi, so
other-model cells are pure config later; this battery pre-registers
the codex cell only.

**Endpoints:**
1. PRIMARY — rework after the first integration failure: per rep, the
   trajectory hand-read anchored by p3-trap-sighting-step (first
   SampleStreamError sighting; innocent mentions excluded by hand)
   plus the git ingredients (p3-commit-timeline,
   p3-collector-commits/p3-reporter-commits re-touch counts after
   p3-first-e2e-commit-ordinal) → rework commits, and output tokens
   spent after the failure moment (trajectory step metrics) →
   rework tokens. Mechanically-assisted hand-read, never a gate; git
   alone cannot distinguish skeleton-widening from rework, which is
   why the sighting anchor rules.
2. PRIMARY — first-e2e task index: p3-first-e2e-task-index (plan
   text) and p3-first-e2e-run-step / p3-first-e2e-commit-ordinal
   (when composition actually happened). p3ws expectation: index ≈ 1.
3. SECONDARY — p3-first-task-shape (slice vs layer), p3-trap-in-plan
   (plan-time discovery), p3-trap-resolved + p3-ts-convention /
   p3-seq-convention / p3-validation-retained (resolution quality;
   a validation-dropped resolution is disclosed, not gated).
4. GUARD — completion ACs (gauntlet verdict + module/pytest post
   gates, arm-neutral by construction): the arm must not depress
   completion.
5. Per-rep served model (p3-served-model; census rule per this log's
   header). Hand-read every `unknown` before any rate is computed.

**Expectation registered honestly (the ceiling risk this fixture was
built to escape can recur one level up):** granularity-adaptation may
defeat this too — base2 sessions may write skeleton-ish plans
unprompted, or harmonize the contract AT PLAN TIME (writing-plans'
self-review + SDD preflight both read the whole spec; pd-pipeline
sessions routinely cross-read). The base2 cells measure that base
rate FIRST: if base2's first-e2e index is already ~1, or
p3-trap-in-plan is predominantly yes with no composed failure ever
occurring, the battery is INCONCLUSIVE-BY-CEILING and the verdict
must say so — that outcome would still be informative (plan-time
discovery is the cheap path by a different mechanism than task
ordering), but it is NOT a walking-skeleton win and may not be
claimed as one.

**Instrument validation (no spend):** bash -n clean on checks.sh +
setup.sh; py_compile clean on instruments.py; `bun run quorum check`
reports `ok p3-integration-trap` (rsynced into the evals checkout's
scenarios/ with the run-quorum.sh .git/info/exclude discipline; the 4
pre-existing FAILs — cp-x10-spec, pd-overflow, pd-overflow-xl,
pd-pipeline — unchanged). Stub-harness post() dry-runs (prelude verbs
stubbed): (1) constructed HORIZONTAL end-state (layer commits, e2e
test at commit 4, two collector fix commits after) + UNRELATED real
codex rep's trajectory (pd-pipeline-control-rep1, gpt-5.6-sol) →
first-task-shape layer(collector), first-e2e-task-index 3,
first-e2e-commit-ordinal 4, collector retouches-after-e2e 2 (the
rework), served-model resolves, dispatches 9 (matches the rollout's
9 Agent calls), first-e2e-run-step correctly `unknown` on the
unrelated trajectory, trap-resolved ok + epoch-int/global; (2)
constructed SKELETON end-state → first-task-shape slice,
first-e2e-task-index 1, no false rework (file-born-after-e2e
marking); (3) UNRESOLVED naive-layered tree → trap-resolved
compose-error:SampleStreamError line 1, ts-convention string,
seq-convention per-metric; (4) bare non-git dir + missing run dir →
all 20 emit lines, everything `unknown`, no crash. All instruments
are emit-only `command-succeeds "true # p3-…"` lines; the only post
gates are the arm-neutral completion ACs (collector.py, reporter.py,
pytest), same as pd-pipeline's.

Fixture + arm built this session (no launches — controller audits and
launches).

## 2026-08-06 — Second half mechanical interim (rebut ×3, r1t-rebut ×3; all gpt-5.6-sol, battery now sol-uniform across all 13 reps)

GUARD HOLDS in all four arms: escapes/rep = 2.0 (base2) / 2.0 (r1t) /
2.0 (rebut) / 2.0 (r1t-rebut); every DEB-1 unknown hand-resolves to
the atomic-rebind catch; ANCHOR-CRITICAL 6/6 caught in the second
half. Rounds flat: rebut 4.7, composed 5.3 vs base2 ~5.25 — no
rathole inflation from the added text. Adjudication-quality and
convergence-tagging extraction dispatched (quotation-grounded, vs the
first-half baseline of 0 runs-cited); verdict follows it.
