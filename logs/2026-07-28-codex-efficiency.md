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
