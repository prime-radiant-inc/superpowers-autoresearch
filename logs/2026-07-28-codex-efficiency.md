# Codex efficiency eval campaign — hypothesis log

**Started:** 2026-07-28
**Campaign home:** `campaigns/codex-efficiency/DESIGN.md`
**Spec:** `docs/2026-07-28-codex-efficiency-eval-campaign-design.md`
**Budget:** $1000 total, tracked below; no per-battery approval gate.

This is an append-only log. Every entry below is a pre-registered prediction
written before any run (per the spec's discrimination rule: an eval counts
only once its baseline on current `dev` exhibits the documented pathology —
inconclusive-by-zero is a stop, not a pass). Verdicts get appended under each
entry as batteries run; predictions themselves are never edited after the
fact.

## Budget ledger

| Date | Battery | $ cost | Sub used_percent before | Sub used_percent after |
|---|---|---|---|---|
| 2026-07-28 | E1 baseline (dev, cx-sdd-small, 4 reps) | $20.59 ($19.43 coding + $1.16 gauntlet) | 28.0% | 31.0% |
| 2026-07-29 | E1 treatment (spinout, cx-sdd-small, 4 reps, axis A) | $21.28 ($19.90 coding + $1.38 gauntlet) | 45.0% | 1.0% (window rollover mid-battery) |
| 2026-07-29 | E1 re-test @ CLI 0.146.0, baseline (dev, cx-sdd-small, rep5-6) | $7.27 ($6.64 coding + $0.63 gauntlet) | 3.0% | 3.0% |
| 2026-07-29 | E1 re-test @ CLI 0.146.0, treatment (spinout, cx-sdd-small, rep5-8, axis A) | $17.74 ($16.42 coding + $1.31 gauntlet) | 4.0% | 7.0% |

## Pre-registered predictions

### E1 — Codex fork hygiene (Finding 1, P0)

- **Prediction (baseline, current `dev`):** ≥40% of SDD spawns use
  `fork_turns:"all"`; ≥60% omit `model`.
- **Prediction (treatment, `codex-spinout-fixes`):** 100% `"none"`, 100%
  explicit model, task completion preserved.
- **Scorer:** per-spawn tuple — `fork_turns` value, explicit-model presence,
  instruction-line offset, child rollout bytes, child skill re-reads.
- **Success criterion:** baseline lands if the ≥40%/≥60% prediction holds
  (discrimination rule). Treatment lands if it hits the spec's bar: 100%
  isolated spawns, 100% explicit models, no loss of task completion.

### E2 — Reviewer recursion (Finding 2, P0)

- **Prediction (baseline):** a dispatched branch reviewer produces ≥1
  descendant in ≥half of reps.
- **Scorer:** subtree census per dispatched reviewer — descendants, max
  depth, thread-limit failures, sessions missing `task_complete`, wait-call
  volume.
- **Success criterion:** baseline lands if the ≥half-of-reps prediction
  holds. Future treatment target (spec): zero reviewer descendants in the
  default case, findings quality preserved.

### E3 — Evidence receipts / duplicate gates (Finding 3, P1)

- **Prediction (baseline):** the full test suite runs ≥2× at an identical
  tree state across implementer→review→finishing.
- **Scorer:** identical-command-at-identical-tree-state detection across a
  workflow's sessions (implementer → task review → finishing).
- **Success criterion:** baseline lands if the ≥2× duplicate-run prediction
  holds. No treatment arm yet (spec).

### E4 — Proportional workflow ceremony (Finding 4, P1)

- **Prediction (baseline):** ceremony census (docs written, approval gates,
  user turns before first code patch) is statistically indistinguishable
  across spike/bounded/architectural task classes.
- **Scorer:** ceremony census before first code — design docs written,
  approval gates, questions asked, tool calls.
- **Success criterion:** baseline lands if ceremony is statistically
  indistinguishable across the three task classes. No treatment yet.

### E5 — Review scope and accretion (Finding 6, P1)

- **Prediction (baseline):** the local-scope defect is caught; at least one
  of {cross-task race, clean-checkout break, repair-induced regression} is
  missed by the mis-matched scope or duplicated across same-scope
  reviewers.
- **Scorer:** seeded-defect recall by intended scope + scope-accretion
  (post-completion commits/lines attributable to review findings;
  unadjudicated new scope).
