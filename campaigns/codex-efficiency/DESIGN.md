# Campaign: Codex efficiency evals

**Spec:** `docs/2026-07-28-codex-efficiency-eval-campaign-design.md` — the
approved design (six experiments, tier ladder, ordering, budget, risks). This
file is the campaign's working home; the spec is the source of truth for
scope decisions. Read the spec for anything not reproduced below.

**Source audit:** `superpowers/docs/superpowers/research/2026-07-28-codex-efficiency-audit.md`

**Budget:** $1000 total, tracked in `logs/2026-07-28-codex-efficiency.md`.

## Experiment packages

The campaign ran **ten** experiments, not six. E1-E6 below are the spec's
original packages, copied verbatim. E7-E10 were added mid-campaign by
Jesse-approved amendment and are specified in "Amendments (E7-E10 and
scope changes)" further down — read that section too before treating this
file's E1-E6 list as the campaign's scope.

### The spec's original six

Copied verbatim from the spec (`docs/2026-07-28-codex-efficiency-eval-campaign-design.md`,
"The six experiment packages"). Each package: pathology signature → scorer
metrics → distilled scenario → tier plan → pre-registered success criterion
(from the audit).

### E1. Codex fork hygiene (Finding 1, P0)

- **Scorer:** per-spawn tuple — `fork_turns` value, explicit-model presence,
  instruction-line offset, child rollout bytes, child skill re-reads.
- **Corpus ground truth:** 1,098 recorded spawns; 52.3% full / 13.4% partial
  / 32.7% isolated; 925 omitted models.
- **Scenario:** small SDD plan (3–4 tasks) run by a Codex controller.
- **Tiers:** MINE → FULL baseline on `dev` → FULL treatment on
  `codex-spinout-fixes`.
- **Success:** 100% isolated spawns, 100% explicit models, no loss of task
  completion.

### E2. Reviewer recursion (Finding 2, P0)

- **Scorer:** subtree census per dispatched reviewer — descendants, max
  depth, thread-limit failures, sessions missing `task_complete`, wait-call
  volume.
- **Corpus ground truth:** 129-session Remux review tree (depth 12);
  31-session Serf tree.
- **Scenario:** one branch review dispatched over a prepared
  moderately-complex branch.
- **Tiers:** MINE → MICRO (non-delegation-contract phrasing sweep, reusing
  the reviewer-directive-micro pattern) → FULL baseline.
- **Success:** zero reviewer descendants in the default case; findings
  quality preserved.

### E3. Evidence receipts / duplicate gates (Finding 3, P1)

- **Scorer:** identical-command-at-identical-tree-state detection across a
  workflow's sessions (implementer → task review → finishing).
- **Corpus ground truth:** Remux 903-unit gate run twice at `51f0f7e`; July
  14 six RED-suite reps.
- **Scenario:** SDD plan carried through finishing-a-development-branch with
  no intervening commits; count duplicate full-suite runs. Paired probe:
  mutate the tree mid-flow and assert the gate reruns (invalidation
  correctness).
- **Tiers:** MINE → FULL baseline. No treatment yet.

### E4. Proportional workflow ceremony (Finding 4, P1)

- **Scorer:** ceremony census before first code — design docs written,
  approval gates, questions asked, tool calls.
- **Corpus ground truth:** Arq cleanup helper and Remux palette follow-up
  sessions.
- **Scenario set:** three task classes — feasibility spike, bounded change in
  an existing flow, architectural change. Baseline expectation: identical
  ceremony for all three.
- **Tiers:** MINE → MICRO (path-choice classification under variant
  entry-decision guidance) → FULL baseline for ceremony counts. No treatment
  yet.

### E5. Review scope and accretion (Finding 6, P1)

- **Scorer:** seeded-defect recall by intended scope + scope-accretion
  (post-completion commits/lines attributable to review findings;
  unadjudicated new scope).
- **Corpus ground truth:** Serf project 2 (+75 commits post-completion);
  Scantastic A/B waves.
- **Scenario:** plan with four planted defects — local bug, cross-task race,
  dependency/clean-checkout break, repair-induced regression — each
  catchable only by its intended scope.
- **Tiers:** MINE → FULL baseline. Most expensive; runs last.

### E6. Context diet / compaction recovery (Finding 8, P2 but cheap to score)

