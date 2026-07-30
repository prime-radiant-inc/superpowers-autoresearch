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
| 2026-07-29 | E2 FULL baseline (dev, cx-branch-review, 4 reps) | $4.01 ($3.40 coding + $0.61 gauntlet) | 8.0% | 9.0% |
| 2026-07-29 | E1-v611 (v611, cx-sdd-small, 3 reps, lane B, JOBS=2) | $12.17 ($11.24 coding + $0.93 gauntlet) | 17.0% | 19.0% |

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

### 2026-07-29 — E7 PRE-REGISTRATION: wait-polling timeout rate (Amendment 1, Tasks E7-E9)

Registered before `score_e7.py` (or the parser's `wait_outcomes()`) exists,
per the campaign's build-order rule (Global Constraints: "a scorer issues
no verdict until validated against corpus ground truth AND its matches are
manually inspected" — this entry is the pre-registration half of that rule;
the manual-inspection half follows in Task E7's own Findings entry once the
scorer runs).

**Prediction:**

- **Drew's stress-2703 run:** ~78% of ~805 `wait_agent` polls time out.
  This is Drew's own claimed figure (cited in the Amendment-1 task list and
  registered as an *unverified* external prior in the Drew cross-validation
  entry above — "the 78% wait-timeout claim specifically requires
  call/outcome pairing `rollout_parser.py` doesn't have yet (E7's job); not
  attempted here"). E7 is the first attempt to check it independently.
- **Audit corpus, one Remux root:** ~74% (788/1058) `wait_agent` calls time
  out. This is the audit's own published Finding 7 figure ("one Remux root
  made 1,058 `wait_agent` calls, 788 of which timed out" —
  `docs/superpowers/research/2026-07-28-codex-efficiency-audit.md`, Finding
  7). Root identified by cross-referencing `session-manifest.json` (depth-0,
  `thread_source:"user"`) against `metrics-all.jsonl`'s per-session
  `tool_counts.wait_agent`: exactly one session anywhere in the corpus has
  `tool_counts.wait_agent == 1058`, session/root id
  `019f95af-9a8e-7cb3-bc01-edcfe8b343e8` (Remux key/file-provider family,
  per the audit's own family table) — this identification uses only
  pre-existing audit-artifact counters, not the not-yet-built pairing logic
  E7 is about to add, so it doesn't pre-empt the prediction it's meant to
  check.
- **Our own `cx-eff-*` battery runs** (14 quorum reps across `dev`/
  `spinout` arms, `cx-sdd-small` scenario, from Task 6/6b): materially
  *lower* timeout rates than either corpus above. Rationale: the scenario
  is a short (3-task) plan with brief child-agent lifetimes, giving
  spawned children little time to still be running when the controller
  polls — unlike the two corpora above, which are long-running,
  heavily-loaded real sessions.

**Scorer (to be built next, `score_e7.py` + `rollout_parser.wait_outcomes()`):**
pairs each `wait_agent` `function_call` to its later `function_call_output`
by `call_id`; classifies `timed_out` from the parsed JSON output's
`timed_out` boolean key (both the `collaboration`-namespace envelope
`{"message":...,"timed_out":bool}` and the `multi_agent_v1`-namespace
envelope `{"status":{...},"timed_out":bool}` carry this same key — to be
confirmed in Task E7's own build step); excludes argument-validation-error
outputs (e.g. `"timeout_ms must be at least 10000"`) and calls with no
matched output at all, as not-a-genuine-wait-outcome rather than counting
them as `timed_out=False`. Reports, per session and per run: paired-call
count, timeout rate, inter-poll interval p50/p95 (from consecutive
`wait_agent` *call* timestamps), and a cache-read rebill estimate (token
usage attributed to the intervals between consecutive polls where
`token_count` events allow it; else the coarser proxy — session total
cache-read tokens × (wait calls / total tool calls), labeled `proxy`).

**Success criterion:** none — Amendment 1 scopes E7-E9 as descriptive
MINE-tier census work ("no new run spend"), not a discrimination-gated
experiment. The check is whether the independently-built scorer reproduces
the two already-published external figures above and whether the battery
runs land materially lower, as predicted.

### 2026-07-29 — E7 wait-polling census: prediction check (Amendment 1)

`rollout_parser.wait_outcomes()` (call_id-paired `wait_agent` outcome
classification, TDD, 2 new tests) + `score_e7.py` (per-session/per-run
census: paired count, timeout rate, inter-poll interval p50/p95,
cache-read rebill estimate) built and run over all three pre-registered
corpora. Full tables and the manual-inspection sample:
`campaigns/codex-efficiency/out/e7-report.md`.

**Two of three predicted clauses CONFIRMED; one FAILS:**

1. **Drew's stress-2703 run (~78% of ~805): CONFIRMED.** 805 raw calls,
   78.3% of all calls / 78.4% of paired outcomes time out.
2. **Audit's high-wait Remux root (788/1058, ~74%): CONFIRMED exactly.**
   788/1058 = 74.5%, reproducing Finding 7's published figure via an
   independently-built pairing algorithm (the root itself was located via
   a pre-existing counter before `wait_outcomes()` existed — see the
   pre-registration entry above — but the 788/1058 split is
   `wait_outcomes()`'s own output, not assumed).
3. **Our own `cx-eff-*` battery runs show materially lower timeout
   rates: FAILS.** dev arm: 67.1%/69.3%. spinout arm: 60.2%/62.1%. Lower
   than the external corpora (74-80%) by 10-20 points, but not
   "materially lower" as the registered rationale implied. Reframed, not
   walked back: the pre-registration's assumption was that timeout rate
   tracks session length/load; the data instead points to a mismatch
   between `wait_agent`'s typical poll timeout (10-30s, the dominant
   `timeout_ms` value in *every* corpus scored, including ours) and how
   long a spawned child actually takes to finish real work — a mismatch
   present even in a fresh 3-task battery, not a pathology confined to
   huge sessions. This is a genuine miss on the registered prediction.

**Schema note:** the `multi_agent_v1` namespace (Drew's codex-5_5 run —
the same namespace that leaves `extract_spawns()`'s `fork_turns`/
`task_name` at `"(omitted)"`, per the Drew cross-validation entry above)
uses a *different* wait-output envelope (`{"status":{...},"timed_out":
bool}` vs. the `collaboration` namespace's `{"message":...,"timed_out":
bool}`) but the **same top-level `timed_out` key**, so `wait_outcomes()`
needed no namespace-specific branch — confirmed on codex-5_5's 26/26
paired calls (0 excluded). No `multi_agent_v1` schema gap for wait
pairing, unlike the fork-hygiene fields.

**Corpus (b)'s "direct human `gpt-5.6-sol` task roots" — not a
reproduction of Finding 8.** The audit's own methodology describes that
population as manually deep-read, not filterable. We documented our own
mechanical proxy instead (depth-0/`user`/`gpt-5.6-sol` roots with
root-family ≤20 sessions) rather than guess at the original selection:
214 candidate roots, only 3 with any `wait_agent` activity at all (80.4%
of their 209 paired calls time out — weak, exploratory support, n=3, our
own definition). Flagged in the report as not citable against Finding 8's
"nine tasks, 111 reads" figure.

**Cache-read rebill:** the "attributed" method (token_count events
between consecutive polls) worked cleanly on every session scored — no
session fell through to the coarser proxy (every session had ≥90% of its
inter-poll intervals containing at least one `token_count` event). The
audit's high-wait root: 381.8M of its 412.3M total cache-read tokens
(92.6%) fall inside inter-poll windows; Drew's stress-2703 root: 369.1M
of 376.6M (98.0%); our battery sessions: 43.3%/42.5% (dev/spinout) — much
lower because these short sessions spend proportionally less of their
activity polling.

**Manual inspection (n=10, seed=42):** all 10 sampled marker texts match
their `timed_out` classification exactly (`"Wait timed out."` ↔ `True`,
`"Wait completed."` ↔ `False`), sampled across all three corpora — no
misclassification observed.

**No budget spent** (MINE tier, existing corpora only, no quorum/Codex
runs). Sub `used_percent` and $ cost: not applicable, no ledger row
added.

### 2026-07-29 — E8 PRE-REGISTRATION: close_agent hygiene census (Amendment 1, Tasks E7-E9)

Registered before `score_e8.py` (or the parser's `lifecycle_calls()`) exists,
per the campaign's build-order rule (Global Constraints: "a scorer issues no
verdict until validated against corpus ground truth AND its matches are
manually inspected"). Every figure below comes from pre-existing counters
(Drew's own `sessions.json`, the audit's `metrics-all.jsonl` /
`state_5.sqlite`) or a plain `grep` over raw rollout files — never from the
not-yet-built `lifecycle_calls()`/`score_e8.py`, so this doesn't pre-empt the
prediction it's meant to check.

**Prediction:**

- **Drew's corpus, reconciled figures verified this task (not taken from the
  Drew-cross-validation entry on faith).** The Amendment-1 task brief's "sol
  0/86" and "codex-5_5 18/18" come from Drew's `sessions.json`, not
  `dispatch.json` — checked directly: `dispatch.json` (both the top-level and
  `stress-2703/metrics/` copies) carries only per-spawn dispatch tuples
  (`args`, `hint`, `hint_honored`, etc.), no `close_agent` field anywhere.
  The actual close counts live in `sessions.json`'s per-session `tool_calls`
  census, read directly for each run's controller (`role: "controller"`)
  record:
  - codex-5_5 root: `tool_calls.spawn_agent: 18`, `tool_calls.close_agent:
    18` → 18/18.
  - sol-5_6 root: `tool_calls.spawn_agent: 19`, `close_agent` key **absent**
    (0/19).
  - stress-2703 root (separate `sessions.json` under
    `analysis/stress-2703/metrics/`): `tool_calls.spawn_agent: 83`,
    `close_agent` key **absent**. Drew's own `report-addendum.md` cites this
    as "0/67" using his children-file-count denominator (§"E8 priors" of the
    Drew cross-validation entry above); our own scorer will use
    `extract_spawns()`'s raw call count (83) as its denominator instead —
    both conventions agree the numerator is exactly zero, only the
    denominator differs, and that's registered explicitly here so a future
    reader doesn't mistake a denominator-convention difference for a
    mismatch. "Sol 0/86" = sol-5_6's 19 + stress-2703's 67 (Drew's own
    children-count convention) — reconciled and holds; grep-confirmed
    independently just now that **zero** rollout files in either the
    sol-5_6 or stress-2703 corpus (root or any child) contain a
    `"name":"close_agent"` string at all, vs. exactly **one** file
    (codex-5_5's root) in the codex-5_5 corpus.
  - **Our prediction:** `score_e8.py`, once built, reproduces `n_close_agent
    == 0` for the sol-5_6 and stress-2703 root sessions and `18/18` for
    codex-5_5's root, using `lifecycle_calls()` — independently, not copied
    from Drew's numbers.

- **Audit corpus, window-scoped (not the full-history sqlite).** The plan
  brief's "`thread_spawn_edges` status 'open' 2,499 vs 'closed' 2,202"
  figure is real — confirmed directly in this machine's local Codex CLI
  state db (`sqlite3 ~/.codex/state_5.sqlite "SELECT status, COUNT(*) FROM
  thread_spawn_edges GROUP BY status"` → `closed|2202`, `open|2499`) — but
  that table is this machine's full lifetime history across every project,
  not scoped to the 2026-07-14–07-28 audit window, so it is **not** used as
  the registered audit-corpus prediction. Registered instead, from
  pre-existing per-session `tool_counts` in `metrics-all.jsonl` (no rollout
  parsing, matching E7's pre-registration discipline):
  - E7's high-wait Remux root (`019f95af-9a8e-7cb3-bc01-edcfe8b343e8`,
    model `gpt-5.6-luna`, not `-sol` — noted since the population below is
    `-sol`-filtered and this root isn't a member of it, just a second data
    point): `tool_counts.spawn_agent = 123`, `close_agent` key **absent**
    (0/123). Same session also carries `followup_task: 71` and
    `interrupt_agent: 13` — real, nonzero context counts for those two
    tools, registered here so E8's "for context" columns have a concrete
    expectation to check against, not just close_agent's near-zero.
  - E7's direct-human-`gpt-5.6-sol` proxy population (214 candidate roots,
    same selection filters `_direct_human_sol_candidates()` documents —
    depth 0, `thread_source:"user"`, `model:"gpt-5.6-sol"`, root-family
    size ≤20, excluding the high-wait root): summed directly from
    `metrics-all.jsonl` `tool_counts` across all 214 (no rollout parsing) —
    only 2 of 214 have any `spawn_agent` activity at all (16 raw
    `spawn_agent` calls total across those 2), and `close_agent` is
    **absent from every one of the 214** (0/16).
  - **Prediction: near-zero close_agent calls among these window-scoped
    audit populations** — for the high-wait root, exactly zero against 123
    spawns; for the sol proxy population, exactly zero against a small
    16-spawn base (most of the 214 candidates never spawn at all, so this
    is a thin population — flagged as thin now, not discovered as a
    surprise later).

- **Our own `cx-eff-*` battery runs (12 scored reps across dev/spinout arms,
  Tasks 6/6b):** predict **zero** close_agent calls in either arm —
  grep-confirmed now, before the scorer exists: `close_agent` absent from
  every rollout in all 12 reps; `followup_task` appears exactly 3 times,
  only in the spinout arm (reps 3/7/8); `interrupt_agent`/`resume_agent`
  absent everywhere.

**Scorer (to be built next):** `rollout_parser.lifecycle_calls()` — same
envelope handling as `extract_spawns()` (a `function_call` under
`response_item`; `namespace` is NOT filtered on, matching `extract_spawns`'s
own convention — confirmed directly that `close_agent` appears under BOTH
the `"collaboration"` namespace, our battery runs and most of the audit
corpus, AND the `"multi_agent_v1"` namespace, Drew's codex-5_5 run and some
audit sessions, with an identical `{"target": "<agent id>"}` argument shape
in both). `score_e8.py`: per-controller census (any session with ≥1
`extract_spawns()` spawn counts as a controller) — spawn count, close_agent
count, closure rate (`close/spawn`, our own scorer's raw-call convention,
chosen to match Drew's own `sessions.json` `tool_calls` semantics exactly
for cross-validation), plus `interrupt_agent`/`followup_task`/`resume_agent`/
`list_agents` counts for context.

**Success criterion:** none — Amendment 1 scopes E7-E9 as descriptive
MINE-tier census work ("no new run spend"), not a discrimination-gated
experiment, same as E7. The check is whether the independently-built scorer
reproduces the reconciled Drew figures and the audit/battery near-zero
pattern registered above.

### 2026-07-29 — E8 close_agent hygiene census: prediction check (Amendment 1)

`rollout_parser.lifecycle_calls()` (call-level extraction of
close_agent/interrupt_agent/followup_task/resume_agent/list_agents, TDD, 2
new tests) + `score_e8.py` (per-controller census: spawn count, close_agent
count, closure rate, context counts) built and run over all three
pre-registered corpora, reusing `score_e7.py`'s own audit-population
selection code directly. Full tables and the complete close_agent-call
listing: `campaigns/codex-efficiency/out/e8-report.md`.

**All three predicted clauses CONFIRMED:**

1. **Drew's sol controllers 0/86 vs. codex-5_5 18/18: CONFIRMED.** codex-5_5
   18/18 (100%), sol-5_6 0/19, stress-2703 0/84 (our own scorer's raw
   denominator; 0/67 under Drew's own children-count denominator — both
   agree the numerator is zero). Independently re-verified against raw
   rollout bytes (an ad hoc Python re-scan of codex-5_5's root rollout
   found the same 18 `(call_id, timestamp)` pairs the scorer did) and
   against Drew's own `sessions.json` `tool_calls` census (bypassing our
   scorer entirely) — not just reproduced by construction.
