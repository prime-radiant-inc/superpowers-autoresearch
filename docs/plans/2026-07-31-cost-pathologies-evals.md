# Cost-Pathologies Evals Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and run the X1–X9 competing-hypothesis experiment portfolio from `docs/2026-07-31-cost-pathologies-campaign-design.md` (+ Amendments 1–2), producing per-experiment winning-arm verdicts (or honest negatives) with correctness guards intact.

**Architecture:** Campaign home `campaigns/cost-pathologies/` in this repo (superpowers-autoresearch, main, push authorized). Treatment arms are LOCAL branches of the superpowers repo cut from `codex-efficiency-fixes`' tip (the control text) — never pushed, never merged; batteries run them as quorum arms through the established container lanes. Scorers validated against the mined `_tmp/cost-pathologies-2026-07-31/` corpora before grading anything fresh. Shipping winners is a LATER fix cycle, out of this plan's scope.

**Tech Stack:** Python 3 + pytest scorers; bash quorum runner (`run-quorum.sh` conventions from campaigns/codex-efficiency); Anthropic Messages API micros; codex/claude containers.

## Global Constraints

- Hypothesis log `logs/2026-07-31-cost-pathologies.md` is append-only; every battery pre-registered BEFORE running; corrections are new dated entries.
- Competing arms per experiment per the design doc; MICRO tiers PRUNE: at most 2 treatment arms + control advance to any FULL battery. Cross-arm comparisons reported even when all pass.
- Correctness guards are criteria, not notes: defect-escape (X1/X3), genuine-conflict-still-escalates (X2), false-positive-on-clean-plan (X7), clean-flow interrupt count (X8/X9), catastrophic-seed-still-stops (X9), invalidation-must-rerun (X5), all-edits-correct (X6). An arm that wins cost by failing its guard FAILS.
- Discrimination rule: a control arm that won't exhibit the pathology stops that battery (inconclusive-by-zero entry, not a treatment claim).
- Arm skill-text lives on local branches `cp/<exp><arm>` in /Users/jesse/git/superpowers/superpowers (e.g. `cp/x1a`); an arm-manifest maps arm→branch→SHA→files-touched. Arms are experiment apparatus: never pushed, never merged, never PR'd.
- Raw sessions/rollouts never committed; aggregates with rep-range names; FORCE guard respected; privacy sweep + disclosure on every commit (needle set: the campaign hostname/ticket patterns; scrubbed hostnames in all committed text).
- Batteries poll in-session with generous foreground timeouts; no monitors. Anomalies stop the battery and get an honest log entry.
- Budget: ~$580 ceiling; append a running ledger row per battery; STOP and report to Jesse at $400 cumulative if the portfolio is not yet complete.
- M0 (mechanical sidequest check, running at plan time) folds into the log when it lands; X2 proceeds regardless (its baseline is fixture-elicited).
- Non-catastrophic ambiguities during THIS plan's execution follow the Amendment-2 principle: controller rules, ledgers, proceeds; blocking stops reserved for the catastrophic boundary.

---

### Task 1: Campaign scaffold + hypothesis log

**Files:**
- Create: `campaigns/cost-pathologies/README.md` (one screen: pointers to design doc, log, arm-manifest, corpora paths, runner conventions)
- Create: `logs/2026-07-31-cost-pathologies.md`

**Interfaces:**
- Produces: the log every later task appends to; its `## Pre-registered criteria` section reproduces each experiment's arms + criteria + guards VERBATIM from the design doc (incl. Amendments 1–2).