- **Success criterion:** baseline lands if the local defect is caught AND
  at least one of the other three planted defects is missed or duplicated
  as predicted. Most expensive experiment; runs last.

### E6 — Context diet / compaction recovery (Finding 8, P2 but cheap to score)

- **Prediction (baseline):** after a forced compaction the controller
  re-reads ≥1 SKILL.md it had already read, and ≥1 post-compaction spawn
  drops isolation or model explicitness relative to pre-compaction spawns.
- **Scorer:** post-compaction skill re-read count, bootstrap/routing
  retention (do isolated-fork rules survive compaction?), controller input
  growth.
- **Success criterion:** baseline lands if both parts of the prediction
  hold (≥1 re-read AND ≥1 degraded post-compaction spawn). Rides on E1's
  `codex-spinout-fixes` infrastructure; forced compaction is the one rig
  unknown (spec risk).

## Findings

### 2026-07-28 — Parser validated against the audit corpus (Task 4, MINE)

`campaigns/codex-efficiency/validate_corpus.py` ran `extract_spawns`/
`parse_session` against the full audit corpus's known ground truth
(`session-manifest.json`, `spawns-window.json`, `metrics-all.jsonl`, 2,240
sessions / 1,098 spawn records). Full report:
`campaigns/codex-efficiency/out/corpus-validation.md`.

- **Phase A (spawn parity):** 161/161 sessions exact match, 0 mismatches;
  `fork_turns`/`model` aggregate distributions identical to the audit's
  (574 `all` / 359 `none` / 18 `(omitted)` / partials; 925/1098 omitted
  models). Exact parity, unconditionally trusted.
- **Phase B (per-session metrics, 49-session stratified sample):**
  93.9–98.0% per-field exact match. All mismatches trace to 3 sessions whose
  rollout activity extends outside the audit's
  `[2026-07-14T07:00:00.000Z, 2026-07-28T16:50:29.164Z)` window (created
  before window start, or still live/growing past window end) — confirmed
  by direct rollout inspection. The audit scanner discards out-of-window
  lines from every counter; `parse_session()` has no such filter (out of
  scope for Tasks 2–3). Restricted to sessions fully inside the window:
  100% (46/46) on all 8 fields.
- **Phase C (manual inspection):** sampled skill-read and test-command
  matches eyeballed by hand — all genuine, no false positives observed in
  the sample (the known `apply_patch`-mentions-`SKILL.md` false-positive
  path from Task 3 wasn't hit here since the sample drew from real
  exec-shaped reads).

**Restriction for downstream scorers:** do not treat `parse_session()`'s
absolute counts as corpus-comparable for a session whose activity spans
outside the audit window; the parser is a strict superset in that case, not
wrong. See task-4-report.md for the full adjudication and a suggested (not
implemented) future parser enhancement.

**Verdict: parser trusted for corpus-relative scoring, subject to the
window-boundary restriction above.**

### 2026-07-28 — E1 baseline discrimination gate: BLOCKED (Task 6, FULL baseline)

Ran the FULL baseline battery (4 reps, `dev` arm, `cx-sdd-small`) via
`run-quorum.sh dev cx-sdd-small ...` (rep1 reused from the Task 5 smoke;
reps 2-4 run fresh) and scored all 34 spawns with
`campaigns/codex-efficiency/score_e1.py`. Full detail:
`campaigns/codex-efficiency/out/e1-report.md`.

**Result: 34/34 spawns (100%) `fork_turns:"none"` (isolated), 0%
`"all"`/partial, 100% model-omitted** — identical across all 4
independent reps.

**Gate:** the registered prediction is compound — ≥40% `fork_turns`
`"all"`/partial (observed 0%, **fails**) AND ≥60% model-omitted (observed
100%, holds). Per the task-6 controller instruction, since the baseline
does not exhibit the full pathology, **the treatment battery
(`codex-spinout-fixes` arm) was not run.** Status returned: BLOCKED, for
controller/Jesse adjudication.

This sits in tension with the audit's own Finding 1 narrative ("The
small SDD control case shows the behavioral consequence... Full-history
'implementers'... recursively became SDD controllers") — our distilled
scenario didn't reproduce that shape on current `dev`, even though `dev`'s
`subagent-driven-development/SKILL.md` and `codex-tools.md` still don't
mention `fork_turns` anywhere (confirmed by grep). The model-omission
half of Finding 1 did reproduce, strongly. See the report's "Why this is
surprising" section for candidate explanations (none confirmed).