2. **Audit corpus, window-scoped near-zero: CONFIRMED, and stronger than
   predicted.** High-wait Remux root: 0/123 (not just near-zero — exactly
   zero). Direct-human-`gpt-5.6-sol` proxy sample (E7's own 214-candidate
   population, reused directly): 0/16, though this is a thin base (only 2
   of 214 candidates spawn anything at all), flagged as thin in the
   pre-registration before scoring, not discovered as a surprise after.
3. **Our own battery runs, both arms: CONFIRMED.** dev 0/48, spinout 0/67
   — zero `close_agent` calls anywhere in 14 scored reps, matching the
   pre-registration's grep-confirmed prediction exactly, including the
   exact `followup_task` count (3, spinout-only).

**The underlying pattern is binary, not graded.** Across every controller
in every corpus scored, closure rate is either ~100% (codex-5_5's single
`multi_agent_v1`-namespace controller, 18/18) or exactly 0% (every other
controller scored, all `collaboration`-namespace runs) — no partial-closure
controller was found anywhere. Why codex-5_5 is the sole exception
(model/harness config vs. a more disciplined controller run) was not
investigated in this task.

**`dispatch.json` does not carry close_agent data — checked directly, not
assumed.** Both copies in Drew's package contain only per-spawn dispatch
tuples (`args`/`hint`/`hint_honored`), no `close_agent` field. The
reconciled numbers (and the "sol 0/86" figure this task's prediction was
registered against) come from `sessions.json`'s `tool_calls` census
instead, read directly this task.

**Privacy finding (load-bearing for scorer design, not just a footnote):**
a `close_agent` `function_call_output` carries `{"previous_status":
{"completed": "<the child's full final message/report>"}}` — verified
directly against a real audit rollout while building this task, unlike
`wait_agent`'s content-free status envelope (E7). `lifecycle_calls()`
never reads `function_call_output` at all (only the calling
`function_call`'s `arguments`), so this scorer has no code path that could
print child report content, by construction. The manual-inspection section
lists every close_agent call found (n=18, all from codex-5_5) as
call_id/timestamp/args_task_name only, per the task brief's "counts +
task_name only" instruction.

**Closure-rate definition:** a raw within-session call-count ratio
(`close_agent` calls / `extract_spawns()` count), chosen to match Drew's
own `sessions.json` `tool_calls` semantics exactly for cross-validation —
not a `target`-id-matched measure against `child_links()`. Flagged as a
scope restriction in `out/e8-report.md`, not fixed in this task (the
`LifecycleCall` dataclass, per the task brief, has no `target` field).

**No budget spent** (MINE tier, existing corpora only, no quorum/Codex
runs). Sub `used_percent` and $ cost: not applicable, no ledger row added.

### 2026-07-29 — E9 PRE-REGISTRATION: workspace-leak census (Amendment 1, Tasks E7-E9)

Registered before `score_e9.py` exists, per the campaign's build-order rule.
E9 differs from E7/E8: it scores **git repos** (run workdirs), not rollout
JSONL, so there is no `rollout_parser.py` change to make first — the
"ground-check before scorer" discipline here means running plain read-only
`git log`/`git ls-tree` by hand, once, before writing any scoring code.

**Drew's fractals set — the task brief's "3 of 4 runs" claim does NOT match
either the raw git history or Drew's own analysis; traced to source and
corrected here, not carried forward uncritically.**

- **Task brief's claim, as given:** "3 of 4 runs shipped `.superpowers/sdd/`
  workspace files into git history."
- **Ground check just now** (`git log --all --diff-filter=A --name-only
  --pretty='@@COMMIT@@%H%x09%s' -- '.superpowers'`, run by hand against all
  four `awesome-fractals-fcu-*` repos under
  `/Users/jesse/git/superpowers/_tmp/drew-sdd-head-to-head-2026-07-27/sdd-testing-fresh/`):
  **2 of 4, not 3 of 4.**
  - `awesome-fractals-fcu-codex-5_5`: 4 paths added across 4 commits
    (`2f72702` Task 3, `07d34e2` Task 4, `8842b73` Task 6, `f4fed14` Task 7).
  - `awesome-fractals-fcu-sol-5_6`: 1 path added (`d5e66d0`, Task 4).
  - `awesome-fractals-fcu-opus-4_8`: 0 (confirmed with an unrestricted
    `git log --all -p | grep -c '\.superpowers'` too — zero mentions of
    `.superpowers` anywhere in this repo's history, not just zero Added
    paths).
  - `awesome-fractals-fcu-opus-5`: 0 (same unrestricted check, zero
    mentions).
  - **None of the four have any `.superpowers` path in the current HEAD
    tree** (`git ls-tree -r --name-only HEAD -- '.superpowers'` empty for
    all four) — both leaking repos self-cured via a later removal commit on
    the same branch (`8d97818`/`c5abb3a` for codex-5_5, `fa2bb75` for
    sol-5_6), so by a HEAD-presence definition all four repos currently
    "ship clean"; only by an ever-added-to-history definition do 2 of 4
    count as leaks.
- **Where "3" likely comes from — traced, not guessed.** Drew's own
  `analysis/report.md` (line 94) says: "5 force-adds of `.superpowers/sdd/`
  reports across both Codex runs; **3 reached the branch unflagged in
  codex-5_5**." That is a within-codex-5_5 count (3 of its leaks rode in
  silently inside planned feat commits, vs. the 4th being a deliberate,
  self-flagged `docs:` commit) — a different denominator (3 of one run's
  leaks) than "3 of 4 runs." Drew's own `analysis/narratives/scope-audit.md`
  (the actual per-run leak narrative, §"SDD workspace leakage into git")
  states the runs-level count explicitly and it agrees with our ground
  check exactly: "Both Claude runs honored that perfectly — no
  `.superpowers` path ever appears in opus-4_8 or opus-5 history. Both
  Codex runs leaked" — i.e. 2 of 4, with the same commit SHAs we found
  independently (`d5e66d0`/`fa2bb75` for sol-5_6; `2f72702`/`07d34e2`/
  `8842b73`/`f4fed14`/`8d97818`/`c5abb3a` for codex-5_5). **Registering the
  corrected figure (2 of 4) as what `score_e9.py` must reproduce**, not the
  task brief's "3 of 4" — flagging the brief's figure as traced to a
  misapplied denominator from Drew's own materials, not a data
  disagreement with Drew.

**Our own battery workdirs — predict some nonzero leak rate on both arms;
ground-checked now, before the scorer exists.**

- Prediction (registered per the task brief): some nonzero leak rate on
  both `dev` and `spinout` arms, on the theory that the `cx-sdd-small`
  fixture drives the same SDD workflow (task-N-report.md etc. written to
  `.superpowers/sdd/`) that produced Drew's Codex-side leaks.
- **Ground check just now**, all 14 real `coding-agent-workdir` git repos
  under `evals/results/cx-eff-cx-sdd-small-{dev,spinout}-rep*/*/` (dev
  rep1-6, spinout rep1-8; see "data-quality note" below for a 15th
  candidate directory excluded from this count): **0 of 14 have any
  `.superpowers` path ever added** (`added=0`) **and 0 of 14 have any in
  HEAD** (`in_head=0`) — flatly contradicting the nonzero prediction.
  Registering the miss now, before the scorer exists, rather than
  reframing after.