- **Scorer:** post-compaction skill re-read count, bootstrap/routing
  retention (do isolated-fork rules survive compaction?), controller input
  growth.
- **Corpus ground truth:** 19,317 corpus compactions; nine direct tasks with
  111 SKILL.md reads; one root re-reading brainstorming 4× in 8 minutes.
- **Scenario:** long controller session with induced compaction, then a
  post-compaction dispatch.
- **Tiers:** MINE → FULL. The compaction hook rides along with E1's
  `codex-spinout-fixes` runs (same branch); `exp/controller-diet` is graded
  in the later fix cycle.
- **Infra risk:** deterministically forcing compaction in drill is the one
  rig unknown.

## Amendments (E7-E10 and scope changes)

Three amendments were approved mid-campaign, each grounded in evidence
that arrived after the spec was written. Full text and rationale:
`docs/plans/2026-07-28-codex-efficiency-evals.md`, "Amendment 1/2/3";
every pre-registration and verdict is in
`logs/2026-07-28-codex-efficiency.md`. Campaign closeout, with all ten
verdicts in one table: `reports/2026-07-codex-efficiency-campaign.md`.

**Amendment 1 (post-Task-6):** container Codex CLI upgraded 0.144.4 →
field 0.146 and E1's axis A re-tested (the pinned container version was a
confound for E1's baseline); Drew-corpus cross-validation ingested as
external evidence; and three new MINE-tier scorers over already-paid-for
corpora — no new run spend:

### E7. Wait-polling waste (audit Finding 7, MINE only)

- **Scorer:** `score_e7.py` + `rollout_parser.wait_outcomes()` — pairs every
  `wait_agent` call to its `function_call_output` by `call_id`, classifies
  `timed_out`, reports poll counts, timeout rate, inter-poll cadence, and a
  cache-read rebill estimate. Writes `out/e7-{drew,audit-high-wait-root,
  audit-direct-sol,battery}.json` (FORCE=1 to overwrite; all-or-nothing).
- **Corpora:** Drew's (external), the audit corpus, our own batteries.
- **Report:** `out/e7-report.md`.

### E8. close_agent lifecycle hygiene (audit Finding 7, MINE only)

- **Scorer:** `score_e8.py` + `rollout_parser.lifecycle_calls()` —
  per-controller spawned-vs-closed census, plus interrupt/followup/resume/
  list_agents counts. **Privacy constraint discovered while building it:**
  a `close_agent` output can carry an entire child's final report, so the
  parser never reads `function_call_output` for these tools.
- **Report:** `out/e8-report.md`.

### E9. Workspace leaks (MINE only)

- **Scorer:** `score_e9.py` — reads **git history of run workdirs**, not
  rollout JSONL (the only scorer that does): was any `.superpowers/` path
  ever added, is it in HEAD, was it added on a HEAD-reachable commit; plus
  a review-package (`review*.diff`) surface added in fix round 1.
- **Report:** `out/e9-report.md`.

**Amendment 2:** the E1-v611 third arm (`v6.1.1` at fixed CLI 0.146, to
separate skill-version dependence from CLI-version dependence —
`out/e1-v611-report.md`), plus:

### E10. Lifecycle truthfulness (audit Finding 7's P0 gap)

- **Probes:** (a) empty-output child (`cx-sdd-small-emptychild`), (b) child
  killed from outside the container (`probe-kill-child.sh --live`), (c)
  tool/time-budget exhaustion (`cx-sdd-small-shortbudget`), (d)
  citation-integrity census over our own corpus (`score_e10.py`).
- **Scorer:** `score_e10.py` (+ `rollout_parser` claim primitives). Writes
  `out/e10-battery.json`.
- **Where the verdict lives — deliberate convention break:** E10 has **no
  `out/e10-report.md`**. Its verdict is the hypothesis-log "E10 RESULT"
  entry plus `out/e10-battery.json`, because probes (b) and (c) are
  single-instance driver-script case studies whose evidence is quoted
  transcript, not a census table — a report file would have been a copy of
  the log entry. Every other experiment has an `out/e*-report.md`; this one
  is the exception, and the closeout report carries its verdict in the
  same table as the other nine.