**Cost:** $20.59 ($19.43 coding + $1.16 gauntlet), sub used_percent
28.0% → 31.0%. Ledger row above.

**Next step:** re-plan with the controller/Jesse — options include
re-scoping the scenario to exercise conditions more likely to trigger
full-history forking, accepting the model-omission-only result as E1's
baseline finding and adjusting the treatment's success bar accordingly,
or treating E1 as inconclusive-by-construction for this scenario shape.

### 2026-07-28 — POST-REGISTRATION AMENDMENT: E1 split into axis A/axis B (Jesse-approved)

**This is a post-registration amendment, not an edit to the original
prediction above** (which stands, unedited, per the log's own
append-only rule). Recorded after controller adjudication of the BLOCKED
gate result, with Jesse's explicit approval.

**Independent verification of the gate result.** Before adjudicating,
the controller independently re-counted the 34 baseline spawns directly
against raw rollout JSON (grep for `"name":"spawn_agent"` /
`"fork_turns"` / `"model"` across all 4 rep controller rollouts,
bypassing `score_e1.py` entirely) and confirmed: **34/34 `fork_turns`
`"none"`, 0/34 explicit `model`** — matching the scorer's output exactly.
The gate result is not a scorer artifact.

**Decision: E1 is split into two independently-gated axes**, effective
immediately, superseding the single compound prediction registered
above:

- **Axis A — model-explicitness.** Baseline: 0/34 (0%) explicit models,
  clearing the ≥60%-omitted threshold decisively. **This axis
  discriminates.** Proceeding to the `codex-spinout-fixes` treatment
  battery (4 reps, spinout arm) now, scoring axis A as primary.
  **Success criterion (treatment):** 100% explicit `model` on SDD
  spawns, task-completion parity with baseline (children still reach
  `task_complete`). Also reporting the treatment arm's `fork_turns`
  distribution as a secondary readout — expected to hold at 100%
  `"none"` (matching baseline); any regression toward `"all"`/partial
  is itself a finding worth flagging, not just noise.
- **Axis B — fork-isolation.** Baseline: 0/34 (0%) non-isolated spawns
  against a ≥40% threshold — **inconclusive-by-zero** on this
  fresh-session, short (3-4 task) SDD scenario shape. Per the audit's
  Finding 1 narrative, full-history recursive forking was observed on
  *long-running* sessions with substantial accumulated context, not
  short fresh-session dispatches — which is exactly the condition E6's
  scenario (long controller session, forced compaction, post-compaction
  dispatch) is built to elicit. **Axis B is formally re-scoped OUT of E1
  and INTO E6.** Do not re-attempt fork-isolation discrimination on the
  cx-sdd-small fresh-session scenario; E6 owns it going forward.

**Rationale:** the two halves of the original compound prediction
diverged sharply (0% vs. 100%) rather than moving together, so treating
them as one gated prediction was actively hiding a real, discriminating
signal (axis A) behind a non-discriminating one (axis B) that the
scenario was never well-shaped to elicit in the first place. Splitting
lets axis A's genuine finding proceed to treatment on schedule while
axis B moves to the scenario (E6) that the corpus evidence actually
supports for eliciting it, rather than spending the treatment budget on
an axis this scenario shape can't discriminate.

**Approved by Jesse.** Treatment battery, updated `out/e1-report.md`,
and budget-ledger row for the spinout battery follow below /
in-report.

### 2026-07-29 — E1 axis A treatment result: literal criterion FAILS, root-caused to Codex CLI version (Task 6 addendum)

Ran the axis-A treatment battery (4 reps, `codex-spinout-fixes` arm,
`cx-sdd-small`) via `bash run-quorum.sh spinout cx-sdd-small 4` and
scored all 34 spawns with `score_e1.py`. Full detail:
`campaigns/codex-efficiency/out/e1-report.md`.

**Result: 34/34 treatment spawns are bit-identical to baseline** — 100%
`fork_turns:"none"`, 0% explicit `model`, 100% model-omitted, 100% child
`task_complete`. Axis A's success criterion (100% explicit model) is
**not met** — no improvement over baseline.

