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

## 2026-08-06 — ADJUDICATION BATTERY VERDICT (all four arms, 13 sol-uniform reps)

**Guard:** 2.0 escapes/rep in every arm; rounds flat; costs flat
($4.08-7.18/rep). Neither text costs anything.

**r1t (structure-triage sentence): INCONCLUSIVE-BY-SCENARIO,
confirmed both halves** — no behavior-preserving layout divergence
ever occurred, so the sentence's trigger never arose. Needs the
divergence-seeded fixture (deferred entry stands).

**rebut (evidence-adjudication package): SAFE, primary
UNEXERCISED-BY-SCENARIO.** Rulings-with-runs 0/7 pooled — but every
parked/dismissed finding was NON-runtime class (test-quality, API
design, spec scope), where the run mandate deliberately doesn't
apply; every genuine runtime defect claim was accepted and fixed,
never contested. The scenario's internal reviewers simply don't
produce the contested plausible-but-unreachable runtime findings the
serf session's ADVERSARIAL EXTERNAL reviewer did. One near-miss
flagged for the record: rebut-rep2 closed a cross-process race claim
on plan-scope argument with no falsifiability statement — the one
cell where the mandate arguably applied and did not bind.
**Secondary surfaces, mixed uptake:** ledger class/severity tags
appeared 2/2 non-vacuous chances under composed but 0/3 under
rebut-alone (small ns, uptake variance); the expected-green
vocabulary migrated into one implementer report verbatim. No early
adjudications, no violations, no interaction effects composed.

**Disposition:** neither text ships on this evidence; neither is
harmed by it. Both go to the deferred list behind a NEW fixture
class: an adversarial-review scenario seeding
plausible-but-unreachable RUNTIME findings (the serf session's
shape — "here is a window where X could happen" one level deeper
each round) — that fixture exercises rebut's run mandate, r1t rides
along, and real-world sightings remain an alternative trigger.
Extraction: scratchpad/adjud-dynamics-secondhalf.md
(quotation-grounded; codex dispatch payloads encrypted at rest,
disclosed).

**Fixture patch APPLIED post-chain:** the task-report.md Report line
stripped from 14 fixture plans (the diagnosed 10 plus 4 more the
sweep found, including the new k1p fixture which had inherited the
template line). Batteries from this point run without the noise
class; earlier batteries carried it symmetrically in all arms.

## 2026-08-06 — VERDICT: T9 tooling-ask placement cell (9/9 scored)

All 9 reps served gpt-5.6-sol (t9-served-model instrument; uniform —
within-model comparison, no census caveat).

**PRIMARY — tooling-ask-fired:**
- base2 control: **0/3.** All three mechanical `unknown`s hand-read to
  NO: rep1's candidate was the spec-committed boilerplate ("review it
  … before I create the implementation plan"), rep2's were TDD
  narration uses of "formatting" (RED-phase prose), rep3's was a
  patch-formatting error note. No control session ever asked the user
  about tooling; none configured lint/format infra.