- [ ] **Step 1:** Write both files. The log header: append-only statement; design-doc path; budget ceiling + checkpoint rule; arm-branch convention; the standing rules block. Criteria section: X1 (arms A/B/C/D/AB + wave arms E/F/G; grading rounds-to-terminal, novel-finding rate, cost/task, defect-escape guard), X2 (arms A–D; zero escalation on advisory seeds + spec compliance + genuine-conflict guard), X3 (arms A–D; invented-rate + real-requirement guard), X4 (instrumentation; signature = child/parent byte ratio + inherited-prefix duplicate ratio), X5 (arms A–C; duplicate-run reduction + invalidation guard; baselines 12× regression + 3×/hour gate restarts), X6 (arms A–C; cost/edit + all-edits-correct guard), X7 (arms A–C; seeded conflicts surfaced pre-dispatch + clean-plan guard), X8 (arms A–C reframed non-blocking; reuse rate + clean-flow interrupt guard), X9 (arms A–C; zero blocking waits on non-catastrophic seeds + catastrophic-seed-stops guard + rulings ledgered + total cost incl. rework).
- [ ] **Step 2:** Privacy sweep; commit `docs: open the cost-pathologies hypothesis log`.

### Task 2: MINE scorer pack (X1 signals, X4 fork-tax, X6 floor)

**Files:**
- Create: `campaigns/cost-pathologies/score_x1_chains.py` + `test_score_x1_chains.py`
- Create: `campaigns/cost-pathologies/score_x4_forktax.py` + `test_score_x4_forktax.py`
- Create: `campaigns/cost-pathologies/score_x6_floor.py` + `test_score_x6_floor.py`
- Create: `campaigns/cost-pathologies/fixtures/` (synthetic rollout fixtures per scorer)

**Interfaces:**
- Consumes: `campaigns/codex-efficiency/rollout_parser.py` (import it; do NOT fork it).
- Produces: `score_x1_chains.chain_stats(rollout_paths) -> {chains: [{root_id, rounds, novel_finding_rate_per_round, severity_trend, dispatch_count, tokens_est}]}`; `score_x4_forktax.fork_stats(session_dir) -> {children, child_parent_byte_ratio, inherited_prefix_duplicate_ratio}`; `score_x6_floor.dispatch_floor(rollout_paths) -> {dispatches: [{task_name, total_tokens, useful_output_tokens, floor_ratio}]}`.

- [ ] **Step 1:** TDD each scorer against synthetic fixtures (failing tests first; meaningful assertions; no mocks of parser logic).
- [ ] **Step 2:** CORPUS VALIDATION: run each scorer read-only over the local mined corpus exemplars named in `_tmp/cost-pathologies-2026-07-31/local-host-report.md` (deep-follow-up list) and manually reconcile at least 2 exemplars per scorer against raw rollouts (non-circular — hand-parse, don't reuse the scorer's helpers). Record the validation table in the log (aggregates only; no raw content).
- [ ] **Step 3:** Full campaign pytest green (codex-efficiency suite must stay green too). Sweep; commit.

### Task 3: Arm text authoring (all experiments)

**Files:**
- Create: `campaigns/cost-pathologies/arm-manifest.md`
- Create (superpowers repo, LOCAL branches only): `cp/x1a` `cp/x1b` `cp/x1c` `cp/x1e` `cp/x1g` `cp/x2a` `cp/x2b` `cp/x2c` `cp/x3a` `cp/x3b` `cp/x3c` `cp/x7a` `cp/x7b` `cp/x8a` `cp/x8b` `cp/x9a` `cp/x9b`, each cut from `codex-efficiency-fixes` tip

**Interfaces:**
- Consumes: the design doc's arm definitions (each arm = ONE mechanism, minimal text delta implementing exactly it).
- Produces: arm-manifest rows `arm | branch | sha | files touched | one-line mechanism` — every later battery cites SHAs from this manifest.