**Root cause identified, not left as a bare negative result:** every
one of the 8 runs across both arms (`session_meta.cli_version` read
directly off the controller rollout) reports Codex CLI **`0.144.4`**.
The spinout branch's own `codex-tools.md` documents the
model/`reasoning_effort` override as gated on **Codex 0.145+**,
explicitly saying pre-0.145 sessions have no such parameters on
`spawn_agent` and correctly inherit model with no override available.
The eval container is running below that version gate on both arms (the
arm only swaps which superpowers checkout is mounted, not the container
image) — so this battery structurally cannot discriminate whether the
spinout branch's model-explicitness fix works. **Axis A verdict:
inconclusive due to eval-container infrastructure, not failed.**

Task-completion parity holds cleanly (34/34 both arms). Fork_turns
regression check: no regression, treatment held at 100% `"none"` as
expected.

**Cost:** $21.28 ($19.90 coding + $1.38 gauntlet). Sub used_percent
45.0% → 1.0% (a rate-limit window rollover occurred mid-battery, not a
budget anomaly — noted, not investigated further). Ledger row above.
E1 running total across both batteries: **$41.87**.

**Recommendation:** before drawing any conclusion about the spinout
branch's axis-A fix, re-run this battery (or a cheaper MICRO check)
against a container image with Codex CLI ≥0.145.

### 2026-07-29 — E1 RE-TEST at Codex CLI 0.146.0 (Task 6b, Amendment 1): axis A no longer discriminates