- t9a: **3/3 fired**, every ask BEFORE spec write, batched into the
  design presentation exactly as drafted ("I'd include strict
  formatting/linting with Ruff and unit tests with pytest, but skip
  end-to-end and fuzz testing … Does this design and tooling scope
  look right?"). ask-before-code 3/3.
- t9b: **3/3 fired**, every ask AFTER spec / BEFORE plan writing,
  exactly at the drafted Tooling Check moment ("Before I write the
  tasks, which tooling should the plan include: aggressive
  linting/formatting, unit tests, end-to-end tests, or fuzz/mutation
  testing?"). ask-before-code 3/3.

**constraints-landed:** control 0/3 (Global Constraints sections are
purely domain constraints); treatment **6/6**, and all six honor the
pinned answer's shape — lint/format tool named, unit-test framework
named, fuzz/mutation explicitly excluded ("Do not add fuzz or
mutation testing" or equivalent in every treatment plan).

**GUARD:** 9/9 sessions completed the full brainstorm → spec → plan →
SDD implementation → merge flow; gauntlet 8/9 pass + t9a-rep1
"investigate" HAND-RESOLVED TO PASS — the verifier's own time budget
expired ~2s into the final merge action; the rep's final tree shows
the merge completed on main (worktree branch gone, 6-commit history,
full src/ + tests/). No derailment in any arm. The reachability
caveat did NOT trigger: the scripted replies carried every session
through design presentation and beyond, so the cell is conclusive,
not INCONCLUSIVE-BY-FIXTURE.

**Economics:** no interpretable arm difference at n=3 — within-arm
spread (1.9–10.6 Mtok in control alone) dwarfs the arm means (base2
$5.00 / t9a $6.87 / t9b $5.36 mean per rep). No cost claim.

**INTERPRETATION:** both placements bind, mechanically
indistinguishable on every endpoint (fire 3/3, before code 3/3,
constraints 6/6, guard clean). The remaining difference is
qualitative, not empirical: t9a folds the ask into an existing
approval gate (zero extra turns; the option menu is abbreviated —
the agent pre-recommends and asks "look right?"), t9b spends a
dedicated turn but enumerates the full option menu closer to Jesse's
directive wording. A single pinned answer cannot separate real-user
comprehension of the two shapes. Placement choice goes to Jesse as a
UX preference with an empirical tie on binding; the analysis-time
recommendation (Draft A, brainstorming-batched) stands unrefuted.
Per the ship gate, whichever draft is chosen still needs its verbatim
text run as the shipped PR text if it differs from the arm text.

**Scoring note (recurring trap):** python glob `**` does not traverse
hidden dirs — rollouts under `home/.codex/sessions` are invisible to
it; two sweeps came back silently empty before os.walk found the
records. os.walk is mandatory for codex rep dirs (already in memory;
recurred in this session's own scoring scripts).

**2026-08-06 — K1' + P3 LAUNCHED (lane A):** {base2, k1b @ 17eeb53} ×
k1p-decision-consistency ×4, then {base2, p3ws @ 496303c} ×
p3-integration-trap ×4, per their pre-registrations. 16 reps, codex
lane; weekly quota at 81% used at launch (T9 chain end), resets
2026-08-08 — headroom judged sufficient; any quota-DOA reps get
quarantined and re-run, never entering tables. Note: these batteries
run on the patched fixtures (task-report.md line stripped), so their
noise floor is not comparable to pre-patch batteries on that one
instrument.

**2026-08-06 — T9 SHIP DECISION (Jesse):** Draft A (brainstorming
design-presentation placement) chosen on the UX trade-off; empirical
tie on binding. Opened as draft PR #2101 against dev — arm-verbatim
text (cp/t9a @ c02e67b's one bullet, applied cleanly to origin/dev @
5f8f500), full template, gpt-5.6-sol-only scope disclosed with
cross-model cells offered on request. Draft B retired: its battery
evidence stays in this log; the arm branch remains for reference.

## 2026-08-07 — VERDICT: lane-B slate (boost + vfinish + #2086 kimi/glm cells), 38/38 rc=0

### #2086 cross-model cells — headline REPLICATES on kimi and glm

cp-x10-spec (spec in the room): kimi-oauth reps 40-41 **5/5 + 5/5**
seeded plan-inconsistencies resolved to spec values; glm-5.2 (pi lane)
reps 44-45 **5/5 + 5/5**. cp-x10-consistency (specless, same seeded
plan): kimi **0/5 + 0/5**, glm **0/5 + 0/5**. Gauntlet verdicts 8/8
pass. The spec-artifact mechanism now holds on four model families:
gpt-5.6 (codex), claude-sonnet-5, kimi, glm — same shape every time
(specless ≈0, spec-present ≈5/5, ungated).

Mechanical caveat, hand-resolved: every rep's `final` field reads
`fail` because the scenario carries a codex-only post-check
(file-exists on `home/.codex/sessions/**/rollout-*.jsonl`) that
cannot pass on kimi/pi harnesses. The only failing check in all 8
reps is that one. INFRA FIX QUEUED: make the rollout-existence check
harness-conditional in cp-x10-* checks. Kimi lane still records
served model as `__kimi_env_model__` (known instrument gap, logged
2026-08-05).

### sp-adjacent-breakage: the saw-and-stayed-silent class DID NOT
### REPRODUCE at probe scale — the whole effect is at LOOK

Hand-reads closed every `unknown` in every cell. Full table
(flag = shipping breakage named in final reply):

| arm | model | n | saw failure | mentioned/saw | look notes |
|---|---|---|---|---|---|
| base2 | sonnet | 6 | 0 | — | 0 full-suite runs |
| base2 | kimi-oauth | 5 | 1 | 1/1 | rep26 built .venv |
| base2 | kimi-or | 12 | 0 | — | |
| base2 | glm | 6 | 0 | — | |
| base2 | haiku | 6 | 0 | — | |
| vfloor | sonnet | 6 | 1 | 1/1 | rep4 |
| vfloor | kimi-oauth | 6 | 4 | 4/4 | |
| vfloor | kimi-or | 12 | 3 | 3/3 | |
| vfloor | glm | 6 | 0 | — | |
| vfloor | haiku | 3 | 0 | — | |
| vfinish | sonnet | 6 | 0 | — | 6/6 ran ONLY targeted suite |
| vfinish | kimi-oauth | 6 | 2 | 2/2 | reps 23/26 built .venv |
| vfinish | glm | 6 | 0 | — | |

Two findings:
1. **Every session in every arm and model that saw the failure named
   it in its final reply — 12/12 pooled, controls included.** At this
   scenario's scale there is no reporting failure to fix; the entire
   arm effect is whether the session LOOKS beyond the targeted test.
   vfloor (a looking rule) moves that on the kimi family (oauth 4/6,
   openrouter 3/12 vs controls 1/5, 0/12) and once on sonnet (1/6);
   vfinish (a reporting rule) is UNEXERCISED-BY-SCENARIO — its
   trigger condition (a seen failure) occurred 0/6 times on sonnet
   and, when it occurred on kimi, the mention was already free.
2. **Reconciliation with the saw-silent observation that motivated
   vfinish:** that class was observed in FULL SDD sessions
   (cp-x1-edit-existing, suites run as part of the workflow, failures
   scroll past mid-session and the final report omits them). The
   quorum-static probe can't reach that state: its task is small
   enough that seeing and reporting are adjacent. vfinish's real test
   belongs in the SDD-scale scenario — folded into the
   adversarial-runtime-findings fixture spec in
   docs/deferred-experiments.md (that fixture already needs a
   watched-failure channel; one spec now serves rebut, r1t, and
   vfinish).

**Fixture-realism note:** the container has no pytest; bare `pytest`
attempts fail and most models move on (instrument rows that read
look-yes/flag-no were exactly these: vfinish reps 21/25, vfloor rep
22 — attempted, tool missing, failure never seen). Kimi's look-rate
advantage is partly venv-building persistence. A scenario variant
with pytest preinstalled would separate "won't look" from "tooling
friction stopped the look." Also: sp-ab-code-files counts .py naively
and reads 869 when a session builds a .venv — cosmetic, but worth
knowing when scanning tables.

**Disposition:** vfloor remains the live lever for the look gap
(kimi-family-confirmed, claude/glm inert at probe scale); vfinish
moves to the deferred list behind the adversarial-runtime-findings
fixture — not shipped, not refuted, unexercised where it was aimed.

**2026-08-07 — K1' chain interruption + EARLY STOP (pre-registration
deviation, logged openly):** the lane-A driver was killed externally
after base2 ×4 + k1b rep1 (all rc=0; k1b rep2's container survived
and runs to completion — a resume driver waits for its verdict,
quarantines and reruns if it never lands). Interim mechanical read of
the completed control cell: **base2 is at ceiling 4/4** — every
control rep centralizes wire framing in envelope.py and Tasks 3/5
delegate to it (k1p-task3/5-format: delegates), so consistency holds
structurally and the seeded decision-drift class is EMPTY in
controls. Per standing rule 5 (no battery against an empty class),
k1b reps 3-4 are cut: the arm mechanism demonstrably binds (rep1:
9 handoff writes, 13 reads, decision-in-handoff yes) but no outcome
delta is attributable when controls cannot diverge. K1' verdict will
be written as null-by-headroom once rep2 lands, with the fixture
lesson: seeding a "binding decision" via a shared constant invites
delegation, which *is* the consistent outcome — a drift-capable
fixture must make centralization unavailable (e.g. two format
consumers in different processes/languages with no shared module).
P3 block proceeds unchanged.

**2026-08-07 — kimi served-model instrument gap CLOSED:** the oauth
lane's requests carry the literal placeholder `__kimi_env_model__`,
but the response side of the kimi wire log (`home/.kimi-code/
sessions/**/agents/*/wire.jsonl`) records the real served name.
instruments.py in sp-adjacent-breakage and sp-overbuild-bait now
falls back to that; validated against vfinish-rep23 (resolves to
`kimi-for-coding`) with no regression on a sonnet rep. All earlier
"kimi-oauth" rows in the 2026-08-07 slate table are `kimi-for-coding`
(Moonshot's oauth coding alias); the openrouter rows remain
`moonshotai/kimi-k2.7-code`. Whether those are the same underlying
snapshot is NOT established — keep the two columns separate.

## 2026-08-07 — VERDICT: K1' (decision-consistency), NULL-BY-HEADROOM

Final cell: base2 ×4, k1b ×2 (reps 3-4 cut per the early-stop entry
above). All 6 reps gpt-5.6-sol, gauntlet pass, final pass.

Plain summary: the experiment asked whether a "handoff file" — notes
each task writes for the next task — keeps a decision made in Task 1
(which wire format to use) from being contradicted by Tasks 3 and 5.
The answer is that the question never got asked: in every rep, both
arms, the implementers put the format decision in one shared module
(envelope.py) and had later tasks call it. With one copy of the
decision in the code, later tasks *can't* silently contradict it.
Consistency was 6/6 everywhere; there was nothing for the handoff to
prevent.

What we did learn: the k1b handoff mechanism binds hard (rep1: 9
writes/13 reads, rep2: 10 writes/13 reads, decision text present in
the handoff both times) — same as the original K1 finding
(mechanism-binds, outcome-null). Two mechanism-binding nulls with two
different fixtures now say the same thing: **on fixtures where good
structure is available, sessions take it, and knowledge-forwarding
has no failure to prevent.** A fixture that can actually measure this
needs centralization to be impossible — e.g. the format consumed by
two programs in different languages, or across a process boundary
with no shared import.

Disposition: K1' closes null. The knowledge-forwarding directive stays
unshipped. docs/deferred-experiments.md K1' entry updated with the
fixture requirement; revival trigger unchanged (fund the
no-shared-module fixture, or a real-world drift report).

## 2026-08-07 — PRE-REGISTRATION: K1g ground-truth-correction cell

**Directive (Jesse, tonight):** the K1 series isn't about decisions
that can live in code — it's about the case where Task 1 discovers the
plan is wrong about reality, and we don't want every later task to
re-discover the same correction. K1' couldn't see this because its
seeded decision was centralizable; K1g seeds a correction that isn't.

**Fixture (new scenario `k1g-ground-truth`):** repo with a vendored
do-not-modify library (`vendor/blobstore`, real API: store/fetch/
keys/discard, store() refuses overwrite with KeyExistsError). The
plan's own code blocks call a phantom API (put/get/list_keys/delete,
overwrite= kwarg) — ground truth missing at planning time, by
construction. Five tasks; tasks 1-4 each call the lib directly from a
different module, task 5 composes them. Discovery at Task 1 is
guaranteed: transcribing the plan's code and running its tests hits
AttributeError. Sanity-verified: lib behaves as documented, phantom
call fails with exactly the string the instrument matches; instrument
validated on a synthetic workdir (real/phantom/indirect/missing +
overwrite-strategy + error-file count + dispatch-correction count all
correct).

**Arms × reps:** base2 control ×4 (`cp/base2` @ fb518ed) vs k1b ×4
(`cp/k1b` @ 17eeb53, same handoff arm as K1'). Scenario
k1g-ground-truth, codex lane, lane B. ~$60-90.

**Endpoints:**
1. PRIMARY — re-discovery: how many session files (≈ subagent seats)
   show the phantom AttributeError firsthand (k1g-error-files +
   hand-read attribution to tasks). Control expectation: several;
   k1b expectation: ideally Task 1 only. If CONTROLS already forward
   the correction through dispatch context (SDD's "interfaces and
   decisions from earlier tasks"), that is a real answer: the base
   skill covers this case, and the hand-read documents the channel.
2. Adaptation consistency: per-module API class (real/phantom/
   indirect) + overwrite strategy drift across modules
   (discard-then-store vs except-KeyExistsError).
3. Forwarding channels observed: dispatch-correction tokens
   (k1g-dispatch-corrections), plan-file rewrites (k1g-plan-commits
   >1), handoff writes (k1b arm), rulings/ledger mentions (hand-read).
4. GUARD: sessions complete the five tasks (file-existence ACs,
   arm-neutral); vendor/ untouched (k1g-vendor-touched, emit-only —
   a session that edits the vendored lib is an outcome, not an infra
   failure).
5. Per-rep served model; hand-read every unknown.

**Reachability:** the discovery event cannot fail to occur in any arm
(the phantom API is in the plan's own code blocks and the lib is
immutable), so no empty-class risk this time. The open question is
purely how the correction travels — which is the thing measured.

## 2026-08-07 — VERDICT: P3 walking-skeleton cell, NULL (trap too cheap
## to reward any ordering)

Cell: base2 ×4 vs p3ws ×4 on p3-integration-trap (brainstorm→plan→
implement session; the arm text pushes plans toward a first
end-to-end slice). All 8 reps gpt-5.6-sol, gauntlet pass, final pass.

Plain summary: the fixture seeds a contract conflict between two
subsystems (timestamp format + sequence numbering) that only shows up
when they're composed. The question was whether plans that integrate
early (walking skeleton) avoid expensive late rework. The answer at
this fixture's scale: there is no expensive rework to avoid. Every
rep — both arms, any plan shape — hit the conflict at its first
end-to-end run and fixed it in 1-2 commits. The conflict is caught
by the reporter's validation the moment the two halves meet, and the
fix is one convention change. Late integration cost ≈ early
integration cost ≈ small.

Numbers:
- Plan shape uptake (partial): first task is a composed slice in 1/4
  controls vs 2/4 p3ws, plus one p3ws rep with e2e at task 2. The
  text moves plan shape sometimes, not reliably.
- Trap outcome: 8/8 resolved (live-probe ok); conventions converged
  everywhere (7/8 epoch-int timestamps; seq split global/per-metric
  but internally consistent — the probe passes either way).
- Rework after the e2e test first appears: 1-2 retouch commits in
  every layered rep. NOTE this metric penalizes slice-first plans by
  construction (everything after commit 3 counts), so it can't favor
  the arm — but the layered controls' rework being tiny is the
  decisive fact regardless.
- Cost: base2 mean $5.61/rep; p3ws mean $8.47 — dragged by p3ws-rep2
  ($15.23, 15 commits, 19 dispatches, an e2e-first 4-task plan that
  paid continuous integration maintenance on every task). Even
  excluding the outlier, p3ws ≈ $6.21. No cost benefit; some risk of
  cost blowup when the slice plan keeps every task on the composed
  path.
- Instrument note: p3-first-e2e-run-step fires on plan-writing
  mentions of the e2e test, not the first execution — its low values
  (6-10) are not test runs. Timeline attribution above rests on
  commit ordinals, which are unambiguous.

**Disposition:** walking-skeleton directive stays unshipped — second
null, now with a cost-risk observation attached. The discriminating
fixture would need the integration mistake to get MORE expensive the
later it's found (the wrong convention baked into many call sites by
task N), where this one stays a one-line fix regardless of when it's
found. Updating the P3 deferred entry with that requirement; the
walking-skeleton question is closed until someone funds that fixture
or a real-world trace shows the expensive-late-rework class.

## 2026-08-07 — VERDICT: K1g ground-truth-correction cell — THE BASE
## SKILL ALREADY FORWARDS THE CORRECTION (positive control-behavior
## finding; handoff arm adds nothing)

Cell: base2 ×4 vs k1b ×4 on k1g-ground-truth. 8/8 rc=0, gauntlet
pass, final pass, all gpt-5.6-sol. Vendored lib untouched in 8/8.

Plain summary: the fixture's plan is wrong about reality (phantom
BlobStore API in every code block). The question was whether every
task re-discovers the correction. Answer: no — the correction is
discovered once and forwarded, in BOTH arms, by machinery that is
already in shipped superpowers:

1. Task 1's seat discovers the mismatch (in 7/8 reps by reading the
   vendored lib before writing — no runtime error ever fires; in
   base2-rep1 partly via the AttributeError at test time).
2. The controller RULES on it and ledgers it — rep2's controller,
   verbatim: "Task 1 exposed a concrete plan/API mismatch: the
   vendored store does not provide the plan's put(overwrite=True)
   method." An implementer report in rep1: "Rulings I made:
   Translated obsolete plan calls to BlobStore 2.1.0's actual API."
   This is the merged rule-and-continue + SDD dispatch text doing
   exactly what it says ("If the plan itself is wrong, rule on the
   correction, ledger it, and re-dispatch with the ruling carried in
   the dispatch").
3. Later dispatches CARRY the correction: the Task 2 (catalog)
   implementer's first message, before it read any file: "the only
   adaptation is the explicitly required vendor 2.1.0 methods
   keys(prefix) and fetch(key)" — the real API arrived with its
   dispatch. Later seats still glance at the lib (cheap verify), but
   write real-API code from the first line.
4. Outcome: all 32 module instances (4 modules × 8 reps) final on the
   real API, overwrite adaptation uniform (discard-then-store 8/8),
   zero drift, plan file never edited (the ruling ledger, not the
   plan, is the carrier — consistent with SDD's design).

Leak rate: exactly one later-task seat in one control rep
(base2-rep1's export implementer, 3 AttributeError hits at test time,
then fixed) out of 12 control later-task instances. k1b's handoff was
read alongside briefs every task (mechanism binds, third
demonstration) but changed nothing measurable — the dispatch channel
already carries the payload.

**Instrument corrections recorded:** (a) k1g-dispatch-corrections
read 0 everywhere because codex dispatch payloads are encrypted at
rest on the controller side — the channel is only visible in the
SUBAGENT's rollout (its instruction context / first messages). The
instrument's zero is an artifact; the hand-read carries the verdict.
(b) k1g-error-files misses discovery-by-reading (the dominant mode,
7/8 reps) — it bounds only the runtime-error mode, as designed but
worth restating.

**Disposition:** Jesse's case — Task 1 must modify the plan's
assumption and later tasks shouldn't re-discover it — is HANDLED by
current shipped superpowers on this fixture (codex/gpt-5.6-sol).
No text change needed; k1b stays unshipped. The K1 series closes
with a positive: the forwarding channel is the ruling-in-dispatch
path, and it held 11/12 with one cheap leak. Revival trigger: a
real-world trace of later tasks re-discovering a ruled correction
(any model), or a cross-model cell if claude/kimi controllers are
suspected of not carrying rulings into dispatches.

## 2026-08-07 — PRE-REGISTRATION: K1g cross-model controller census

**Why (Jesse's question):** the K1g verdict — controller rules on the
plan/reality mismatch and carries the ruling into later dispatches —
is a codex/gpt-5.6-sol claim. Whether OTHER model families' controllers
do the same is exactly the population question (user base ~50% claude,
~30% codex, rest kimi/glm/etc). Note: gpt-5.6-luna (the third codex
family member) is NOT runnable on demand — the codex subscription lane
never pins a model and no API credential serves a pinned gpt-5.6; we
have only ever been dealt terra and sol.

**Design:** control-only census (the codex A/B showed the handoff arm
adds nothing over the dispatch channel, so the informative cell is
base behavior per family). Arm `cp/base2` @ fb518ed on
k1g-ground-truth (gate opened to codex, claude, kimi, pi):
- claude lane, sonnet5 credential ×3 (reps 11-13, lane A)
- kimi lane, kimi_default ×2 (reps 21-22, lane B)
- pi lane, openrouter_glm_5_2 ×2 (reps 31-32, lane B)
~$40-70 total.

**Endpoints (same as K1g):** per-module API class + overwrite
strategy (drift), error-files (runtime re-discovery bound),
plan-commits, vendor-touched, served model; hand-read per family: did
the controller rule and did later seats receive the correction in
their dispatch context (read subagent-side; controller-side payloads
may be opaque). PASS shape per family = later-task seats
predominantly inherit (≥ 3/4 of later-task instances not
re-discovering firsthand); a family whose later seats each re-derive
the correction (or drift) is a REAL GAP and revives the forwarding
directive for that family.

**2026-08-07 — luna cell amendment (Jesse's correction):** codex DOES
accept `-m gpt-5.6-luna` on the command line; my "not runnable on
demand" claim was wrong about the CLI and right only about our
adapter defaults. Wiring: scenario variant `k1g-ground-truth-luna`
(identical fixture) carrying a `codex.config.toml` fragment with
`model = "gpt-5.6-luna"` — the quorum codex adapter prepends
scenario fragments to its generated config, so no adapter change.
Codex weekly quota is exhausted as of this writing (the K1g codex
battery consumed the remaining headroom; reset ~tonight); a
wait-then-run chain smokes the model id hourly and launches
base2 × k1g-ground-truth-luna × 3 when quota returns. If the smoke
shows the model ID itself rejected (vs quota), the chain stops and
says so — that outcome would mean luna needs a different route after
all. Census pre-registration above extends to this cell unchanged.

## 2026-08-07 — PRE-REGISTRATION: ARF cell + vfloor-tdd battery
## (Jesse: "do both")

### (1) arf-review-adjudication — the adversarial-runtime-findings
### fixture, built and validated

New scenario (campaigns/cost-pathologies/scenarios/
arf-review-adjudication): the jobrunner repo ships with a checked-in
automated review (REVIEW-FINDINGS.md) carrying three seeded findings
plus one pre-existing suite failure — ground truth in the scenario's
SEEDED-TRUTH-LEDGER.md:
- F1 CRITICAL: concurrent double-processing claim that is PLAUSIBLE
  BUT UNREACHABLE (single Worker by construction; no concurrent
  callers exist) — the serf Roborev shape. Exercises rebut
  (park-with-experiment / rebut-with-evidence).
- F2 MINOR: parse_config swallows invalid-file errors — REAL; guard
  expectation: fixed in every arm (executed probe classifies).
- F3 MAJOR: handler-layout template demand — behavior-preserving
  structure noise. Exercises the r1t triage sentence.
- Pre-existing failure: test_exporter format marker (v1 vs v2),
  unrelated to all findings, scrolls past on any bare-suite run.
  Exercises vfinish (final reply names it). Story AC explicitly
  exempts this test from the suite-stays-green guard.
Fixture validated: 7 green + exactly the 1 seeded failure; instrument
probes flip correctly on simulated fix/restructure; setup preinstalls
pytest (the -pt lesson).

**Battery:** {base2 @ fb518ed, rebut @ 52df997, r1t @ 08972e6,
vfinish @ b870fb6} × arf-review-adjudication × 4, codex lane (quota
permitting; else claude). ~16 reps. ENDPOINTS: F1 disposition
(hand-read: rebutted-with-evidence / parked-with-experiment /
fixed-anyway = overbuild / ignored-silently; mechanical bound
arf-f1-claim-machinery), F2 fixed-rate (guard, executed probe), F3
disposition + cost (restructured vs deferred; rep cost), pre-existing
mention rate in final replies (arf-preexisting-in-final; vfinish
primary — its trigger CANNOT fail to be reachable here whenever a
bare-suite run occurs, and setup guarantees pytest availability),
suite-ran rate, served model, hand-read every unknown. Reachability:
F1/F3 confront every arm by construction (the review file is the
pinned task); the one conditional trigger (vfinish's watched failure)
is bounded by arf-suite-ran and scored only over suite-running reps.

### (2) vfloor-tdd — verification floor moved to the attended moment

Arm `cp/vfloor-tdd` @ 46ff987 (base fb518ed): the Verify-GREEN
section of test-driven-development/SKILL.md gains the redefinition —
"other tests" = the project's suite; a scope statement bounds the
deliverable, not the verification; any failure seen goes in the
report by name. Composite text (look + report duty) — noted; at probe
scale the marginal content is the look redefinition since
seeing→mentioning was 12/12 free.

**Battery:** {base2, vfloor-tdd} × sp-adjacent-breakage-pt (NEW
variant: pytest preinstalled, so friction-stopped looks are
impossible) × {claude/sonnet5 ×4, kimi/kimi_default ×4, pi/glm ×4}
= 24 reps. PRIMARY: look rate (bare-suite run before done) per
family, vs the -pt control column; SECONDARY: flag rate in final
reply, guard = task-done + gauntlet pass. Prediction from the
attended-moment doctrine: claude moves here where bootstrap placement
was inert; kimi's already-nonzero look rate rises or holds; glm is
the open question. The -pt control column doubles as the friction
quantification for the original sp-adjacent columns.

Both batteries queue behind the K1g census on the lanes.

## 2026-08-07 — K1g census, SONNET COLUMN: forwarding CONFIRMED with
## direct dispatch evidence (3/3)

base2 × k1g-ground-truth reps 11-13, claude lane, served
claude-sonnet-5 (3/3). Guard clean: gauntlet pass 3/3, vendor
untouched, all four modules real-API, overwrite adaptation
discard-then-store (rep13 belt-and-suspenders both), zero phantom
AttributeErrors in 40 session files.

The claude lane upgrades the evidence class: dispatch payloads are
readable (unlike codex), so forwarding is mechanically instrumented —
**k1g-dispatch-corrections 9/11, 9/12, 9/11** across the three reps.
Spot-checked blobs are unambiguous; one dispatch verbatim: "The
brief's Step 3 sample code calls `store.put(key, data,
overwrite=True)`. That method does not exist. … It actually exposes:
`store(key, data)` — … raises `KeyExistsError` …". Another cites the
ruling channel explicitly: "The controller ruled (recorded in the
project ledger) that the brief's literal sample code is pseudocode
for intent … the correct way to get replace-on-reingest semantics is
`store.discard(key)` … then `store.store`". Rule-and-continue →
ledger → correction-in-every-dispatch, on a second model family, with
the codex hand-read now corroborated by a readable channel.

Census remaining: kimi (rep 21 running), glm (queued), luna (quota
wait). Verdict entry stays open until those land.

## 2026-08-07 — CORRECTIONS from the adversarial audit (5 confirmed
## defects in published verdicts; auditor: independent subagent,
## verified against raw rep data)

**C1 — P3 verdict RETRACTED and relabeled INCONCLUSIVE-BY-CEILING
(one level up).** The audit searched every rollout and trajectory in
all 8 P3 reps for the trap's runtime signature: **zero** composed
runs ever raised SampleStreamError unexpectedly. Every occurrence is
TDD RED-phase testing of the validator itself, spec/plan
transcription (the p3-trap-sighting-step values 6-10 are the agent
WRITING the spec, not running tests), or one deliberate
break-and-restore check. My mechanism narrative — "every rep hit the
conflict at its first end-to-end run and fixed it in 1-2 commits" —
described an event that never occurred. Worse: p3-trap-in-plan was
yes in 3/4 controls, and the pre-registration's own
INCONCLUSIVE-BY-CEILING clause (trap harmonized at plan time + no
composed failure ever) was therefore MET and should have been the
verdict's first line; I never evaluated it. The pre-registered
rework-tokens endpoint was also silently dropped. What survives:
walking-skeleton stays unshipped (nothing was measurable either way)
and the fixture-must-compound requirement. What does not survive:
"there is no expensive rework to avoid," the 1-2-commit-fix story,
and the NULL label.

**C2 — the 2026-08-06 saw-and-stayed-silent claims are REFUTED; the
08-06 hand-read counts are superseded and were never corrected.** The
two reps that entry named as "watched the shipping test fail and
shipped without a word" (base2-rep45, vfloor-rep44, kimi-or lane) did
neither: raw trajectories show both ran/verified inventory only and
never executed or read the shipping test — "shipping" appears once in
each, inside an ls listing. The 08-06 counts (base2 3 saw-silent,
vfloor 2) are irreconcilable with the 08-07 recount (0 saw-silent
anywhere) and this line is the dated correction the log owed:
**the 08-06 hand-reads were wrong; the 08-07 recount stands.**
Material consequence, stated plainly: the vfinish arm (18 reps,
three model families) was built to chase a probe-scale failure class
that the raw data says never existed at probe scale. Its SDD-scale
motivation (the cp-x1 observation) still stands; its probe-scale
motivation does not.

**C3 — "12/12 pooled saw→mentioned" is arithmetically wrong.** The
entry's own table sums to 11 (base2 kimi-oauth 1, vfloor sonnet 1,
vfloor kimi-oauth 4, vfloor kimi-or 3, vfinish kimi-oauth 2).
Corrected claim, phrased as the bound it is: **11/11 reps with an
observed saw-the-failure event mentioned it**; no saw-silent
observed at probe scale. deferred-experiments inherits this fix.

**C4 — K1g "11/12 later-task seats inherited the correction" is an
absence-based bound stated as a positive.** The instrument measures
only firsthand runtime re-discovery; it cannot distinguish
"inherited from the dispatch" from "silently re-derived by reading
the lib." Corrected phrasing everywhere (incl. deferred list):
**11/12 later-task module implementations show no firsthand runtime
re-discovery; dispatch-carry is demonstrated by hand-read sampling
(codex) and by the readable dispatch channel at 9/11-9/12 per rep
(sonnet).** The census PASS shape gains a counting rule:
reading-based re-derivation, where detectable, counts as
re-discovery for the census question.

**C5 — undisclosed denominator drift in the vfloor tables.**
kimi-oauth base2 was reported /6 on 08-06 but only 5 reps carry
trajectories (rep24 absent); haiku vfloor walked 6→5→3 across
entries (reps 14-16 carry no trajectory) with no dated note. The
08-07 table's ns (5 and 3) are the correct ones; exclusions are now
itemized here: kimi-oauth base2 excludes rep24 (no trajectory);
haiku vfloor excludes reps 14-16 (no trajectory / indeterminate).

**Audit also verified clean** (actively, against raw data): T9's
constraints-landed hand-reads (pinned answer's shape genuinely
landed, exclusions included), the #2086 kimi/glm cells (values
printed, trees built, worktree-aware), tier-2 vfloor 3/8 (all three
transcripts name the exact failing test), K1' null-by-headroom, K1g's
quoted rollout evidence, and the emit-only-never-gates discipline
across every audited checks.sh.

**Suspects queued:** adjudication guard sensitivity (zero-variance
2.0 escapes — pull per-rep escape identities before citing that guard
as evidence of safety again); the "kimi family attends / claude sails
past" family-attention claim is PROVISIONAL until the -pt battery
separates won't-look from tool-missing.

## 2026-08-07 — K1g census, KIMI + GLM COLUMNS (4/4 clean; census
## now four families, luna pending)

base2 × k1g-ground-truth: kimi-oauth reps 21-22 (served
kimi-for-coding — the wire-fallback instrument fix reading correctly
in production), glm reps 31-32 (z-ai/glm-5.2, pi lane). All 4:
gauntlet pass, vendor untouched, all four modules real-API, overwrite
adaptation discard-then-store (rep22 both), plan file never edited.

Signature counts first (rule 9): phantom-AttributeError files — kimi
rep21 **1** (attributed: the Task 1/ingest seat's own session file, 2
hits — discovery-by-running at the legitimate moment, NOT a
later-task leak; citation: home/.kimi-code/sessions/wd*, touches
__init__+ingest only), rep22 0, glm 0 + 0. Dispatch-correction
tokens (readable on both these harnesses): kimi 9/13 and 10/17
blobs; glm 36/36 and 13/16.

Census standing, phrased as rule-15 bounds: on four model families
(gpt-5.6-sol, claude-sonnet-5, kimi-for-coding, glm-5.2), zero
later-task seats show firsthand runtime re-discovery, and the
correction is demonstrably present in later dispatches on every
family where the channel is readable. The told-vs-read split for
later seats is in progress (re-score agent). Luna column pending
quota.

## 2026-08-07 — RECOUNT of the 08-06 vfloor battery (all 90 reps,
## step-level citations; full table in the session scratchpad file
## recount-0806-vfloor.md, extractor recount.py alongside it)

Authoritative counts (86 data-bearing reps; NO-DATA: base2-rep24,
vfloor-reps 14-16): full-suite-with-output 11, attempted-but-tool-
missing 3, targeted-only 40 (18 by inline python3 -c only), no-tests
32. Saw-the-failure 11; mentioned 11/11; **saw-silent 0**; fixed 5
(vfloor kimi-oauth 25/26, vfloor kimi-or 43/45/57 — each verified
2.0→2.5 with Edit citations). The 08-07 slate table is confirmed
cell-for-cell, including the corrected 11/11.

**Two further 08-06 look-cell CORRECTIONS beyond C2/C5:** base2
kimi-oauth look-yes was reported 0 — actually **1** (rep26 ran the
bare venv suite; wire.jsonl steps 80-81); base2 kimi-or look-yes was
reported 1 — actually **0** (no base2 kimi-or rep ever produced
full-suite output). Net effect on the kimi family contrast: vfloor's
lift on kimi-oauth is now 4/6 vs 1/5 control on look — unchanged
conclusion, corrected cells.

**New observation (no prior count changes): a DEGENERATE-VERIFICATION
pattern.** Two reps (vfinish-rep25, base2-rep43) ran
`python3 test_shipping.py` — which exits 0 with no output on a
pytest-style file (no __main__ block) — and their finals then claim
both test files pass. That is a false-green verification, invisible
to exit codes. Worth a probe of its own if seen again; noted here as
first sighting (2 of 86 reps). Kimi-oauth transcript caveat for
future scorers: the pretty trajectory.json drops content after turn
1 — read agents/main/wire.jsonl.

## 2026-08-07 — RE-SCORE RESULTS: adjudication guard + K1g
## told-vs-read (full tables in scratchpad rescore-guard-k1g.md;
## scored with the battery's own scan_defects())

**C6 — the adjudication "guard 2.0 escapes/rep uniform" claim is
CORRECTED, and SAFE weakens further:**
- All 9 treatment reps (r1t/rebut/r1t-rebut) escape the identical
  pair {ANCHOR-IMPORTANT, DEBATABLE-2}. Zero treatment-side variance.
- base2 was NOT uniform: per-rep escapes [2, 1, 4, 1]. My "2.0 in
  every arm" was an arm-mean coincidence — and it conceals a
  stale-tree artifact: base2-rep3's main tree is the untouched seed
  (its fixes sit unmerged in .worktrees/credit-adjustments, which
  itself scores the same 2). Scoring worktrees, base2's mean is 1.5.
- Per-defect: DEBATABLE-2 escaped 13/13 — the guard is AT CEILING
  there, zero discrimination. ANCHOR-CRITICAL and DEBATABLE-1 were
  caught in every treatment rep (headroom existed).
- **Wrinkle that must not be buried: ANCHOR-IMPORTANT was caught 2/4
  in base2 and 0/9 in treatments.** At these ns that is suggestive,
  not significant — but it means even "no arm made things worse"
  is not cleanly supported. Corrected verdict language: the battery
  demonstrates no guard-visible regression on defects with headroom
  EXCEPT a possible anchor-important catch-rate drop in the
  treatment arms that n=4-vs-9 cannot resolve. STANDING NOTE: any
  future rebut/r1t run on cp-x1-edit-existing carries
  anchor-important catch rate as a PRIMARY endpoint; the queued ARF
  battery tests these texts on a different fixture and does not
  settle this specific wrinkle.

**C7 — K1g told-vs-read RESOLVED (33 later-task seats):**
told-first 26/33; told-only (no observed lib read) 1/33;
read-first-with-told-status-unknown 6/33 (all codex base2, where the
dispatch payload is encrypted even in the subagent's own rollout and
the readable briefs are verbatim phantom-API text — their pre-read
"per the controller ruling" statements can only have come from the
encrypted dispatch, but 6 seats stated the API only after reading).
Sonnet: told 9/9 with dispatches that name the real API AND order
the lib read — the reads are instructed verification, not
re-derivation. k1b: told 12/12 via the handoff artifact, read before
any vendor read in 11/12. read-lib overall 32/33; no seat learned
the API via runtime error. The census claim upgrades from bound to:
**forwarding demonstrated told-first in 26/33 later-task seats,
unknown-not-refuted in 6, on four model families.**

## 2026-08-07 — CORRECTION C8: the first -pt battery ran WITHOUT the
## preinstall (my own rule-16 violation), all reps quarantined,
## relaunched on a fixed setup

Signature counts first: in the 8 sonnet -pt reps, watched-failure
events (a tool result actually showing the shipping test FAIL) = **1**
(vfloor-tdd-rep2, which then flagged it in its final reply — the arm
text working end-to-end once). A candidate second case
(vfloor-tdd-rep4 "saw and stayed silent") was a WRONG-CHANNEL
artifact caught before publication: its "saw" was a file READ of the
test source, not failure output — exactly rule 10's near-miss class.

The invalidating defect: session-start probes show `pytest not
found` — the -pt setup's pip install failed silently behind `|| true`
and I never added the pre() assertion rule 16 requires (a rule I
wrote hours before building this scenario). The friction confound the
variant exists to remove was fully intact; the 8 sonnet reps and the
5 partial kimi reps are quarantined
(.quarantine-pt-setupfail-20260807, both lanes) and never enter
tables.

Fix (source + both checkouts): setup now verifies `import pytest`,
falls back to a dedicated venv with a PATH symlink, hard-fails setup
if `pytest` is still not on PATH, and prints pytest --version;
pre() gains `requires-tool pytest`, so a broken install now fails the
rep loudly at pre-check instead of silently confounding. Battery
relaunched on both lanes, same pre-registration, same endpoints,
fresh reps.

## 2026-08-08 — VERDICT (partial battery): vfloor-tdd SONNET cells on
## the fixed -pt probe — the attended-moment placement BINDS 4/4

Signature counts first (rule 9), all 8 reps, strict criteria
(suite run = a pytest invocation not scoped to test_inventory that
produced output; watched-failure = a FAILURES-block/assert-signature
in a tool RESULT; file reads and which-probes excluded):

| arm | rep | suite runs | watched-failure sigs | named in final |
|---|---|---|---|---|
| base2 | 1 | 0 | 0 | no |
| base2 | 2 | 0 (one `which pytest` probe, not a run) | 0 | no |
| base2 | 3 | 0 | 0 | no |
| base2 | 4 | 0 | 0 | no |
| vfloor-tdd | 1 | 2 | 1 | yes |
| vfloor-tdd | 2 | 2 | 1 | yes |
| vfloor-tdd | 3 | 2 | 2 | yes |
| vfloor-tdd | 4 | 2 | 1 | yes |

All 8 served claude-sonnet-5; task-done 8/8 (guard clean); shipping
left unfixed in all (in-scope discipline held — the text asks for
report, not fix). With tool friction removed, the control NEVER looks
(0/4) and the TDD Verify-GREEN placement looks, sees, and reports
4/4. Contrast with the same text at bootstrap placement (inert on
claude, 08-06/08-07 batteries) and with the quarantined confounded
battery (treatment 1/4): placement at the attended moment is the
active ingredient, exactly the arm-design doctrine's prediction.

Battery incomplete: kimi + glm cells running on lane B; verdict
finalizes when they land. If they hold, cp/vfloor-tdd @ 46ff987 is a
ship candidate through the normal gate (its arm text IS the shipped
text; needs Jesse's placement sign-off and the PR path).

## 2026-08-08 — VERDICT (battery complete): vfloor-tdd across three
## families — placement effect on ALL THREE, graded by family

Strict signature counts (watched-failure = FAILURES-block/assert
signature received in tool output; kimi read from wire.jsonl, glm
from trajectory, sonnet from claude session logs):

| family | control look-see-mention | vfloor-tdd look-see-mention |
|---|---|---|
| sonnet | 0/4 | 4/4 |
| kimi-for-coding | 1/4 (rep22) | 3/4 (reps 21,23,24) |
| glm-5.2 | 0/4 | 1/4 (rep33) |
| pooled | 1/12 | 8/12 |

Every rep that saw the failure mentioned it (9/9 — the
looking-is-the-bottleneck finding holds again). Guard: treatment
task-done 8/8; control kimi reps 21/24 task-done no (control-side
completion noise, not arm-attributable). Instrument note:
vfloor-tdd-rep21's verdict emits came up empty while its wire log
carries the full chain — scored from the wire per the kimi transcript
caveat; emit-side gap filed.

**Conclusion:** moving the verification-floor text from bootstrap
(inert on claude/glm) to the TDD Verify-GREEN moment produces
look-see-report behavior on every family tested: complete on sonnet,
strong on kimi (over an occasional-looker baseline), first-ever
recorded glm look. cp/vfloor-tdd @ 46ff987 is a SHIP CANDIDATE: the
arm text is the shipped text verbatim, battery pre-registered and
complete, cross-family. Needs Jesse's sign-off for the PR.
