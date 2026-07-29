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