Bumped the eval container's pinned Codex CLI (`evals/container/Dockerfile`)
from `0.144.4` to `0.146.0` (newest published exact-version npm release;
local commit only in the `evals` checkout, not pushed —
`6266ced`). Rebuilt, verified `codex --version` -> `codex-cli 0.146.0`
and confirmed `session_meta.cli_version` == `0.146.0` on all 6 new reps
before spending. Re-ran E1 as a small confirmatory battery: **2 new
baseline reps** (dev, rep5-6, extending Task 6's rep1-4) and **4 new
treatment reps** (spinout, rep5-8, extending Task 6's rep1-4), scored
with `score_e1.py`. Full detail:
`campaigns/codex-efficiency/out/e1-retest-cli0146.md`.

**(a) Baseline fork_turns confound: holds cleanly.** 14/14 new baseline
spawns are `fork_turns:"none"` at 0.146.0, identical to Task 6's 34/34
at 0.144.4. The CLI-version confound registered in the Amendment 1 scope
note does not disturb the fork-isolation result.

**(b) Axis A: the headline result from the Task 6 addendum does NOT
survive at the field CLI version, and the direction of the surprise
matters.** Treatment jumps from 0% explicit model (Task 6, 0.144.4) to
93.9% (31/33, this re-test) — but **baseline also jumps, from 0% to
100% (14/14)**. Root cause: `dev`'s own
`subagent-driven-development/SKILL.md` already instructs "Always
specify the model explicitly when dispatching a subagent" (pre-existing,
not spinout-specific) — it had no `model` parameter to act on before
0.145, so the CLI gate was masking a `dev`-side capability all along,
not just a spinout-side one. Every root-controller spawn on both arms
(45/45 combined) is explicit-model at 0.146.0. **Axis A no longer
discriminates baseline from treatment at the field CLI version** — this
supersedes the Task 6 addendum's "inconclusive by infrastructure, would
likely show the fix working once unblocked" framing. The evidence at the
field CLI version does not show the spinout branch's specific
`codex-tools.md` content doing incremental work beyond what the CLI
unlock + `dev`'s pre-existing generic instruction already produce.

Treatment's 2 shortfalls from literal 100% are **both depth-2 spawns
issued by an implementer child recursively calling `spawn_agent` itself**
(`agent_path` traced to `/root/task2_implementer/cli_review` and
`/root/task1_implementer/task1_reviewer` respectively via
`parent_rollout`), not root-controller dispatches. One of these two is
also the *only* `fork_turns:"all"` spawn in either new battery — a
full-history fork issued by a child. Both occur only on the treatment
arm in this sample (n=2, small); baseline (2 reps) shows zero depth-2
forking. Reported as an observation for E6 (which owns the fork-isolation
axis), not adjudicated here — sample too small to claim the spinout
branch causes more child-initiated recursion.

**(c) Completion parity: full, both arms** — 14/14 dev + 33/33 spinout
children resolved with `task_complete` present; 6/6 new reps
gauntlet-passed.

**Cost:** $25.01 ($7.27 baseline + $17.74 treatment), against the plan's
≈$32 estimate. E1 running total across all three batteries (Task 6
baseline + Task 6 axis-A treatment + this re-test): **$66.88**.

**Process note:** `score_e1.py`'s output-JSON filename is derived from
the battery-dir label only (`cx-sdd-small-dev` / `cx-sdd-small-spinout`),
which collides across `REP_START`-extended batteries scoring different
rep ranges under the same label — first invocation here silently
overwrote Task 6's committed `out/e1-cx-sdd-small-{dev,spinout}.json`.
Caught via `git status`/`git diff --stat` immediately after, recovered
with `git checkout --` (Task 6's original 34/34-spawn aggregates
restored unmodified, verified), new-reps-only output re-saved under
`out/e1-cx-sdd-small-{dev,spinout}-cli0146.json`. No data lost, but the
script has a real collision risk for any future REP_START-extended
re-score — flagged for a fix, not fixed in this task.

### 2026-07-29 — EXTERNAL EVIDENCE: Drew-corpus cross-validation (Amendment 1)

**Provenance:** Drew Ritter, 2026-07-27 package (`HANDOFF.md` dated
2026-07-27; fractals runs 2026-07-25, stress-2703 stress specimen
2026-07-24). All Codex runs: superpowers `codex-spinout-fixes @
bd68a949`, Codex Desktop CLI `0.146` (`session_meta.cli_version` =
`0.146.0-alpha.3.1` on every rollout, verified directly). Corpus path
(external, read-only, never committed):
`/Users/jesse/git/superpowers/_tmp/drew-sdd-head-to-head-2026-07-27/sdd-testing-fresh/`.
Full reconciliation, methodology, and per-field match/mismatch table:
`campaigns/codex-efficiency/out/drew-cross-validation.md`. Adapter used:
`campaigns/codex-efficiency/drew_adapter.py` (thin run-dir-discovery
adapter over unmodified `rollout_parser.py`; Drew's flat
`transcripts/*/rollouts/` layout doesn't match `score_e1.py`'s quorum
battery-dir convention).

**Schema finding (load-bearing):** Drew's corpus contains two different
`spawn_agent` tool schemas under the *same* CLI version string —
`collaboration` namespace (`fork_turns` string + `task_name`, matching
our own parser/eval-container schema exactly: sol-5_6, stress-2703) and
`multi_agent_v1` namespace (`fork_context` bool, no `task_name`:
codex-5_5 only). `rollout_parser.extract_spawns()`'s `fork_turns`/
`task_name` fields correctly read `"(omitted)"` for every codex-5_5
spawn (the key really is absent) — this is a schema gap, not a fork
hygiene finding; an adapter-level raw peek confirms codex-5_5 is 18/18
`fork_context: false` (isolated), same as the other two runs.
`child_links()` also returns empty for every `multi_agent_v1` rollout
(no `sub_agent_activity` event exists in that schema) — flagged as a
concern for any future corpus ingestion (§5 of the cross-validation
report), not patched in this task.

**Headline numbers, reconciled (ours via `rollout_parser`+`drew_adapter`,
independently, then cross-checked against his script-emitted
`analysis/metrics/*.json`):**

- **103/103 "letter-perfect" dispatch tuples** (18 codex-5_5 + 19
  sol-5_6 + 66 stress "clean" tuples): verified independently — all 103
  are isolated (`fork_context:false`/`fork_turns:"none"`) AND
  100% explicit-model. Matches his `report-addendum.md` framing exactly.
- **18 compactions in the stress run:** our `parse_session(root).
  compactions` = 18, exact match to his `compaction.json`
  (`compacted_records: 18` / `context_compacted_events: 18`). Plus 7
  more inside 4 long-running child sessions (his `compaction.json`
  `children` block agrees exactly) — total 25 across the run-tree, 18 at
  root.
- **805 wait polls in the stress run:** our root `wait_calls` = 809, not
  805 — fully reconciled, not a real mismatch: his own `sessions.json`
  keeps `wait_agent` (805) and a separate `wait` tool (4) as distinct
  counters; our classifier's `WAIT_NAMES` merges both into one metric.
  805 + 4 = 809, exact.
- **67 stress children:** confirmed exactly, root-caused rather than
  taken on faith. Root issued 83 raw `spawn_agent` calls (matches his
  `sessions.json` `tool_calls.spawn_agent: 83` exactly); 17 of those 83
  are a replay burst (all 17 timestamps cluster in the same ~150ms
  window as the run's first `compacted` record, which his own
  extraction tags `"phase": "replayed_import"` — historical records
  re-emitted at a resume boundary, not fresh spawns) and correctly have
  no separate rollout file; the remaining 66 match his `dispatch.json`
  exactly. One additional child — invisible to his root-scoped
  `dispatch.json` but present in his broader `sessions.json`
  (`depth: 2`, `role: "other"`) — was spawned recursively by a depth-1
  **implementer**, not by root. 66 + 1 = 67, matching the HANDOFF
  headline exactly. That same depth-2 recursive spawn is also the one
  spawn anywhere in Drew's 121-spawn corpus missing an explicit model —
  the identical failure shape our own E1 CLI-0.146 re-test found
  independently (two depth-2, implementer-issued spawns).
- **Reviewer no-recursion:** could not locate a "0/53" figure anywhere
  in Drew's shipped materials (searched exhaustively). Computed our own
  instead: 0 of 64 reviewer-role spawns (`task_reviewer`/`fix_reviewer`/
  `final_reviewer`, his own role labels, all three runs combined)
  produced any descendant. The corpus's only recursive spawn (above) was
  implementer-issued, not reviewer-issued. Reporting **0/64**, not 0/53
  — the qualitative claim holds, the denominator in the task brief does
  not trace to any file in the package.

**Which E-experiments this bears on:**

- **E1 axis A (model explicitness):** corroborating, not independently
  discriminating — Drew's corpus has no `dev` arm to compare against.
  All 103 clean dispatches across both fractals runs are 100%
  explicit-model at the field CLI version, consistent with our own
  CLI-0.146 re-test's finding that the CLI version (not spinout
  specifically) is what unlocks the parameter. A second, larger,
  independent data point for the same conclusion.