- **Mechanism spot-checked (not exhaustively investigated — flagged as an
  open question, matching Drew's own unresolved one below).** Two guards
  are visibly present: (1) every repo has a workspace-internal
  `.superpowers/sdd/.gitignore` containing `*` (git status shows it `!!`
  ignored in every repo checked) — this matches Drew's own domain-review
  note that all four of *his* fractals repos also end up with this same
  nested self-ignore file; (2) in 10 of the 14 battery repos, the agent
  itself additionally committed a repo-root `.gitignore` containing
  `.superpowers/` as an early, own-initiative hygiene commit — confirmed
  NOT scripted by `setup-helpers` (grepped `evals/src/setup-helpers/*.ts`:
  neither `init_repo_from_fixtures` nor `symlink_superpowers` touches
  `.gitignore` or makes a second commit; `initRepoFromFixtures` makes
  exactly one commit, "seed scenario fixtures"), and the commit message
  itself varies across reps ("chore: ignore development workspaces",
  "chore: ignore local worktrees", "chore: ignore development artifacts",
  "chore: ignore local workspaces", "chore: ignore local worktree
  artifacts") — i.e. genuinely agent-authored wording, not a fixed
  template string. The other 4 reps (dev-rep3, spinout-rep1/2/3) have no
  such root `.gitignore` commit at all yet still show zero leaks, so guard
  (1) alone appears sufficient on its own. Why guard (1) held reliably
  here but did not prevent Drew's Codex-side leaks is Drew's own flagged
  "open mechanism question" (`scope-audit.md`: the nested ignore file's
  mtime in his repos post-dates the run, "harness-mechanism ... vs.
  model-behavior ... indeterminate") — not re-investigated or resolved by
  this task; noted here only as the most plausible explanation for the
  prediction miss, not as a settled cause.

**Data-quality note, found while locating the 14 battery repos (must be
guarded against in the scorer, not just noted):**
`evals/results/cx-eff-cx-sdd-small-spinout-rep6/` contains a 15th directory
matching the naming pattern
(`cx-eff-cx-sdd-small-codex-.../coding-agent-workdir`, an artifact of a
retried/duplicated run) that has **no `.git` of its own**. Running any git
command with `cwd` set to it does not fail — it silently resolves upward
through the filesystem to the **evals checkout's own git repo**
(`git rev-parse --show-toplevel` from inside it prints
`/Users/jesse/git/superpowers/superpowers/evals`; `--git-dir` prints
`/Users/jesse/git/superpowers/superpowers/.git/modules/evals`, the
submodule gitdir). Scoring that directory under the `cx-eff-...` label
would silently report the *entire evals repo's* history as if it were one
battery run's workdir. `score_e9.py` must check for a directory's **own**
`.git` entry (`os.path.exists(os.path.join(d, ".git"))`) before invoking
git at all, never rely on `git rev-parse --is-inside-work-tree` from
inside the target directory for this decision. This directory is excluded
from the "14" count above and will be excluded (skipped, logged) by the
scorer.

**Scorer (to be built next, `score_e9.py`, no `rollout_parser.py` change
needed):** per repo, read-only `git` subprocess calls with `cwd=repo_dir`
only (`log --all`, `log` [HEAD-reachable], `ls-tree`; never a mutating
command) —

- (a) workspace paths **ever added in history**: `git log --all
  --diff-filter=A --name-only --pretty=... -- '.superpowers'`.
- (b) workspace paths **present in HEAD**: `git ls-tree -r --name-only HEAD
  -- '.superpowers'`.
- (c) workspace paths added in **any commit reachable from HEAD** (same
  query as (a), without `--all`) — classifies each path in (a) as
  leaked-and-still-shipped (in (b)), leaked-then-removed (in (c) but not
  (b)), or leaked-on-an-unreachable-ref (in (a) but not (c)).

`FORCE=1`/`--force` overwrite guard on any JSON output, matching
`score_e1.py`/`score_e8.py`'s convention.

**Success criterion:** none — same as E7/E8, descriptive MINE-tier census,
no new run spend. The check is whether the independently-built scorer
reproduces the corrected Drew figure (2 of 4, not the task brief's 3 of 4)
and the battery's 0-of-14 ground check above.

**No budget spent** (MINE tier, existing corpora only, no quorum/Codex
runs). Sub `used_percent` and $ cost: not applicable, no ledger row added.

### 2026-07-29 — E9 workspace-leak census: prediction check (Amendment 1)

`score_e9.py` (no `rollout_parser.py` change -- E9 scores git history of
run workdirs, not rollout JSONL; TDD, 6 new tests in `test_score_e9.py`)
built and run over both pre-registered corpora. Full tables, the complete
5-path leak listing with commit subjects, and the read-only verification
section: `campaigns/codex-efficiency/out/e9-report.md`.

**Both pre-registered clauses land as predicted; the scorer reproduces the
pre-registration's hand count exactly, to the individual commit SHA:**

1. **Drew's fractals set, corrected figure (2 of 4, not the task brief's
   original 3 of 4): CONFIRMED exactly.** `codex-5_5`: 4 paths added, all 4
   later removed (status=removed for all 4, 0 shipped). `sol-5_6`: 1 path
   added, removed. `opus-4_8`/`opus-5`: 0. Every commit SHA and subject
   line the scorer extracted matches the pre-registration's hand count
   character-for-character, and matches Drew's own
   `analysis/narratives/scope-audit.md` narrative independently (same six
   SHAs he names: `2f72702`, `07d34e2`, `8842b73`, `f4fed14` for
   codex-5_5's four leaks and cleanup, `d5e66d0` for sol-5_6's one).
2. **Our own battery, both arms: FAILS as predicted-to-fail — 0 of 14
   real repos leaked.** Matches the pre-registration's own ground check
   exactly (that ground check was done by hand before the scorer existed;
   this is the scorer independently reproducing it, not the scorer's only
   evidence for the number). Not reframed as a pass: the pre-registration
   predicted nonzero and got zero. The most plausible mechanism (the
   workspace-internal `.superpowers/sdd/.gitignore` containing `*`,
   present in all 14 repos, plus an agent-initiated root `.gitignore` in
   10 of 14) was already identified during pre-registration and nothing
   found while building the scorer contradicts it — see `out/e9-report.md`
   Concerns for why this isn't treated as a settled explanation (it's the
   same guard Drew's own domain review found present-but-not-always-
   effective in his four fractals repos, and his own mechanism question
   there stays open, un-re-investigated by this task).

**Real bug found and regression-tested, not just a defensive check added
on spec.** While locating the battery's 14 real repos, one candidate
directory (an artifact of a retried run under
`cx-eff-cx-sdd-small-spinout-rep6/`) turned out to have no `.git` of its
own. `git rev-parse --show-toplevel` run with `cwd` set to it does not
fail -- it silently resolves upward to the **`evals` checkout's own git
repo** via the submodule gitdir
(`.../superpowers/.git/modules/evals`). Had the scorer used
`git rev-parse --is-inside-work-tree` (or any bare git subprocess call) as
its "is this a repo" test, it would have silently scored that unrelated
directory as a battery repo and reported the entire `evals` checkout's
history under a misleading per-rep label. `score_e9.py` instead checks for
the directory's own `.git` entry on the filesystem before ever invoking
git; `test_score_e9.py::test_nested_dir_without_own_git_is_not_scorable`
reconstructs the same nested-no-`.git`-inside-a-real-repo shape and
asserts it is skipped, not silently escalated.

**Read-only, verified not assumed.** Every scored repo's `git status
--porcelain` was diffed before/after running `score_e9.py` (both corpora,
all reps): identical every time; the only untracked entries present
predate this task (setup.sh's `.agents/skills/superpowers` symlink,
`__pycache__/` from the agent's own test runs, session-ID marker files in
Drew's repos). The scorer issues only `git log`, `git ls-tree`, and `git
rev-parse --verify` -- no command that can write.

**Audit corpus not scored (by design, not omission).** E9 needs a
persisted git working-tree history to query; the audit corpus is Codex
rollout JSONL only, with no corresponding checked-out git repo to run `git
log`/`git ls-tree` against. Amendment 1's task list already scopes E9 to
"run workdir[s]" specifically (unlike E7/E8's three-corpora framing), read
as intentional -- flagged explicitly in `out/e9-report.md` Concerns since
Amendment 1's summary paragraph says "each scores three corpora."

**No budget spent** (MINE tier, existing corpora only, no quorum/Codex
runs). Sub `used_percent` and $ cost: not applicable, no ledger row added.

### 2026-07-29 — E9 fix round 1: review-package surface (workspace-in-diff)

Task review found the initial E9 submission implemented only the first
half of the plan's E9 bullet (git-history leaks) and silently dropped the
second half ("plus workspace-in-diff at review packages") without flagging
it as a scope decision -- breaking the scorer's otherwise-consistent
practice of flagging every scope decision explicitly. This entry appends
the fix; the two entries above (pre-registration, prediction check) are
unedited.

**What "workspace-in-diff at review packages" means, operationalized:** a
review package is a diff artifact following the SDD skill's own
`review-<sha>..<sha>.diff` naming convention (matched broadly:
`review*.diff` / `*review*.diff`, any filename shape); "workspace-in-diff"
means the diff ITSELF names a `.superpowers/` path in one of its own
header lines (`diff --git a/... b/...`, `--- a/...`, `+++ b/...`) -- the
exact condition Drew Ritter's own review-prompt convention treats as an
automatic finding (`analysis/report.md`/`cross-run-comparison.md`: "any
workspace path (`.superpowers/**`) appearing in the review diff is an
automatic finding").

**`score_review_packages()` added to `score_e9.py`** (TDD, 1 new test in
`test_score_e9.py`, total 7/7 passing): searches each repo's working tree
(plain filesystem walk excluding `.git/` -- how a review package left in
the normally-gitignored `.superpowers/sdd/<plan>/` workspace is found at
all) and git history (`git log --all --diff-filter=A --name-only`,
UNrestricted by the `.superpowers` pathspec this time since a review
package need not live under it -- filtered client-side by filename
instead). Content is read ONLY to extract diff HEADER lines -- never a
hunk (`@@`) or content (`+`/`-`) line -- via a regex that matches
exclusively `diff --git `/`--- `/`+++ `-prefixed lines; historical blobs
are read via `git show <commit>:<path>` (still read-only, no checkout).
The new test's synthetic diff's hunk-body placeholder line is deliberately
named `HUNK_BODY_MUST_NEVER_BE_READ_FOR_PATH_EXTRACTION` so a
header/body-boundary regression would be obvious, not silent.

**Both corpora genuinely searched, both SCORED ZERO -- a census result,
not an omission, matching the fix instruction's explicit requirement:**

- **Drew's fractals corpus (4 repos, working tree + all-refs history):
  0 review-package artifacts found.** Consistent with, not contradicted
  by, his own materials -- his review-diff artifacts live in a separate
  `analysis/` directory tree outside these four product-code repos
  entirely, so there is nothing under any of their own git histories to
  find.
- **Our own battery corpus (14 real repos, working tree + all-refs
  history): 0 review-package artifacts found.** The `cx-sdd-small`
  fixture's 3-task plan does not appear to have produced a fix-round
  review loop (and its `review-<sha>..<sha>.diff` artifact) inside any of
  the 14 scored workdirs -- unlike this very campaign's own SDD workspace
  (`.superpowers/sdd/2026-07-28-codex-efficiency-evals/`), which genuinely
  does contain multiple such files (visible in `task-e8-report.md`'s
  directory listing), confirming the naming convention and detection
  pattern are correct against a real example -- just not one inside either
  corpus E9 scores.
- **No workspace-in-diff artifact found anywhere** -- there is nothing to
  flag, because there is no review-package artifact of any kind in either
  corpus to inspect. The detection logic itself is verified only against
  `test_score_e9.py`'s synthetic fixture (a fake `review-abc123..def456.diff`
  whose header names `.superpowers/sdd/task-1-report.md`, correctly
  flagged `workspace_in_diff=True` with exactly that one path extracted)
  -- flagged in `out/e9-report.md` Concerns as a real (not just
  theoretical) gap: the extraction logic has not been checked against any
  real leaked review diff, because none exists in the data available to
  this task.

**Read-only preserved.** Every scored repo's `git status --porcelain` was
diffed before/after this pass too (both corpora, all reps): identical in
every case, same as the original E9 pass. `FORCE=1` re-run to regenerate
`out/e9-battery.json` (force-added, tracked) and `out/e9-drew.json`
(regenerated on disk, still deliberately left untracked -- same rationale
as before: real absolute paths into an external/private corpus).

`python3 test_score_e9.py`: 7/7 pass. `python3 test_rollout_parser.py`:
10/10 pass (unchanged). `python3 test_score_e1.py`: 6/6 pass (no
regression).

**No budget spent** (MINE tier, existing corpora only, no quorum/Codex
runs). Sub `used_percent` and $ cost: not applicable, no ledger row added.

### 2026-07-29 — E2-MICRO PRE-REGISTRATION: reviewer non-delegation phrasing sweep (Task 7)

Registered before `reviewer-recursion-micro.py` runs, per the campaign's
pre-registration discipline. E2's own baseline entry above (registered
2026-07-28) predicts a dispatched branch reviewer produces >=1 descendant
in >=half of reps at FULL scale; this MICRO is the cheap first probe at a
fix, per the spec's MINE -> MICRO -> FULL tier plan for E2. It does not
attempt to reproduce the FULL-scale baseline pathology itself (a single
task-scoped review, not a whole-branch review over a long session) — see
the scoring-nuance caveat below.

**Design:** four variants, holding a fixed review task (a real 60-line
diff, `campaigns/codex-efficiency/fixtures/review-micro/`, containing one
seeded off-by-one loop-bound bug in `moving_average` that the fixture's
own shipped tests do not catch — verified by hand: all 6 shipped tests
pass against the buggy implementation) constant and varying only the
dispatch prompt's delegation guidance:

- **Z-null** — a bare review request, no SDD template, no delegation
  guidance either way (negative control).
- **A-control** — the current `dev`-arm
  `subagent-driven-development/task-reviewer-prompt.md` template,
  verbatim (the exact text Finding 2 was raised against), with this
  fixture's placeholders filled in. This template currently says nothing
  about delegation in either direction.
- **B-contract** — A + an explicit personal-performance contract:
  "You personally perform this review. Do not spawn, delegate to, or
  wait on any other agent; produce findings directly."
- **C-budget** — A + a hard numeric budget framed as a protocol
  violation: "Hard budget: 0 subagents. Any delegation is a protocol
  violation reported as failure."

REPS=5 per variant (20 single-turn `codex exec` samples total), cached
per (variant, rep). Scored two ways: `len(extract_spawns(rollout)) > 0`
(does the reviewer delegate at all) and whether the seeded bug is named
in the answer file (a regex over the bug's identifying tokens, findings-
quality guard — cross-checked by a full manual read of every answer file
before the regex count is trusted, not just the 3-per-variant sample the
written report quotes from).

**Prediction:**

- **Z-null and A-control may spawn in some reps** — neither variant tells
  the reviewer not to delegate, and A-control is the literal template
  Finding 2 was raised against, so if the underlying pathology exists at
  all at this task-scoped (not whole-branch) scale, it should show up
  here first, not be fully suppressed.
- **B-contract and C-budget spawn in zero reps** — both variants add an
  explicit, unambiguous prohibition on delegation to the same base
  template; if phrasing is the lever, an explicit contract should drive
  spawn incidence to zero.
- **Bug-found rate is comparable across all four variants** — the
  question this micro is built to answer is whether suppressing
  delegation costs findings quality. The prediction is that it does not:
  a competent reviewer catches this diff-visible, docstring-contradicting
  off-by-one whether or not it delegates.

**Scoring-nuance caveat, registered up front (per the task instruction,
citing E1's own experience):** fresh, single-turn `codex exec` sessions
rarely delegate at all, independent of phrasing — E1's baseline SDD
battery spawned readily, but every one of those spawns came from a
long-lived, skill-primed controller session running a multi-task plan,
not a single fresh `codex exec` call. If ALL FOUR variants (including
Z-null) show zero spawns, that is an **inconclusive-by-zero** result for
this MICRO, not a confirmation that any phrasing "works" — it would mean
this rig's single-turn task-scoped shape doesn't elicit the pathology at
all, and the FULL scenario (Task 8: one branch review dispatched over a
prepared moderately-complex branch, matching the spec's E2 FULL tier)
carries the real baseline question. This MICRO's result will be reported
honestly either way, including a zero-across-the-board outcome.

**No run yet — this is the pre-registration.** Battery and verdict follow
in a separate log entry once `out/e2-micro.md` exists.

### 2026-07-29 — E2-MICRO RESULT: inconclusive-by-zero (Task 7)

Ran the pre-registered battery (`reviewer-recursion-micro.py`, 4 variants
x 5 reps = 20 single-turn `codex exec` samples, `campaigns/codex-efficiency/
fixtures/review-micro/` fixture). Full table, variant text, and manual-read
notes: `campaigns/codex-efficiency/out/e2-micro.md`.

**Result: 0/20 spawns (0%) across every variant, no exceptions —
independently confirmed by raw `grep -l '"name":"spawn_agent"'` across all
20 rollouts (zero matches), bypassing `extract_spawns()` entirely.**
Bug-found rate: 20/20 (100%) — every reviewer, including Z-null with no
SDD template at all, correctly named the seeded off-by-one loop bound
(`src/rolling.py`: `range(len(values) - window)` should be
`range(len(values) - window + 1)`) with file:line and the exact fix;
manually verified by reading all 20 answer files in full, not just the
3-per-variant sample the written report quotes from.

**This is the inconclusive-by-zero outcome the pre-registration named as a
live possibility, not a surprise reframed after the fact.** None of the
three predicted clauses can be evaluated as registered: Z-null/A-control
did not spawn in "some reps" (0/10 combined), B-contract/C-budget's
predicted zero holds trivially (0/10) but only because nothing in this
rig ever attempts delegation regardless of phrasing, and bug-found-rate
parity holds (100% flat) but for the same reason — there is no delegation
axis, phrasing or otherwise, for this MICRO shape to discriminate on.

**Root cause (hypothesis, not fully investigated): the rig's single-turn,
single-diff review has no natural sub-task to delegate**, independent of
prompt content — consistent with E1's own finding that every observed
spawn came from a long-lived, multi-task SDD controller session, never a
single fresh `codex exec` call. The corpus's recursive-reviewer pathology
(129-session Remux tree, 31-session Serf tree) involves large, long-lived
review trees, not a single small diff. **This MICRO does not confirm or
refute the registered E2 baseline prediction** (>=1 descendant in >=half
of reps at FULL/whole-branch scale) in either direction — it remains
untested. The FULL scenario (Task 8: one branch review dispatched over a
prepared moderately-complex branch) is still required to answer the
baseline question; per the pre-registration's own caveat, it "carries the
real baseline question."

**Side observation, not scored:** A-control/B-contract/C-budget samples
each issued exactly one `exec_command` (a single combined `sed -n`
reading all three fixture files); Z-null samples issued 2-4 separate
reads of the same files. Consistent with, not proof of, the template's
own "read the diff file once" instruction doing real work on a dimension
unrelated to delegation.

**Cost:** subscription-billed `codex exec`, no $ split. `used_percent`
flat at 8.0% across the entire battery (no measurable movement — the
battery's real cost was too small to register against the primary
window). Codex CLI `0.146.0` confirmed on all 20 samples. No ledger row
added (not a $-costed battery).

### 2026-07-29 — E2-FULL PRE-REGISTRATION: branch-review baseline (Task 8)

Registered before any `cx-branch-review` battery run, per the campaign's
pre-registration discipline. This is the FULL-tier baseline the E2-MICRO
entry above (Task 7, inconclusive-by-zero) explicitly deferred: "the FULL
scenario ... still carries the real baseline question."

**Rig, built this task (all under
`campaigns/codex-efficiency/`):**

- **Scenario:** `scenarios/cx-branch-review/` (`story.md`/`setup.sh`
  executable/`checks.sh` non-executable, `# coding-agents: codex` first
  line) — a quorum scenario, interactive (`quorum run ... --coding-agent
  codex`, NOT `codex exec`), `quorum_max_time: 20m`. The Gauntlet brief is
  a neutral engineer-oversight persona with no efficiency/measurement
  vocabulary anywhere in the body (Task 5's Gauntlet-blinding fix
  precedent, re-applied from the start here rather than fixed after the
  fact): "You are a software engineer who has been working on a small
  Python library ... on the `feature` branch. Implementation is done and
  you want a review before merging to `main`." The fixed typed message:
  "Please do a final review of the feature branch using your superpowers
  review skills before we merge." `bun run quorum check
  scenarios/cx-branch-review` passes (`ok cx-branch-review` / `ok
  credentials`).
- **Fixture:** `fixtures/branch-review/build.sh` (hand-authored git
  history — the review's INPUT, not skill output, per the task brief's
  explicit allowance) — a `main` baseline (2 files) plus a `feature`
  branch (checked out at the end) carrying 4 commits across 4 concerns:
  core logic (`taskqueue/queue.py`, `taskqueue/validators.py`), CLI
  (`taskqueue/cli.py`, `taskqueue/__main__.py`), tests
  (`tests/test_queue.py`, `tests/test_validators.py`,
  `tests/test_cli.py`), docs (`docs/USAGE.md`, `docs/DESIGN.md`,
  `README.md`). 10 files touched, **453 changed lines**
  (`git diff --stat main..feature`), 5 commits total (1 baseline + 4
  feature) — well past the "8-12 files / 300+ lines / several commits /
  3+ concerns" bar this task was scoped to, specifically so a reviewer
  has genuine surface area to consider splitting the review up (Task 7's
  lesson: a single-turn, single-diff review never delegates because
  there's no natural sub-task to delegate to).
  **Verified by hand before committing:** `python3 -m pytest tests/` on
  the built `feature` branch — 22/22 pass.
- **Two seeded issues, both confirmed live (not just asserted) and both
  invisible to the passing test suite:**
  1. **Missing edge-case test** — `taskqueue/queue.py:46-58`
     (`dequeue_batch(n)`) is correctly implemented for `n` greater than
     the queue's length or an empty queue (it returns whatever remains
     instead of raising, per its own docstring — confirmed by hand:
     `dequeue_batch(5)` on a 1-item queue returns the 1 item,
     `dequeue_batch(3)` on an empty queue returns `[]`, no exception
     either way), but `tests/test_queue.py` (lines 39-51) never exercises
     either path — only `n <= len(queue)`.
  2. **Docstring/behavior mismatch** — `taskqueue/queue.py:60-65`
     (`peek()`)'s docstring says "Returns None if the queue is empty";
     the implementation (`return self._heap[0][2]`) has no empty check
     and raises `IndexError` instead — confirmed by hand
     (`PriorityQueue().peek()` on a fresh queue raises
     `IndexError: list index out of range`). `docs/DESIGN.md` repeats the
     same (wrong, relative to the code) contract, so a reviewer who reads
     only the docs would be misled the same way; only reading `peek()`'s
     own body against its docstring catches it.
     `tests/test_queue.py` never calls `peek()` on an empty queue, so the
     suite stays green either way.
- **Scorer:** `score_e2.py` (TDD, 9 new tests in `test_score_e2.py`, all
  passing; existing suites unaffected — `test_rollout_parser.py` 10/10,
  `test_score_e1.py` 6/6, `test_score_e9.py` 7/7). Walks every rollout in
  a run's `home/.codex/sessions/**` TRANSITIVELY via `child_links()` (not
  just the root's own spawns, like `score_e1.py` — a reviewer that itself
  spawns further reviewers is exactly what this measures), starting from
  the chronologically-earliest rollout as root. Census per run:
  `total_sessions` (tree size, root included), `max_depth` (root = 0),
  `spawns_by_nonroot` (spawn_agent calls issued by anyone OTHER than
  root — the recursion signal, since the root dispatching one reviewer is
  the expected/intended single delegation), `missing_task_complete`
  (rollouts in the tree with zero `task_complete` events), `total_wait_calls`
  / `root_wait_calls`, and `orphan_rollouts` (rollout files present but
  unlinked from the tree). `score_run()` asserts root identity (the
  chronologically-earliest rollout's first `event_msg/user_message`
  contains the review-request marker) and raises `SystemExit` if that
  assertion fails, rather than silently scoring the wrong session as
  root — this is our own fixed Gauntlet prompt, not corpus content, so
  checking it for a known substring (never printing the raw text) is
  safe per this campaign's established precedent for Gauntlet-prompt
  text. `FORCE=1`/collision-refusal convention matches
  `score_e1.py`/`score_e8.py`/`score_e9.py`.

**Prediction (unchanged from the original E2 baseline entry above,
registered 2026-07-28):** a dispatched branch reviewer produces ≥1
descendant in ≥half of reps (i.e. **≥2 of 4 dev-arm reps show
`spawns_by_nonroot > 0`**, equivalently `max_depth >= 2` — a session
below the root itself spawning something further, NOT counting the
root's own single expected reviewer dispatch, which is the intended
baseline shape and does not by itself indicate the pathology).

**Alternative outcome, registered explicitly as a live possibility before
this battery runs (per Task 7's own instruction and the E1/E7
fresh-session lessons):** E1's baseline (Task 6) found 34/34 SDD spawns
isolated (`fork_turns:"none"`) on a fresh, short-lived `dev`-arm session
— axis B (fork-isolation) landed as **inconclusive-by-zero** and was
re-scoped into E6 (long-history/compaction elicitation), on the
hypothesis that the audit's own Finding 1/Finding 2 recursive-forking
narratives describe *long-running, heavily-loaded* controller sessions,
not short fresh dispatches. E2-MICRO (Task 7) independently found the
same shape at single-turn scale (0/20 spawns of any kind). **If this
FULL battery shows 0 reviewer descendants across all 4 dev reps
(`spawns_by_nonroot == 0` in every rep, i.e. review recursion never
occurs even once), that is recorded as inconclusive-by-zero for E2 on
fresh sessions, the same terminal state as E1's axis B** — the baseline
question (does review recursion happen at all, absent any intervention)
gets folded into E6's scope (long-history/compaction elicitation) rather
than re-attempted with more reps at this scenario shape, per the
discrimination rule (inconclusive-by-zero is a stop, not grounds to keep
spending on more reps chasing the same shape). This is registered now,
before the battery runs, exactly like E1 axis B and E2-MICRO's own
inconclusive-by-zero caveat — not a reframe invented after seeing a
disappointing result.

**Battery plan:** 4 reps, `dev` arm only (no treatment arm exists yet for
E2 — DESIGN.md's E2 tiers are MINE → MICRO → FULL baseline, no treatment
tier registered), sequential, via `run-quorum.sh dev cx-branch-review 4`.
Per the task instruction: if the discrimination gate reads 0 descendants
everywhere, do not run more reps chasing the pathology — record
inconclusive-by-zero and stop.

**Seeded-issue recall (secondary readout, not gating the discrimination
verdict):** per rep, whether both seeded issues (dequeue_batch edge-case
gap, peek() docstring mismatch) are named in the root session's final
`task_complete.last_agent_message` and/or any report-shaped file left in
the workdir. This checks findings quality, not delegation — registered
here so it's clear this is a secondary readout, not something the
discrimination gate depends on.

**No run yet — this is the pre-registration.** Battery, census, and
verdict follow in a separate log entry once `out/e2-report.md` exists.

## 2026-07-29 — EXTERNAL EVIDENCE: Codex source recon resolves E8's open question (controller entry)

Provenance: read-only recon of the Codex CLI source at ~/git/agent-harnesses/codex,
full report committed as docs/2026-07-29-codex-multiagent-v2-capabilities.md.

- E8's open question ("why is codex-5_5 the sole 18/18 closer?") is RESOLVED:
  close_agent exists only in multi-agent V1. codex-5_5 ran V1; sol/terra
  presets select V2, whose schema has no close_agent at all. E8's 0% closure
  on modern controllers is the harness schema, not agent indiscipline. V2
  auto-evicts finished children (LRU); unclosed children cost nothing.
  Drew's "checklist close_agent" recommendation is unexecutable on V2 and
  unnecessary. E8's scorer remains valid as a V1/V2 schema detector.
- E7's fix direction is confirmed and sharpened by source: wait_agent is an
  event subscription with a 1-hour max timeout; completed children push
  FINAL_ANSWERs into the controller mailbox with no wait needed while local
  work remains (trigger_turn=false caveat: one long wait when idle).
- Model-omission fix candidates: [agents].default_subagent_model config knob;
  note V2 spawn allowlist is sol/terra only, and the model-without-effort
  trap (effort resets to model default, sol->low).
- codex-tools.md (spinout branch) has five source-contradicted claims,
  enumerated in the doc — fix-cycle input.

## 2026-07-29 — Live probe: V2 spawn allowlist confirmed with codex children (controller entry)

5 codex exec probes (CLI 0.146.0, container, scratch homes; report in session scratchpad).
- sol controller: spawn model=terra OK (child ran terra); model=luna and model=gpt-5.5 both
  rejected verbatim "Unknown model `X` for spawn_agent. Available models: gpt-5.6-sol,
  gpt-5.6-terra"; model omitted inherits sol.
- Collaboration tools ARE present in codex exec mode (all 5 sessions) — E2 micro's 0/20
  spawn result is a genuine elicitation finding, not a tool-availability artifact.
- SURPRISE: Jesse's host ~/.codex/config.toml sets [features.multi_agent_v2] enabled=true,
  which OVERRIDES the model preset default (config/mod.rs multi_agent_version_override).
  So even a luna controller runs V2 under this config — luna gets V2's tool surface and
  cannot spawn any child (incl. itself; allowlist is sol/terra). True V1 behavior needs
  -c features.multi_agent_v2=false (not probed; budget 5 runs).

## 2026-07-29 — Live probe round 2: preset-default V1 vs V2 (controller entry)

4 runs, EMPTY config.toml (verified sufficient: preset governs when no override).
- luna preset-default = V1 (3/3 arms). V1 luna spawns sol OK, luna OK, inherit OK;
  V1 tool description advertises 5 spawnable models (sol/terra/luna/5.5/5.4) —
  no allowlist under V1, matching source.
- sol preset-default = V2 even with empty config — round 1's explicit
  multi_agent_v2.enabled=true only mattered for luna (wrongly forcing it into V2,
  where it cannot spawn at all).
- Default concurrency: V2 = 4 slots (live hint text); V1 = 6 (source constant,
  never surfaced in hint text).
- V1 schema differences beyond fork_context: wait_agent REQUIRES targets:[agent_id];
  V1 collab tools route through the code_mode JS sandbox as multi_agent_v1__* inside
  exec custom_tool_calls — different calling convention from V2's direct
  function_calls. This explains the audit's "older sessions invoke tools inside a
  single exec/JS call" observation (Corpus section, nested-call caveat).

## 2026-07-29 — Probe round 3 (controller entry)

Arm J: sol controller, empty config, no -m flag (implicit default): spawn
model=gpt-5.6-luna rejected byte-identically to round 1. The V2 sol/terra
allowlist holds under all three config regimes tested; sol can never spawn
luna children regardless of configuration.

### 2026-07-29 — E2-FULL RESULT: inconclusive-by-zero (Task 8)

Ran the pre-registered battery (4 reps, `dev` arm, `cx-branch-review`,
sequential, via `run-quorum.sh dev cx-branch-review 4`) and scored all 4
with `score_e2.py`. Full detail: `campaigns/codex-efficiency/out/e2-report.md`.

**Housekeeping note, zero cost:** the first `run-quorum.sh` invocation used
a `checks.sh` with a bug (`git-branch main` — that verb checks the
*current* branch, not existence; the fixture deliberately leaves `feature`
checked out at the end, so this always fails) and produced an
`indeterminate` rep1 with `gauntlet: null` / `economics: null` — no
Gauntlet or Codex session ever started, $0 spent. Fixed
`checks.sh` to assert `git-branch feature` (dropping the bad `git-branch
main` line), re-validated with `bun run quorum check`, then ran the real
4-rep battery. The leftover indeterminate directory
(`cx-eff-cx-branch-review-dev-rep1/..-1cc4`) was left in place, unscored.

**Result: 4/4 reps show the root dispatching exactly ONE reviewer child
(`total_sessions=2`, `max_depth=1` in every rep) — the expected, intended
single delegation. ZERO of the 4 reviewer children themselves spawned any
further descendant** (`spawns_by_nonroot=0` in all 4 reps) —
**independently confirmed** by raw `grep -c '"name":"spawn_agent"'`
against each of the 4 reviewer-child rollout files directly, bypassing
`extract_spawns()`/`score_e2.py` entirely: 0 matches in all 4. The
recursion pathology this experiment is built to detect never occurred
once across the battery.

**Discrimination gate, per the pre-registration's explicit operational
definition** (`spawns_by_nonroot > 0`, equivalently `max_depth >= 2`,
NOT counting the root's own single expected reviewer dispatch): **0/4
reps clear the bar. This is the alternative outcome registered above —
INCONCLUSIVE-BY-ZERO, not a pathology-absent "pass."** Per the
pre-registration and the task instruction, no further reps were run
chasing this shape. **E2's baseline question (does review recursion
happen at all, absent intervention) is folded into E6's scope
(long-history/compaction elicitation), the same terminal state as E1's
axis B** — consistent with the corpus's own Finding 1/Finding 2
narratives describing long-running, heavily-loaded controller sessions,
not a single fresh interactive dispatch. `score_e2.py`'s root-identity
assertion passed on all 4 reps (chronologically-earliest rollout's first
instruction matched the review-request marker in all 4) — the tree this
census is built on is the right tree; the zero result is not a
misidentified-root artifact.

**Seeded-issue recall (secondary readout, does not gate the
discrimination verdict), read from each rep's root session
`task_complete.last_agent_message` — the message actually relayed to the
Gauntlet, not just the dispatched reviewer's own private findings —
plus a check of the workdir for any left-behind report file (none found
in any rep; findings live only in the transcript, matching
`requesting-code-review`'s "return findings directly" convention, no
`.superpowers/` report artifact anywhere):**

- **Issue 2 (docstring/behavior mismatch, `queue.py` `peek()` raising
  `IndexError` instead of returning `None`): 4/4 (100%).** Every rep
  named the exact file:line, the exact contradiction (docstring +
  `docs/DESIGN.md` promise `None`, code doesn't check for empty), and the
  fix, and rated it "Important." This is the finding every reviewer
  converged on independently.
- **Issue 1 (missing edge-case test for `dequeue_batch(n)` at `n` >
  queue length / on an empty queue): 0/4 by strict match (no rep's
  *relayed* review named this gap at all).** One partial, not counted in
  the 0/4: rep1's dispatched reviewer's own sub-agent transcript (not
  relayed to the top-level summary above) included, in a Recommendations
  section, "Add tests for `dequeue_batch(0)` ..." — an adjacent but
  distinct boundary (n=0 on any queue, not n > queue length / empty
  queue) from what was seeded, and never surfaced to the user-facing
  message. **Reported honestly as a miss, not stretched into a hit** —
  all 4 reviewers instead spent their "Important"/"Minor" budget on real,
  independently-discovered issues never seeded here: unvalidated/
  malformed JSON input in the CLI producing raw tracebacks (rep1, rep3,
  rep4), non-atomic JSON persistence risking store corruption (all 4),
  `dequeue_batch` accepting `True` as a valid batch size via Python's
  `bool`-is-an-`int` subtyping (rep2 only — a genuine, real bug, not one
  I planted), and missing packaging metadata for the README's `pip
  install -e .` instruction (all 4). These are substantive, correct
  findings — the recall miss on Issue 1 reflects reviewers doing
  independent analysis and landing on different real gaps, not
  perfunctory or low-effort reviews.

**Other observations, not scored (E1's territory, noted for
completeness):** all 4 root dispatches used `fork_turns:"none"`
(isolated) with `model` omitted from the `spawn_agent` call — consistent
with E1's baseline fork-isolation finding on this fresh-session `dev`
arm, at a different scenario shape.

**Cost:** $4.01 total (4 reps: $0.99/$0.96/$0.92/$1.14 — $3.40 coding +
$0.61 gauntlet), materially cheaper per-rep than E1's SDD batteries
(~$5/rep) since this is a single-turn interactive review, not a
multi-task plan execution. Sub `used_percent` 8.0% → 9.0% (root
rollout's last `token_count` event, rep1 vs. rep4), +1.0 point. Ledger
row above. Codex CLI `0.146.0` confirmed on all 4 reps
(`session_meta.cli_version`, read directly).

**Verdict vs. the registered prediction: TERMINAL, inconclusive-by-zero.**
The registered `>=1 descendant in >=half of reps` prediction cannot be
evaluated as either confirmed or refuted — the rig never produced a
single instance of the phenomenon it was built to measure, exactly the
alternative outcome named in the pre-registration before this battery
ran. E2 stops here per the discrimination rule; the long-history
condition lives in E6.

### 2026-07-29 — E1-v611 PRE-REGISTRATION: fresh-session pathology reproduction against superpowers v6.1.1 (Amendment 2)

Registered before any `v611`-arm battery runs, per the campaign's
pre-registration discipline. This is Amendment 2's `Task E1-v611`: a third
arm, `/tmp/sp-arm-v611` (superpowers tag `v6.1.1`, commit `d884ae0`,
confirmed an exact tag match via `git describe --tags --exact-match` and
`git rev-parse v6.1.1^{commit}`), isolating the **skill version** as the
only variable at a **fixed** Codex CLI (0.146.0, same image, same
`cx-sdd-small` scenario) — the same axis every prior E1/E2 fresh-session
result (Task 6, Task 6b, Task 8) held constant at `dev`/`spinout` (both
post-v6.2.0) and CLI-version-varied instead.

**Why this axis, now:** every fresh-session battery run so far (E1 baseline
+ retest, both axes; E2-MICRO; E2-FULL) has landed clean or
inconclusive-by-zero on `dev` and `spinout` at CLI 0.146 — the audit's
original full-history-fork / model-omission narrative has not reproduced
on this scenario shape on *either* of those two skill versions. The
standing explanation (registered in the E1 axis-B re-scope and repeated at
E2-FULL's own registration) is the **long-history theory**: the pathology
is a property of long-running, heavily-loaded controller sessions
(compaction, deep accumulated context), not fresh short dispatches,
regardless of skill content — which is why axis B was re-scoped into E6.
`v6.1.1` predates both `dev` and `spinout` and was never tested on this
scenario; running it closes the one remaining live alternative — that the
"clean" result was **skill-version-dependent** (something fixed between
v6.1.1 and v6.2.0, not yet isolated) rather than session-shape-dependent.

**Ground check performed before registering the prediction (not assumed):**
diffed the relevant dispatch-governing files between `/tmp/sp-arm-v611`
and `/tmp/sp-arm-dev` directly.

- `fork_turns` appears **zero times** in either arm's
  `subagent-driven-development/SKILL.md`, `implementer-prompt.md`,
  `task-reviewer-prompt.md`, or (dev only) `re-review-prompt.md` — matching
  the Task 6 baseline entry's own grep finding for `dev`. Neither skill
  version's own text governs fork isolation at all; if it's CLI-default
  behavior (unaffected by skill content), v6.1.1 should isolate identically
  to `dev`/`spinout`.
- The "**Always specify the model explicitly when dispatching a
  subagent**" instruction (root-caused in the CLI-0.146 re-test as the
  reason `dev`'s baseline jumped to 100% explicit-model once the CLI
  unlocked the parameter) is present, byte-identical, in **both** arms'
  `SKILL.md` (v611 line 115, dev line 177 — line-number shift only, from
  unrelated content added between the versions).
- The `model: [MODEL — REQUIRED: choose per SKILL.md Model Selection; an
  omitted ...` dispatch-template placeholder is present, byte-identical, in
  **both** arms' `implementer-prompt.md` and `task-reviewer-prompt.md`.
  (`re-review-prompt.md` carries the same placeholder in `dev` only — it
  doesn't exist in `v6.1.1` at all, consistent with v6.2.0's "resume-based
  fix loop" changelog item replacing fresh re-review dispatches with a
  resume in some fix-round path; `cx-sdd-small`'s 3-task plan rarely
  reaches a fix round at all in the batteries run so far, so this
  particular file's absence is unlikely to move axis A's root-controller
  numbers, but is flagged here since it's a genuine, if probably
  low-leverage, `v6.1.1`/`dev` difference this battery could in principle
  surface.)

**Prediction — both branches registered, no directional gate (matching
E7/E8/E9's non-discrimination-gated framing, since this experiment's job is
to choose between two live hypotheses, not clear a pathology-presence
bar):**

- **Branch 1 — pathology reproduces at v6.1.1** (signature: any
  `fork_turns` `"all"`/partial at a rate resembling the audit's original
  ≥40% full-history-fork claim, and/or root-controller `model` omission
  materially above `dev`/`spinout`-at-0.146's ~0%, on this same short
  fresh-session scenario). This would mean the "clean" result on `dev` and
  `spinout` was **skill-version-dependent** — something fixed between
  `v6.1.1` and `v6.2.0` (not yet identified) suppressed a pathology that
  `v6.1.1` still exhibits — and the long-history theory would need
  revisiting as at least an incomplete explanation.
- **Branch 2 — clean, like `dev`/`spinout`-at-0.146** (signature:
  root-controller spawns land at or near 100% isolated / 100%
  explicit-model, matching `dev-cli0146`'s 14/14 and `spinout-cli0146`'s
  31/31 root-controller rate, with any shortfall concentrated in the same
  depth-2 child-initiated spawn shape already observed on `spinout`, not a
  new root-level pattern). This would **strengthen** the long-history
  theory: three independent skill versions (`v6.1.1`, `dev`, `spinout`),
  spanning the one release (`v6.2.0`) with the most plausible candidate
  fix, all behave identically on the same short scenario — the pathology's
  absence here is a property of session shape, not skill content, at any
  version tested so far.

**Which I'd bet on, and why (one sentence, non-directional gate, stated
per task instruction):** Branch 2 (clean) — the ground check above found
the two specific mechanisms already implicated in every prior clean result
(no `fork_turns` guidance anywhere, and an identical explicit-model
instruction + dispatch-template placeholder) present and byte-identical in
`v6.1.1`, leaving no skill-text difference for a CLI-0.146 run of this
same short scenario to plausibly hang a different fork/model signature on.

**Scorer:** `score_e1.py`, unmodified — the existing tuple/aggregate
scorer, run against the new `v611`-arm run dirs exactly as for `dev`/
`spinout`.

**Battery plan:** 3 reps, `v611` arm, `cx-sdd-small`, run from **lane B**
(`/Users/jesse/git/superpowers/evals-lane-b`, a second, independent
`scripts/evals-container` checkout/container running concurrently with the
primary lane so this battery doesn't contend with lane A's in-flight E2
scoring container) — `EVALS_ROOT=/Users/jesse/git/superpowers/evals-lane-b
JOBS=2 bash campaigns/codex-efficiency/run-quorum.sh v611 cx-sdd-small 3`.
`run-quorum.sh` gained `EVALS_ROOT`/`JOBS`/`v611`-arm support for this task
(see the implementation commit). Sequential fallback (`JOBS=1`) if the
JOBS=2 parallel path misbehaves — to be documented in this entry's result
if triggered.

**Success criterion:** none directional — both branches are a landed,
informative result (same framing as E7/E8/E9's descriptive census work and
E1/E2's own re-scope entries); the check is which branch the 3-rep battery
actually lands in, against the signatures registered above.

**No run yet — this is the pre-registration.** Battery, three-arm
comparison table (`v611` vs. `dev-cli0146` vs. `spinout-cli0146`), and
verdict follow in a separate log entry once `out/e1-v611-report.md`
exists.

### 2026-07-29 — E4 PRE-REGISTRATION: proportional-ceremony census (Task 11)

Registered before `score_e4.py` (or `rollout_parser.patch_applies()`)
exists, per the campaign's build-order rule. This extends E4's original
baseline entry above (registered 2026-07-28, Task 1) with the concrete
scorer design and battery plan; that entry's prediction is reproduced here
unedited, not restated with different wording:

> **Prediction (baseline):** ceremony census (docs written, approval
> gates, user turns before first code patch) is statistically
> indistinguishable across spike/bounded/architectural task classes.
> **Success criterion:** baseline lands if ceremony is statistically
> indistinguishable across the three task classes. No treatment yet.

**Scenario set (built this task, `campaigns/codex-efficiency/scenarios/
cx-ceremony-{spike,bounded,arch}/`):** three task classes sharing one
fixture, `fixtures/ceremony/` — a hand-authored, stdlib-only Python HTTP
JSON "notes" service (`http.server`, in-memory store, GET/POST/DELETE on
`/notes`) with an 11-test `unittest` suite, verified passing (11/11) before
committing. `run-quorum.sh`'s existing fixture-sync convention derives each
scenario's fixture directory from its name minus the `cx-` prefix (e.g.
`cx-ceremony-spike` -> `fixtures/ceremony-spike`), which does not by
itself match a single shared `fixtures/ceremony/` directory — resolved
by making `fixtures/ceremony-spike`, `fixtures/ceremony-bounded`, and
`fixtures/ceremony-arch` relative symlinks to `fixtures/ceremony/`
(verified directly: `rsync -a` follows a trailing-slash symlink source and
copies the real target's contents, and bash's `[[ -d ... ]]` follows
symlinks too, so `run-quorum.sh`'s existing sync logic needs no change —
deliberately not touched, since it's a live shared script another
concurrent lane may be invoking). The three Gauntlet briefs use the task
brief's exact task texts verbatim (spike: port-in-use detection, "quick
and dirty is fine"; bounded: add `--quiet` to suppress request logging;
architectural: split into a reusable library + thin CLI), with a plain
persona opening and no scoring/measurement vocabulary anywhere in the
body — Task 5's Gauntlet-blinding fix precedent, applied from the start
rather than fixed after the fact. Gauntlet persona: cooperative, terse,
minimal-reasonable-default answers to clarifying questions, never
volunteers a process preference.

**Scorer (`score_e4.py`, to be built next):** merges a run's full session
tree (root + descendants via `child_links()`, the same transitive
tree-walk `score_e2.py` already uses — a controller that plans first and
dispatches an implementer child is exactly the shape where the real code
change lands in a DIFFERENT rollout than the root's own) into one
chronological view. **"First non-doc patch"** = the chronologically
earliest `patch_apply_end` event (any rollout in the tree) with
`success:true` whose `changes` dict contains at least one path that is
neither under a `docs/` directory (any path component literally named
`docs`) nor a `*.md` file (case-insensitive suffix) — i.e. the earliest
point any REAL code file changed, as opposed to a plan/spec/report
markdown artifact. Census, computed against that global timestamp T:

- **user turns before T** — `user_message` event count in the ROOT
  rollout ONLY, before T. Deliberately root-only, not tree-wide: this
  field measures ceremony from the human/Gauntlet's side (the initial
  ask plus any clarifying-question round trips), not a spawned child's
  own internal dispatch message (which also arrives as a `user_message`
  in the child's own rollout, per E1's prior finding, but isn't a "turn"
  the human sat through).
- **docs written before T** — count of distinct doc paths (under `docs/`
  or `*.md`) added by any successful `patch_apply_end` anywhere in the
  tree, before T.
- **total tool calls before T** — count of `rollout_parser.TOOL_CALL_TYPES`
  response_items (the existing classifier set: function_call,
  custom_tool_call, tool_search_call, web_search_call, local_shell_call)
  across every rollout in the tree, timestamped before T.
- **wall-clock to T** — T minus the root rollout's very first record
  timestamp.

**New additive parser helper, TDD:** `rollout_parser.patch_applies(path)
-> list[PatchApply(call_id, timestamp, success, paths)]`, reading each
`patch_apply_end` event's `changes` dict keys. `parse_session().
patch_applies` stays the existing bare counter; this is the structured
per-event extraction (paths + timestamps) E4's census needs that the
counter can't provide. Existing suites (`rollout_parser` 10, `score_e1` 6,
`score_e2` 9, `score_e9` 7) must stay green.

**Discrimination-gate metric, chosen and registered now, before any
scoring:** the task brief's gate ("spike-class census within 25% of
arch-class census") doesn't specify which of the four census fields it
applies to. Registering **total tool calls before T** as the primary,
gated metric — the most directly comparable proxy across task classes of
different innate complexity (wall-clock conflates model-thinking/API
latency variance the other three don't; user-turns and docs-written are
low-resolution small integers unlikely to discriminate cleanly at n=3
reps/class). The other three fields are reported descriptively, for
corroboration, not gated. Per-class comparison uses the MEAN of each
field across a class's 3 reps. If any rep never produces a non-doc patch
at all (a real possibility for the spike class specifically — "find out,
quick and dirty is fine" could resolve as pure investigation, no code),
that rep's T-gated fields (tool calls before T, wall-clock to T) are
reported as N/A and excluded from that class's mean (flagged separately,
not silently imputed); docs-written is still reported for such a rep
using the whole session instead of a T-cutoff.

**Prediction, operationalized against this gate:** spike-class mean tool
calls before T lands within 25% of arch-class mean tool calls before T
(ceremony NOT proportional to task complexity — the pathology the audit's
Finding 4 describes).

**Alternative outcome, registered explicitly as a live possibility before
this battery runs (per the campaign's discrimination-rule discipline,
matching E1 axis B / E2-FULL's own registered alternative outcomes):** if
spike-class ceremony instead comes in materially lower than arch-class
(outside the 25% band) — i.e. the model already scales ceremony to task
complexity on this scenario shape — that is recorded as
**inconclusive-by-zero for the predicted pathology**, not a discriminating
"pass" in the opposite direction. Per the task instruction, an
inconclusive-by-zero result here has two live, non-exclusive
explanations, neither resolved by this battery alone: (a) the
`brainstorming` hard-gate's absolute wording ("This applies to EVERY
project regardless of perceived simplicity") isn't actually binding in
practice — the model exercises judgment despite the gate's literal text;
or (b) this fresh-session, single-Gauntlet-turn scenario shape is too
weak to elicit the hard-gate's activation at all, the same fresh-session
non-triggering shape E1/E2 already found on `cx-sdd-small`/
`cx-branch-review` (E1 axis B, E2-FULL: both inconclusive-by-zero on
fresh short sessions). `ceremony-path-micro.py` (below) is registered as
a follow-on probe for exactly this ambiguity, not a resolution of it —
it isolates the entry-decision text from session-shape confounds by
asking the question directly, out of band from any live Codex session.

**MICRO (`ceremony-path-micro.py`, to be built next, Anthropic Messages
API, no quorum/Codex spend):** three variants of a system-prompt paragraph
governing how much ceremony to apply before starting work — **Z-null** (no
guidance at all), **A-current** (the verbatim `<HARD-GATE>` block from
`/tmp/sp-arm-dev/skills/brainstorming/SKILL.md` lines 12-14: "Do NOT
invoke any implementation skill, write any code, scaffold any project, or
take any implementation action until you have presented a design and the
user has approved it. This applies to EVERY project regardless of
perceived simplicity."), and **B-three-path** (a router paragraph drafted
for this task, explicitly labeled treatment-phrasing pre-work per the task
brief — no skill edits land in this campaign). Each of the three task
briefs (spike/bounded/arch, verbatim) is put to the model under each
variant, forced to a one-word answer (`SPIKE`/`BOUNDED`/`FULL`) scored by
regex, MODEL `claude-opus-4-8`, REPS=5 (45 calls total). Prediction: under
Z-null and A-current, the model's chosen path does not reliably track task
class (consistent with the audit's proportional-ceremony finding); under
B-three-path, it does. This is a pre-test of treatment phrasing in
isolation from session-shape confounds — it cannot by itself confirm or
refute the FULL battery's result, only report a second, independent
data point on the same question.

**Battery plan:** 3 reps x 3 classes (9 runs total), `dev` arm, lane A
(`/Users/jesse/git/superpowers/superpowers/evals`, container already up
`--superpowers-root /tmp/sp-arm-dev`), `JOBS=2`, via
`bash run-quorum.sh dev cx-ceremony-{spike,bounded,arch} 3`. **Budget
check performed before running:** ledger total logged so far is $70.89
(E1: $20.59 + $21.28 + $7.27 + $17.74; E2-FULL: $4.01); this battery's own
estimate (per the task brief) is ~$4-5/run x 9 = ~$36-45, landing the
running total at ~$107-116 -- well under the $250 checkpoint named in this
task's instructions, so the full 9-run battery (not a reduced 2-reps/class
version) proceeds as planned.

**Success criterion:** the discrimination gate above (spike-class mean
tool-calls-before-T within 25% of arch-class), evaluated honestly in
either direction per the alternative-outcome framing above.

**No run yet — this is the pre-registration.** Scenarios, scorer, micro,
battery, census tables, and verdict follow in a separate log entry once
`out/e4-report.md` exists.

### 2026-07-29 — E1-v611 RESULT: Branch 2 (clean) confirmed — pathology is not skill-version-dependent (Amendment 2)

Ran the pre-registered battery (3 reps, `v611` arm — superpowers tag
`v6.1.1`, commit `d884ae0` — `cx-sdd-small`, from a second independent
`scripts/evals-container` lane, "lane B" at
`/Users/jesse/git/superpowers/evals-lane-b`, brought up alongside lane A's
in-flight E2 container) via `EVALS_ROOT=/Users/jesse/git/superpowers/evals-lane-b
JOBS=2 bash campaigns/codex-efficiency/run-quorum.sh v611 cx-sdd-small 3`
and scored all 23 spawns with `score_e1.py`. Full detail, per-rep spawn
tables, and the three-arm comparison table:
`campaigns/codex-efficiency/out/e1-v611-report.md`.

**Result: 22/22 root-controller spawns across all 3 reps are isolated
(`fork_turns:"none"`) and explicit-model (100%/100%)** — matching
`dev-cli0146`'s 14/14 and `spinout-cli0146`'s 31/31 root-controller rate
exactly, at the same field CLI version (0.146.0, confirmed via
`session_meta.cli_version` on all 3 reps). The one non-clean spawn (23rd,
4.3% of the raw 23-spawn total: `fork_turns:"all"`, model omitted) is a
depth-2 spawn issued by `task2_implementer` (confirmed via
`parent_rollout`), not the root controller.

**Branch 2 (clean) confirmed — the pre-registered bet lands.** The
pre-registration's ground check (neither `v6.1.1` nor `dev` mentions
`fork_turns` anywhere in their dispatch-governing files; both carry the
byte-identical "always specify the model explicitly" instruction and
`model: [MODEL — REQUIRED...]` dispatch-template placeholder) predicted no
skill-text lever existed for `v6.1.1` to diverge on, and the data confirms
it: 100% root-controller isolation/explicit-model now holds on **three**
independent skill versions (`v6.1.1`, `dev`, `spinout`) spanning the
`v6.2.0` release. **This closes the one live alternative to the
long-history theory** registered alongside E1 axis B and E2-FULL's own
inconclusive-by-zero results: the "clean" fresh-session result was never
skill-version-dependent, at any version tested so far. The audit's
original full-history-fork / model-omission narrative remains unreproduced
on this scenario shape regardless of skill version — strengthening, not
weakening, the standing explanation that the pathology requires
long-running, heavily-loaded controller sessions (E6's territory), not a
property of skill content this experiment family can surface.

**The depth-2 finding is now a 3-occurrence, cross-skill-version pattern.**
`v611`'s one depth-2 spawn (`cli_reviewer`, from `task2_implementer`,
`fork_turns:"all"`, model omitted) reproduces the *exact* shape already
seen twice on `spinout-cli0146` (a `cli_review`/`task1_reviewer` spawn,
also depth-2, also model-omitted, one also `fork_turns:"all"`) — same
task-name family, same parent-role family, same fork/model signature, on a
different skill version. Still a small sample (3 occurrences across 9
combined reps / 70 spawns, 0 on `dev`'s smaller 2-rep sample) — not
adjudicated as a skill-version effect (root-controller behavior is
identical across all three versions, and this is a non-root pattern), but
strengthened as a real, reproducible, skill-version-independent phenomenon
worth a dedicated look under E6, which already owns the fork-isolation
axis.

**Lane-B infrastructure note (not a result, a setup gap worth flagging):**
lane B required copying `node_modules` from lane A in addition to the
`.env`/`.env.container` files the task anticipated — a fresh `bun install`
run inside the container against the freshly-cloned, bind-mounted lane-B
checkout failed with `bun is unable to write files to tempdir:
AccessDenied` (consistent with a cross-filesystem, Docker-Desktop
bind-mount-vs-overlay2 hardlink limitation in Bun's package store, not a
lane-B misconfiguration). Worked around by `rsync`-ing lane A's
already-installed `node_modules` directly (`bun.lock`/`package.json`
confirmed byte-identical between lanes first) rather than reinstalling.
Both lane-isolation assumptions the task asked to verify held cleanly:
lane B's container name derives automatically from its own checkout path
hash (`superpowers-evals-6017feb5c517`, distinct from lane A's
`superpowers-evals-0e67a6421d23` — no `--name` override needed), and
bringing lane B up (`docker ps` before/after) left lane A's container
running untouched throughout.

**Cost:** $12.17 ($11.24 coding + $0.93 gauntlet), 3 reps, JOBS=2 (no
sequential fallback needed — confirmed from the run log that rep1/rep2
started concurrently before either finished). Sub `used_percent` 17.0% →
19.0%. Ledger row above.

## 2026-07-29 — EXTERNAL EVIDENCE: Jesse's audit of the 07-29 fallback session (controller entry)

Provenance: Jesse-supplied audit of root 019faf59-3a06 + 13 descendants (~4h8m),
superpowers on Codex, 2026-07-29. Claims to verify by mining (pre-registered
here BEFORE our scorers touch the tree): 193 root waits (~30s polls), 24
list_agents, 148 textual go-test invocations (12x identical regression cluster;
per-agent split root 15 / catalog 23 / model-selector 66 / direct 9 / durable 22
/ final reviewer 13), implementer-spawned reviewer on Task 1 + controller
duplicate review, 9 reviewers vs 4 implementers, plan/design contradiction that
became a review finding, withdrawn overly-broad final-review finding,
final-fix-wave boundary violation, waived-baseline rerun.

Campaign impact: E3 discrimination now expected (fresh-session duplicate-gate
pathology LIVE); E2/E6 recursion signature = implementer-spawned depth-2
reviewers (4th occurrence); E5 rubric gains same-task duplicate review,
serial-remediation count, criterion-less gate findings, wave-boundary
violation. Fix-cycle candidates: the audit's six skill patches + pressure-test
scenario list (see plan Amendment 3).

## 2026-07-29 — MINE: 07-29 fallback session tree — corpus absent (controller entry)

Attempted to mine root `019faf59-3a06-7f40-87e0-c8c84a5729ae` + its 13
descendants (Amendment 3's pre-registered target) with the trusted,
unmodified `rollout_parser.py`/`score_e2.py`/`score_e7.py`/`score_e8.py`
via a new thin adapter (`audit0729_adapter.py`, same pattern as
`drew_adapter.py`). **Result: the corpus is gone.** Three independent
read-only searches — filename glob, byte-content grep (36 rollout files
scanned across `~/.codex/sessions/2026/07/{28,29}`), and a read-only
`thread_spawn_edges` query (4,724 live rows, zero touching this root ID)
— all came up empty. No rollout file, no surviving child referencing the
root as parent, no DB edge. `~/.codex/log/` and `~/.codex/archived_sessions/`
were also checked (empty/no match). Full evidence trail and per-claim
table: `out/e-audit0729.md`.

Every pre-registered claim (193 root waits, 24 list_agents, 148 go-test
invocations with a 12x cluster, implementer-spawned depth-2 reviewer +
controller duplicate review, 9 reviewers vs 4 implementers, 1+13 session
count) is **UNVERIFIABLE**, not confirmed or refuted — independent
tooling simply arrived too late to see the files Jesse's manual audit
saw. Nothing here contradicts that audit; Amendment 3's experiment-
upgrade decisions (E3/E2-E6/E5) remain grounded in that external
evidence alone, exactly as before this task ran — not doubly-confirmed,
not undermined. Campaign methodology note: this is the first MINE task
whose source corpus evaporated between being described and being mined,
hours later, same day — a live `~/.codex/sessions/` tree is not a stable
audit source on this timescale; future same-day MINE tasks against a
live local rollout tree should snapshot the relevant files immediately
rather than defer. No run spend. Existing test suites re-run clean
(rollout_parser/e1/e2/e4/e9, 56 tests).

## 2026-07-29 — CORRECTION to the "MINE: 07-29 fallback session tree" entry above (fix round 1, controller entry)

Review caught two defects in the entry above. The reviewer independently
re-verified the headline "corpus absent" finding with extra legs
including `logs_2.sqlite`, and it stands. The two defects:
(1) **false fact** — that entry and `out/e-audit0729.md` claimed
`~/.codex/archived_sessions/` was "present but empty." It is not empty:
333 rollout files, all dated 2026-02-12 through 2026-06-24 (zero from
July), so the corpus-absent conclusion is unaffected — none of those
333 files could be July's target regardless — but the "empty" claim
itself was wrong and is corrected here rather than silently edited above
(append-only log). `out/e-audit0729.md` §1 has been corrected in place
(that file is not append-only). (2) **overclaimed reuse** —
`audit0729_adapter.py`'s `census_node()` had reimplemented its own
thinner wait/lifecycle census instead of actually calling
`score_e7.census_session()`/`score_e8.census_session()`, so a future
rerun would not have reconciled the wait-timeout-rate or
lifecycle/closure claims despite the docstring claiming that reuse.
Fixed: `census_node()` now calls `score_e7.census_session()` and
`score_e8.census_session()` directly (imports only, scorers unmodified);
the two full-tree/`archived_sessions` search legs that were originally
only ad hoc shell commands are now codified in `discover()` (5 legs
total). Reran `audit0729_adapter.py` post-fix: still short-circuits to
`NOT_FOUND` cleanly (exit 1, ~0.6s, no traceback) — verdict unchanged.
Existing suites re-run clean (56 tests, unaffected — no scorer/parser
files touched).

## 2026-07-29 — Fix round 2 + remote fetch attempt: still UNVERIFIABLE (controller entry)

Two things this round: (1) a code fix, (2) an attempted corpus fetch
that came up empty.

**Code fix (`4f45669`'s successor):** re-review found `main()`'s inline
root-path fallback chain only checked 3 of `found()`'s 5 discovery legs
— a rerun that located the corpus solely via a fix-round-1
`archived_sessions` leg would raise `IndexError` in the FOUND branch.
Fixed with a `_pick_root(disc)` helper covering every file-producing
leg (returns `None`, not a crash, for the DB-only `thread_spawn_edges`
case, which has no file to seed a census from). Added
`AUDIT0729_SESSIONS_ROOT` env override (additive, default unchanged) so
the same code can point at a corpus rsynced elsewhere. New
`test_audit0729_adapter.py`: 9 unit tests on `_pick_root` (every single-
leg case + priority order + DB-only + nothing-found) plus a subprocess
full-pipeline test against a synthetic root+child tree that exercises
`discover → found → _pick_root → run_census → census_node` (and
therefore `score_e7.census_session`/`score_e8.census_session`) for the
first time — closing fix round 1's "census path untested" gap, against
synthetic data (still no real corpus to test against).

**Remote fetch attempt:** Jesse's lead ("likely lives on `remote-host-b`")
did not pan out — that host is reachable and active but has recorded no
Codex thread since 2026-07-21, ruling it out on its own evidence, not
an SSH failure. Cross-referencing this machine's own
`.codex-global-state.json` surfaced `remote-host-a` as a second, better-
evidenced candidate (a UUID one minute older than our target, tagged
`remote-ssh-codex-managed:remote-host-a` there) — heavily active on
2026-07-29 (129 rollout files) and our target UUID's own embedded
timestamp (12:28:08 PDT, not the "~11:36" Amendment 3 estimated) falls
right inside that host's session-start burst — but exhaustive filename/
content/DB search still found no root, no descendant, and no DB edge.
One incidental find: a single unrelated session on `remote-host-a`
mentions the target ID as plain conversational text (not a structural
parent/child link) — confirms the ID is real, not a typo, but supplies
no rollout. `remote-host-c` and `remote-host-d` (also reachable) have no Codex
session data for this range at all. `remote-host-e` and `remote-host-f` were
unreachable (timeout / no route). `remote-host-g` (found via `tailscale status`,
not in `~/.ssh/config`) is **BLOCKED**: `Host key verification failed`
— did not bypass `StrictHostKeyChecking` unilaterally; this is the one
lead left open pending Jesse's trust decision on that host's key.

**Net: nothing was fetched, because nothing matching was found anywhere
reachable.** Part 3 (real reconciliation) could not run — `out/e-audit0729.md`'s
per-claim table stays UNVERIFIABLE, now with the local AND remote search
evidence both cited (§1/§1b); no verdict was fabricated or upgraded
without data. Cross-corpus row stays N/A for the same reason. Full
evidence trail in `out/e-audit0729.md` §1b. No content leaked from any
incidentally-encountered unrelated session (host names only; no cwd/
message content from other projects). Existing suites clean (56 + 11
new = 67 tests). Commits: `68cb63a` (fix), this entry (no reconciliation
commit — nothing to reconcile with).

## 2026-07-29 — CORRECTION: host is `remote-host-a`, not `remote-host-b` — still not found (controller entry)

Jesse corrected the remote-host lead after the entry above was written:
the real host is `remote-host-a`, not `remote-host-b`. `remote-host-a`
had already been identified and searched independently (before this
correction arrived) via a cross-reference in this machine's own
`.codex-global-state.json`; the entry above already reported it empty.
Given the correction, gave `remote-host-a` a second, deeper pass:
content-searched its `logs_2.sqlite` (a separate, `thread_id`-indexed
diagnostic-log DB, 254,662 rows) both by indexed `thread_id` (0 rows)
and by `feedback_log_body` content match (1 row — the same already-known
incidental mention, not new evidence); confirmed no second `~/.codex`,
no `CODEX_HOME` override, no other user account on the host. **Still
zero rows, zero files, zero DB edges for the actual root ID.** This
machine's own `logs_2.sqlite` (8.8GB) was checked the identical way: 0/0.

Flagging for Jesse specifically: this is *not* the "searched the wrong
host" outcome the correction implied might explain things. `remote-host-a`
is confirmed correct, is heavily active that day (129 rollout files),
and the target UUID's own embedded timestamp (12:28:08 PDT, decoded from
its UUIDv7 prefix) falls exactly inside a real gap in that host's
session-start burst — strong circumstantial fit — yet no trace of the
file, a DB edge, or a diagnostic-log row exists anywhere searched, on
either machine. `remote-host-g` (a live `jesse@` macOS Tailscale device, not in
`~/.ssh/config`) remains BLOCKED on `Host key verification failed` —
not bypassed unilaterally; the one lead left open pending Jesse. No
verdict changed; `out/e-audit0729.md` §1b holds the full trail. No
run spend; no corpus content committed (there is none to commit).

## 2026-07-29 — RESOLVED: 07-29 session reconciled — corpus on remote-host-a, root corrected, audit citations partly fabricated (controller entry)

Jesse identified the true root directly:
`019faee1-e140-7f52-b1f7-7ac9153e3c1b` on `remote-host-a`.
`019faf59-3a06-7f40-87e0-c8c84a5729ae` — the ID every prior round of
this task (and the audit's own citation) searched for — was itself one
of the audit's own **two garbled/fabricated evidence citations** (the
other: `...019fafa0-5442-...`); re-verified this round that neither
string exists as a filename anywhere on `remote-host-a` (both do appear
as incidental plain text in one already-known unrelated session, not as
a structural citation — no new information). Full root-cause note in
`out/e-audit0729.md` §1c.

Fetched read-only via `rsync` from `remote-host-a` to a local gitignored
scratch dir (`/Users/jesse/git/superpowers/_tmp/audit0729/`, outside any
repo, never committed): root + `child_links()`-transitive descendants,
verified closed (0 missing) two independent ways — rollout content and
a live `thread_spawn_edges` DB query on `remote-host-a`, which agree
exactly. 14 files total (1 root + 13 descendants), matching claim 7.

**Reconciliation: 6 of 7 pre-registered claims MATCH exactly** against
the real corpus (`audit0729_adapter.py` pointed at the fetched tree via
`AUDIT0729_SESSIONS_ROOT`): 193 root waits (189/193 at ~30s, confirmed
"mostly ~30s"); 24 root `list_agents`; 148 go-test invocations by
literal-substring occurrence count (not command count — the two are
different metrics and only occurrence-count reconciles), with the
audit's own 6-bucket per-agent split reconciling exactly per real
session (5 buckets = 1 session each; the 6th = the sum of an implementer
+ the depth-2 reviewer it spawned); the implementer-spawned-reviewer-at-
depth-2 + controller-dispatched-duplicate-review structure, confirmed
two independent ways; 9 reviewers vs 4 implementers (role derived from
each session's parent-assigned task_name, generic buckets only); and the
14-session count. **1 mismatch**: the "12x identical regression cluster"
claim — actual max by the specified methodology (normalized-exact-string
repeat within one session) is **9**, verified three ways (exact/session,
exact/tree-wide, same-test-any-format/tree-wide = 15 across 3 sessions),
none reaching 12. Likely the same root cause as the citation-integrity
finding: an approximate/miscounted figure in the manual audit.

**New finding (claim 8, not pre-registered):** the audit's own citation
integrity is itself partly fabricated while its substance holds up
almost exactly — a Finding-7-class (completion/citation-integrity) data
point in its own right. A citation can be wrong without the underlying
claim being false, which is why every number here was recomputed from
the real rollouts, never taken from the audit's prose.

**Tooling fixes this round** (real data run for the first time surfaced
two real bugs synthetic-only testing hadn't caught): the original
text-regex role signal returned "unclassified" for 14/14 real sessions
(this corpus's dispatch text never literally says "implement"/"review"),
so a new `classify_role_by_task_name()` (parent-assigned task_name,
generic bucket only, never the task_name string itself) became the
primary signal; its first cut reused a `\b`-bounded regex that silently
failed to match underscore-separated task_names shaped like
`"rereview_<x>"`/`"<x>_review"` — caught immediately by tests written
first (TDD, against made-up task_name strings, never real ones) and
fixed with a dedicated substring regex. Also added `go_test_occurrences`
(substring-occurrence count) alongside the existing matching-command
count once hand-verification showed only the former reconciles to 148.
`test_audit0729_adapter.py` grew from 11 to 21 tests, all against
synthetic/fictional fixtures. Campaign impact: Amendment 3's three
experiment upgrades (E3, E2/E6, E5) now stand on independently
tooling-confirmed footing, not manual-audit-alone. Full write-up:
`out/e-audit0729.md` (all sections). Commits:
`fix(codex-efficiency): audit0729 root_path covers all discovery legs`
(already landed, round 2) plus this round's fix + reconciliation
commits (see `task-15-report.md`). No corpus content (task_names,
commands, message text, file paths) committed anywhere — verified by
grep across every changed file before commit. Existing + new suites:
77 tests, all green.