**Amendment 3 (Jesse-supplied 2026-07-29 session audit):** a real
fresh-session tree (root + 13 descendants, ~4h) independently replicated
several campaign findings and sharpened three experiments — E3 gained
identical-command-repeat and waiver-violation measures, E6 gained
depth-2-spawn-by-role and same-task-duplicate-review measures, E5 gained
four rubric measures. Reconciled BEFORE being trusted (6/7 claims exact,
2 of the audit's own evidence citations fabricated):
`out/e-audit0729.md`, `audit0729_adapter.py`.

**Terminology note carried by the amendments.** "Depth-2 spawns by role"
means SPAWNER role in `score_e6.py`/`out/e6-report.md` and CHILD role in
`out/e-audit0729.md`'s cross-corpus table; "duplicate review" means
same-**task**-worker-depth-2 in E6 and same-**scope** in E5. Both pairs
are defined at their point of use in those files. Don't compare the
numbers across reports without checking which sense is meant.

## Recon facts

Facts gathered before scoring work starts, recorded here so every scorer
built on top of them doesn't have to rediscover them:

- **Rollout line shape:** `timestamp` / `type` / `payload`.
- **Spawn args** are a JSON string with unstable key order and `"(omitted)"`
  markers.
- **Child linkage:** via `sub_agent_activity.event_id == spawn call_id`.
- **Compaction** emits a `compacted` record plus an
  `event_msg/context_compacted` marker pair.
- **Skill reads are textual heuristics** over exec input — audit regex:
  `/SKILL\.md|skills\.read|activate_skill/i`, false-positives on
  `apply_patch`.
- **Quorum invocation forms and `--scenarios-root`.**
- **`codex exec` micro pattern** from `harnesses/codex-read-delivery-micro.py`.

## External corpus: Drew head-to-head

**Path (read-only, external to this repo):**
`/Users/jesse/git/superpowers/_tmp/drew-sdd-head-to-head-2026-07-27/sdd-testing-fresh/`
— Drew Ritter's SDD head-to-head package (fractals codex-5_5/sol-5_6/
opus-4_8/opus-5 runs + the stress-2703 stress specimen), all Codex runs on
superpowers `codex-spinout-fixes @ bd68a949`, Codex Desktop CLI 0.146.
Read `HANDOFF.md` there first for layout.

**Never-commit rule:** this corpus is READ-ONLY. No file from it is ever
copied into this repo, and no content from it — session text, task
names from the stress-2703 stress run (a real, private client session),
message bodies — is ever committed here beyond aggregate numbers derived
from it. `campaigns/codex-efficiency/drew_adapter.py` reads it in place
and prints aggregates only; it never writes corpus content anywhere.
Fractals task_names (e.g. `task1_implementer`) are low-sensitivity SDD
taxonomy labels and are fine to cite; stress-run task_names are not
(private plan) and must not appear in any committed file.

**Provenance and findings:** `campaigns/codex-efficiency/out/
drew-cross-validation.md` (reconciliation against Drew's script-emitted
metrics, schema findings, what this corpus adds as treatment-arm
evidence); registered as external evidence in
`logs/2026-07-28-codex-efficiency.md`.

## E6 compaction forcing (Task 9 Step 1)

**Chosen mechanism: the `model_auto_compact_token_limit` config knob
(preferred, deterministic) — not the padding-file fallback.**