- **E2 (reviewer recursion):** 0/64 reviewer spawns recursed, across
  three independent sessions and two schemas — clean corroboration of
  E2's baseline pathology-absence shape at a much larger n than our
  battery has run.
- **E6 (compaction recovery):** the only real-world evidence anywhere
  (ours or his) of the compaction hook firing repeatedly under actual
  load — 18/18 root re-injections, 7 more inside children, no observed
  dispatch drift across any boundary. **Compliant-controller caveat**
  (his own analysis, paraphrased not quoted): this controller was
  independently well-behaved even in windows with no re-read prompt at
  all, so the run shows hook + chokepoint + compliant model = zero
  drift — it does not isolate the hook's own marginal contribution.
  Treat as strong supporting evidence for the mechanism, not proof the
  hook alone suffices against a less-compliant controller.
- **E7 (wait-polling) / E8 (close_agent hygiene) / E9 (workspace
  leaks) priors:** wait_calls (809 root, reconciling exactly to his
  805+4 split), compactions (18 root / 7 child), and close_agent (cited
  from his metrics only, not computed by us: codex-5_5 18/18 closed;
  sol-5_6 0/19; stress-2703 0/67 — "sol 0/86" in the plan = 19+67, both
  sol-controller runs, both zero) are registered here as the priors
  those three experiments need before building their scorers. Not
  scored — E7/E8/E9 are separate Amendment-1 tasks. The 78%
  wait-timeout claim specifically requires call/outcome pairing
  `rollout_parser.py` doesn't have yet (E7's job); not attempted here.

**Concerns raised against our own tooling (not fixed, this task):**
`extract_spawns()`'s `fork_turns`/`task_name` silently read
`"(omitted)"` for `multi_agent_v1`-schema rollouts (technically correct,
easy to misread as a fork-hygiene finding); `child_links()` returns an
empty map for the entire schema (no `sub_agent_activity` event exists in
it), so `score_e1.py`'s child-resolution would silently under-report on
any battery using this schema. Full detail:
`campaigns/codex-efficiency/out/drew-cross-validation.md` §5.

**No budget spent** (read-only analysis of existing external files, no
quorum/Codex runs). Sub `used_percent` and $ cost: not applicable, no
ledger row added.