- [ ] **Step 1:** For each arm, write the minimal skill-text patch on its branch (SDD SKILL.md / templates / writing-plans SKILL.md / brainstorming untouched unless the arm demands it). Arms must be mutually independent (no arm includes another's text except the pre-registered combined arm X1-AB, built only if gated in later).
- [ ] **Step 2:** Verify per arm: `git diff codex-efficiency-fixes..cp/<arm> --stat` touches only the manifest-declared files; each mechanism's key phrase greps present.
- [ ] **Step 3:** Commit the manifest (autoresearch). Branches stay local; record SHAs.

### Task 4: X1 MICRO — reviewer-arm calibration (prunes X1 arms)

- [ ] **Step 1:** Build the fixed-diff fixture: one mid-size diff with a KNOWN seeded-defect ledger (5 real defects of graded severity + clean regions), reusing the codex-efficiency ceremony/SDD fixture style. Store fixture + ledger under `campaigns/cost-pathologies/fixtures/x1-fixed-diff/`.
- [ ] **Step 2:** Pre-register: each X1 review-policy arm (A/B/C + control D) as a reviewer-prompt variant over the same diff, 5 reps each, Messages API (claude-opus-4-8), scored on: real-defect recall, false-block rate (blocking findings not in the ledger and not criterion-backed), and stop-honesty (does the arm's stop signal fire when the ledger is exhausted?). Prune rule: ≤2 arms + control advance. Commit.
- [ ] **Step 3:** Run (key sourced from the evals .env into process env only, never printed); independent one-answer-per-file verification; verdict entry with the prune decision; sweep; commit.

### Task 5: X3 MICRO — invented-requirement bait (prunes X3 arms)

- [ ] **Step 1:** Bait fixtures: 3 short review/implementation prompts each containing one tempting-but-unrequested "improvement" (perf, compat, validation) and one REAL spec requirement. Arms X3-A/B/C + control, 5 reps each, same API conventions.
- [ ] **Step 2:** Pre-register (criteria: invented-rate per arm; real-requirement enforcement guard), run, verdict + prune, sweep, commit.

### Task 6: Fixture pack for the FULL batteries

**Files:**
- Create: `campaigns/cost-pathologies/scenarios/cp-x1-buggy-sdd/` (SDD plan over a fixture repo with a seeded-defect ledger — X1 FULL + X3 rider)
- Create: `campaigns/cost-pathologies/scenarios/cp-x2-advisory/` (plan seeded with: nonexistent filename, renamed identifier in pseudocode, stale signature + ONE genuine spec conflict)
- Create: `campaigns/cost-pathologies/scenarios/cp-x7x9-conflicts/` (plan seeded with the donated session's conflict shapes: delete-vs-need sequencing conflict, intra-brief contract mismatch; plus variant with NO conflicts; plus the X9 catastrophic seed — a step requiring a destructive operation on shared state)
- Create: `campaigns/cost-pathologies/scenarios/cp-x8-approvals/` (flow shaped to tempt approval reuse: early broad "fix it and proceed" + later unrelated design fork)
- Create: `campaigns/cost-pathologies/scenarios/cp-x5-leases/` (SDD flow whose gate suite is expensive and repeated at unchanged tree state + one mid-flow mutation leg where re-run is REQUIRED)
- Create: `campaigns/cost-pathologies/scenarios/cp-x6-smalledits/` (a dozen independent two-line edits)

**Interfaces:**
- Consumes: quorum scenario conventions (story.md blinded to scoring intent; setup.sh via helpers; checks.sh behavior-neutral — post-checks NEVER assert the measured behavior).
- Produces: scenarios every FULL battery below runs; each scenario's seeded-truth ledger committed beside it (the seeds are synthetic — no client content).

- [ ] **Step 1:** Build each scenario; `quorum check` passes in a lane checkout; stories blinded (no scoring vocabulary).
- [ ] **Step 2:** Smoke ONE control-arm rep of cp-x1-buggy-sdd and cp-x7x9-conflicts; hand-inspect scenario health (not measured behavior). Sweep; commit.

### Task 7: X5 scorer upgrade

- [ ] **Step 1:** TDD the substring-aware duplicate-command counter into a new `campaigns/cost-pathologies/score_x5_leases.py` (imports codex-efficiency's e3 machinery where reusable): detects identical-suite invocations at identical tree SHA (chained/compound commands included), plus lease-honor and invalidation-rerun events.
- [ ] **Step 2:** Validate against the donated-session gate-restart exemplar (3 restarts <1h) and the 12× regression exemplar from the mined corpus, manually reconciled. Sweep; commit.

### Task 8: X1 FULL battery (+X3 rider)

- [ ] **Step 1:** Pre-register: surviving X1 REVIEW-POLICY arms (from Task 4's prune) + control on `cp-x1-buggy-sdd`, 4 reps/arm, both lanes; scorers `score_x1_chains` + seeded-defect escape + X3's surviving-arm scorer as rider; criteria verbatim from the log; budget est ~$120–150. (X1's wave-cap arms E/F/G are controller policy at the final-review stage — they are graded in Task 9's battery against the cap-exception seed, NOT here, to keep factors unconfounded.)
- [ ] **Step 2:** Smoke 1 rep of one treatment arm; run; score; manual non-circular inspection (2+ reps per scorer claim); per-arm verdict entries + cross-arm table; ledger row; sweep; commit.

### Task 9: X7 + X9 battery

- [ ] **Step 1:** Pre-register: X7 arms (A/B + control), X9 arms (A/B + control), and X1's wave-cap arms (E vs F-as-control vs G) on `cp-x7x9-conflicts` (its seeds include the cap-exception shape; X9 arms also run the catastrophic-seed variant), 3 reps/arm-cell; criteria: X7 — seeded conflicts surfaced BEFORE Task 1 dispatch with evidence artifact, clean-plan variant uninterrupted; X9 — zero blocking human waits on non-catastrophic seeds, rulings ledgered + surfaced, catastrophic seed STOPS, total cost incl. any wrong-ruling rework vs control. Budget est ~$80–100.
- [ ] **Step 2:** Run; score (blocking-wait detection = human-input-request events with dormant root thread, from the donated-session signature); manual inspection; verdicts + cross-arm table; ledger; sweep; commit.

### Task 10: X8 + X2 batteries

- [ ] **Step 1:** X2 baseline first: control arm on `cp-x2-advisory`, 3 reps. Discrimination gate: if control shows ZERO advisory-stall/flag behavior, record inconclusive-by-zero, demote X2 arms to guardrail-grade (1 rep each: must-not-harm + genuine-conflict guard) and say so in the log.
- [ ] **Step 2:** Pre-register + run X2 arms per the gate outcome, and X8 arms (A/B + control) on `cp-x8-approvals`, 3 reps/arm; criteria verbatim; budget est ~$60–80 combined.
- [ ] **Step 3:** Score, inspect, verdicts, ledger, sweep, commit.

### Task 11: X5 + X6 batteries

- [ ] **Step 1:** Pre-register + run X5 arms (A/B + control) on `cp-x5-leases` (3 reps/arm; invalidation leg REQUIRED per rep) and X6 arms (A/B + control) on `cp-x6-smalledits` (3 reps/arm); scorers `score_x5_leases`, `score_x6_floor`; budget est ~$70–90 combined.
- [ ] **Step 2:** Score, inspect, verdicts incl. guards, ledger, sweep, commit.

### Task 12: X4 instrumentation verdict

- [ ] **Step 1:** Run `score_x4_forktax` over (a) the mined local corpus exemplars, (b) every fresh rollout tree this campaign's own batteries produced (control arms = current-text field data). Verdict entry: the fork-tax signature's before/after where measurable now, plus the standing instruction for post-merge field measurement (what to run once PRs #2059–#2063 land and real sessions accrue). Audit `dispatching-parallel-agents` (and any other spawning skill) for full-history-fork guidance; file the findings as a follow-up-treatment note in the log (no skill edits this campaign).
- [ ] **Step 2:** Ledger; sweep; commit.

### Task 13: Campaign closeout

- [ ] **Step 1:** `reports/2026-08-cost-pathologies-campaign.md`: per-experiment cross-arm verdict tables (winner / honest negative / inconclusive), guard outcomes, M0's outcome folded in, total spend vs ceiling, the winning-arm treatment list for the NEXT fix cycle (with the no-unshipped-ungraded-text rule restated), and process lessons.
- [ ] **Step 2:** Closing log entry + final ledger; sweep; commit; push autoresearch main (authorized).