Source recon against `~/git/agent-harnesses/codex` (codex-rs, read-only):
`core/src/config/mod.rs` declares `model_context_window: Option<i64>` and
`model_auto_compact_token_limit: Option<i64>` as top-level `Config` fields
(`config.schema.json` confirms both are root-level TOML keys, not nested
under a table). `core/src/session/context_window.rs::context_window_token_status()`
forces compaction (`token_limit_reached = true`) once
`auto_compact_scope_tokens >= model_auto_compact_token_limit` (default
scope `Total`: the session's full active context) OR
`active_context_tokens >= model_context_window` (the hard model cap).
Setting `model_auto_compact_token_limit` low is therefore a genuine Codex
config field doing exactly what we want, not a rig hack — confirmed
directly against the merge point in `session.rs`/`context_window.rs`, not
inferred from behavior alone.

**Verified working, 2 adhoc calibration runs (in-container, throwaway
`CODEX_HOME` + workdir under `evals/results/.e6-calibration/`, gitignored,
not committed), both 100% reliable:**

1. `codex exec -c model_auto_compact_token_limit=30000` against 2×200KB
   synthetic padding files (read-then-summarize prompt): 1 compaction
   fired at line 28 of a 45-line rollout (`rollout_parser.parse_session().
   compactions == 1`, matching the `context_compacted` marker count
   exactly — no double-count from the paired bare `compacted` record).
2. The SAME knob set via a prepended `config.toml` line (not `-c`) —
   the actual mechanism the real scenario uses, since quorum's codex
   launcher takes no extra CLI flags — also fired reliably (2 compactions
   in that run's 48-line rollout; confirmed both via the CLI's own visible
   "context compacted" output and independently via
   `rollout_parser.parse_session()`).

**Delivery mechanism for the real scenario:** `scenarios/cx-compaction/
setup.sh` prepends `model_auto_compact_token_limit = <N>` (env-overridable,
default 40000) to the codex-agent's already-provisioned `config.toml`
BEFORE the coding agent launches. This works because (verified directly
against `evals/src/agents/codex.ts` + `evals/src/runner/index.ts`):
`CodexAgent.provision()` writes a plugins-only `config.toml` to
`<runDir>/home/.codex/config.toml` and runs strictly BEFORE `runSetup()`
(`setup.sh`) — so by the time `setup.sh` executes, the file already
exists at a path computable from `$QUORUM_WORKDIR`
(`<runDir>/coding-agent-workdir`) as `$(dirname
"$QUORUM_WORKDIR")/home/.codex/config.toml`. The new key MUST be
prepended, not appended: TOML keys after a `[section]` header belong to
that table, not the document root, and the provisioned file already has
`[features]`/`[plugins."superpowers@debug"]` tables.

**Threshold choice (40000), not a guess:** Task 6's real dev-rep root
rollout (`cx-eff-cx-sdd-small-dev-rep1`) has a `token_count` event curve
that climbs ~20K tokens (turn 1, system prompt + tool defs) → ~34K (turn
3) → a slow, roughly monotonic climb to a 60,422-token peak by turn 66 of
a 302-line session. 40,000 lands ~25-30% into that curve: past the
controller's own initial skill reads and first subagent dispatch (real
"pre-compaction" activity to compare), with most of a typical run's turns
still ahead (real "post-compaction" activity too). A real cx-compaction
session will grow differently (compaction adds recovery turns; the knob
changes behavior, not just counting) — if the baseline battery shows 0 or
all-immediate compactions, `out/e6-report.md` reports that honestly
rather than re-tuning the threshold after the fact to manufacture a
result.

**Scenario reuses `cx-sdd-small`'s exact plan/spec fixture** (copied to
`fixtures/compaction/`, per `run-quorum.sh`'s per-scenario fixture-merge
convention) and its Gauntlet prompt verbatim — the only difference from
`cx-sdd-small` is `setup.sh`'s config-knob injection and a longer
`quorum_max_time` (30m, generous headroom for compaction-recovery turns).
`checks.sh` is deliberately minimal (`git-repo`/`file-exists` pre,
rollout `file-exists` post only) — no `tool-called Agent` or skill-read
check, per the E2/E4 scenario-authoring lesson already in the ledger: a
post-check must not assert a behavioral choice the experiment itself
measures.

**Treatment mechanism (why baseline=dev, treatment=spinout):** the
spinout branch ships a real Codex `SessionStart` hook
(`hooks/hooks-codex.json`, matcher `"compact"` → `hooks/session-start-codex`)
that dev does NOT have at all (dev's `hooks.json` has no codex-specific
hooks). Codex re-fires `SessionStart` with `source:"compact"` after every
compaction (documented in the hook's own header comment, verified on
codex-cli 0.145.0); the hook re-injects the full `using-superpowers`
bootstrap and explicitly instructs: "Re-read the SKILL.md of any skill you
are mid-way through executing. If you are executing
subagent-driven-development, re-read
skills/subagent-driven-development/SKILL.md... also re-read
skills/using-superpowers/references/codex-tools.md and follow its
dispatch rules on every spawn_agent call." This is the literal, concrete
mechanism E6's axis-B/bootstrap-retention question (b) is designed to
detect the presence or absence of — dev has no such recovery path, spinout
does.
