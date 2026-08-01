# Queue-Execution Campaign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close all 23 items in `reports/2026-08-cost-pathologies-campaign.md` §6 — each ends fixed, answered, designed, or parked-with-evidence.

**Architecture:** Instruments → scenario hardening → fixtures (MICRO-validated) → batteries (pre-registered) → design/park → closeout. Test base is `sim/dev-postmerge` in the superpowers repo (dev + PR #2059–#2064 heads); all `cp/*` arms rebased onto it.

**Tech Stack:** Python scorers + pytest in `campaigns/cost-pathologies/`, quorum container lanes A/B, local git arm branches.

## Global Constraints

- §6 of `reports/2026-08-cost-pathologies-campaign.md` is the requirements source; every task cites its item numbers and the closeout maps all 23.
- Append-only log `logs/2026-08-01-queue-campaign.md`: pre-registration before every battery; corrections as new dated entries; never edit an existing entry.
- Scorer changes need regression tests run against real campaign artifacts (rep trees under lane result dirs / `_tmp` mining extracts) — never only synthetic strings. Tests live in `campaigns/cost-pathologies/tests/`.
- Never commit: `_tmp/` corpora, raw session transcripts, lane `.env` files, `/tmp/cp-arm-*` paths, literal donor hostnames (use remote-host-a / remote-host-b) or donor usernames.
- Arms (`cp/*`, `sim/*`) are local-only: never pushed, merged, or PR'd.
- Battery spend requires a log pre-registration naming: arms, n, tier, scorer, pass/fail criteria, and the discrimination guard. MICRO before FULL for any new fixture.
- All subagent work in the autoresearch repo commits to `main` locally; pushes happen only at Jesse-authorized checkpoints.

---

### Task 1: score_x1_chains fixes (items 11, 12)

**Files:**
- Modify: `campaigns/cost-pathologies/score_x1_chains.py`
- Test: `campaigns/cost-pathologies/tests/test_score_x1_chains.py`

**Requirements:**
- [ ] Item 11: `_extract_findings()`'s `NONE_VALUE_RE` recognizes prose-none variants ("none identified beyond the X above", "no new findings", "none beyond …") without swallowing real findings; add corpus-derived positive and negative cases.
- [ ] Item 12: detect the fourth chain pattern — a single reviewer re-tasked repeatedly via `NEW_TASK`/`MESSAGE` envelopes — and count it as chain depth alongside fresh-spawn chains. Verify against the X1 FULL rep artifacts where the pattern is known absent (no false positives) and a constructed fixture where it is present.
- [ ] Re-run the scorer over the archived X1 battery outputs; log any headline number that moves as a dated correction entry (do not rewrite the report silently).
- [ ] Commit.

### Task 2: score_x5_leases fixes (items 9, 10)

**Files:**
- Modify: `campaigns/cost-pathologies/score_x5_leases.py`
- Test: `campaigns/cost-pathologies/tests/test_score_x5_leases.py`

**Requirements:**
- [ ] Item 10: `lease_events` counts distinct events — dedupe on `(kind, command_norm, tree_sha)` and/or read the final receipts file once; scan exec **call** command text, not only output.
- [ ] Item 9: add a prose-aware honor detector alongside (never replacing) the strict `LEASE-HONORED:`/`LEASE-INVALIDATED:` grammar; report both counts separately so strict-vs-prose divergence stays visible.
- [ ] Regression tests from the X5 battery's real reviewer-prose exchanges (the 8 unencrypted exchanges are the positive corpus).
- [ ] Re-run over archived X5 outputs; log moved numbers as corrections.
- [ ] Commit.

### Task 3: scorer hygiene sweep (items 13, 14)

**Files:**
- Modify: any scorer with a dot-directory glob defect; `campaigns/cost-pathologies/score_x3_rider.py`
- Test: `campaigns/cost-pathologies/tests/test_scorer_hygiene.py`

**Requirements:**
- [ ] Item 14: audit every `glob`/`rglob`/`Path.glob('**…')` in `campaigns/cost-pathologies/*.py` for the dot-directory miss; fix with `os.walk` or literal dot components; test with a fixture tree containing `.worktrees/.superpowers/.codex` layers.
- [ ] Item 13: add a blocking-precision BAIT signature (narrower than the recall signature) as a separate function; the two manually-corrected false positives from the campaign are the test's negative cases. Leave the recall signature untouched.
- [ ] Commit.

### Task 4: scenario hardening (items 15, 20, 21, 22, 23)

**Files:**
- Modify: `campaigns/cost-pathologies/cp-x7x9-conflicts/story.md` (and `-clean`, `-prose` variants), `cp-x2-advisory/story.md`, `cp-x8-approvals/story.md`, `cp-x1-buggy-sdd/checks.sh`
- Possibly modify: battery runner scripts (ledger capture, provenance)

**Requirements:**
- [ ] Item 15: every scripted Gauntlet reply in the three scenarios becomes a pinned verbatim string with an explicit "reply with EXACTLY this text, no paraphrase" instruction. The x9b ad-lib that voided a rep is the motivating case.
- [ ] Item 20: `cp-x1-buggy-sdd/checks.sh` gains a `main`-advanced-past-seed check reported as its own line (not folded into pass/fail — the 31% non-merge rate is a graded outcome, not an exclusion).
- [ ] Item 21: ruling recorded in the log — keep the 60m ceiling, grade non-merge as an outcome (default), OR size up; state the choice and why.
- [ ] Item 23: the runner captures `.superpowers/sdd/*/progress.md` content to the rep's result dir before/independent of the session's own workspace deletion.
- [ ] Item 22: investigate why `provenance.superpowers_rev` is null; fix if it's a runner-side one-liner, else document the gap and the per-invocation stderr echo as the fallback.
- [ ] Commit.

### Task 5: X1 edit-existing-code fixture (item 1)

**Files:**
- Create: `campaigns/cost-pathologies/cp-x1-edit-existing/` (story.md, setup.sh, checks.sh, seeded starting repo)

**Requirements:**
- [ ] Starting code (not prose) carries the seeded defect shapes from the X1 design; the task is an edit/extend of that code so the defect-escape guard is finally reachable.
- [ ] Deflections pinned verbatim from birth (Task 4's standard).
- [ ] Seeded-truth ledger written alongside (which defects exist, where, what escape/catch looks like) before any run.
- [ ] MICRO validation: 2 reps, verify the scorer discriminates on seeded truth; log verdict.
- [ ] Commit.

### Task 6: X1 wave-cap independent fixture (item 2)

**Files:**
- Create: `campaigns/cost-pathologies/cp-x1-wavecap/` (or a revised plan file within the X1 scenario family)

**Requirements:**
- [ ] Plan whose cap-exception is reachable regardless of how other conflicts resolve — no earlier task may moot the cap-exception's target (the Conflict-1-composition defect named in item 2).
- [ ] Earlier tasks conflict-free so arms E and G reach their own mechanism.
- [ ] Seeded-truth ledger + pinned deflections + MICRO validation (2 reps); log verdict.
- [ ] Commit.

### Task 7: X6 plan-framed fixture + MINE tier (item 3)

**Files:**
- Create: `campaigns/cost-pathologies/cp-x6-planframed/`
- Create: `campaigns/cost-pathologies/x6_mine_dispatch_floor.py` (mined-corpus dispatch-floor distribution)

**Requirements:**
- [ ] Fixture frames the dozen-small-edits work as an explicit plan/task list (accepting that this tests "does X6 help once SDD is engaged" — state this in story-adjacent docs and the log).
- [ ] MINE tier: dispatch-count distribution from the `_tmp` corpora (read-only), giving the fixture's dispatch counts a real baseline; results into the log, script committed, corpus never committed.
- [ ] Seeded-truth ledger + pinned deflections + MICRO validation (2 reps); log verdict.
- [ ] Commit.

### Task 8: X8 confound-free + X2-B isolation fixtures (items 4, 5)

**Files:**
- Create: `campaigns/cost-pathologies/cp-x8-approvals-v2/`
- Create: `campaigns/cost-pathologies/cp-x2-consequential/`

**Requirements:**
- [ ] X8 v2: remove the "note your reasoning in the report" mandate (the disclosure confound); stark approval boundary; n sized so `Ruling:` grammar has a fair shot on the hard case.
- [ ] X2-B isolation: file-structure/naming choice consequential enough for a reviewer to hold an opinion (a real reorganization, not edits-in-place).
- [ ] Both: seeded-truth ledgers, pinned deflections, MICRO validation (2 reps each); log verdicts.
- [ ] Commit.

### Task 9: X5 savings battery at scale (item 6) — after Tasks 2, 4

**Requirements:**
- [ ] Size the X5 plan up (5+ tasks with genuine re-verification surface) so the duplicate-verification worst case (anchored at 10×, per the report's corrected count) is reachable.
- [ ] Pre-register in the log: arms A/B/control, n≥8 per arm, FULL tier, distinct-event scorer (Task 2), savings criterion, discrimination guard.
- [ ] Run on lanes A/B against rebased `cp/x5a`/`cp/x5b`; score; verdict entry answering item 6 (real reduction vs variance).
- [ ] Commit scorer outputs summary (not raw reps) + log entry.

### Task 10: X3-B controller-half battery (item 7) — after Task 4

**Requirements:**
- [ ] Mount rebased `cp/x3b` as a real FULL arm for the first time; pre-register (n, criteria: does grep-and-flag fire on unsourced inventory lines end-to-end; discrimination guard).
- [ ] Run, score with the blocking-precision signature from Task 3 where applicable; verdict entry answering item 7.
- [ ] Commit.

### Task 11: X7+X9 composed battery (item 8) — after Task 4

**Requirements:**
- [ ] Compose rebased `cp/x7a` (or `x7b`) + `cp/x9a` into `cp/x7x9-composed`; this battery is ALSO the re-validation gate for the rebased x9a/x7 text (standing rule: no ungraded text ships).
- [ ] Pre-register: pinned-deflection scenario (Task 4), n≥9 across composed/x9-only/control, stall + preflight + catastrophic-guard criteria.
- [ ] Run, score, verdict entry answering item 8 and explicitly stating whether rebased-text behavior matches the original battery's.
- [ ] Commit.

### Task 12: new-fixture batteries (items 1–5 runs) — after Tasks 5–8

**Requirements:**
- [ ] One pre-registered FULL battery per validated fixture: X1-edit (~16 reps), wave-cap (~9), X6 plan-framed (~12), X8 v2 (~9), X2-B consequential (~9). Sizes adjustable on MICRO evidence; any cut is flagged in the log, not silent.
- [ ] Each battery's verdict entry answers its §6 item by number.
- [ ] Budget check against the design's envelope before each battery; stop and ask Jesse if cumulative spend would exceed $1000.
- [ ] Commit summaries + log entries per battery.

### Task 13: parser scope, honoring channel, scope auditability (items 16, 17, 19)

**Files:**
- Modify: `campaigns/cost-pathologies/` X7-B conflict-scan script + tests
- Create: design section in the log / a short design note for item 19

**Requirements:**
- [ ] Item 16: regression tests encoding the three ratified parser limits; implement multi-name backtick span decomposition if tests show it's a local change; document the other two limits as tested-and-deferred.
- [ ] Item 17: amend the X5-A design (design-doc amendment entry) to echo honor/invalidate lines through an unencrypted channel; no battery this campaign.
- [ ] Item 19: one-page design for machine-readable declared scope in dispatch briefs, explicitly marked as input to the plan-decomposition campaign.
- [ ] Commit.

### Task 14: closeout (items 18 + all)

**Files:**
- Create: `reports/2026-08-queue-campaign.md`
- Modify: memory + log closing entry

**Requirements:**
- [ ] Item 18 parked with the evidence gap named (no gemini/pi/antigravity corpus on any reachable host).
- [ ] Closeout report: 23-row table mapping every §6 item to fixed/answered/designed/parked + evidence pointer; new queue section; budget actuals.
- [ ] Needle sweep (staged diffs AND commit messages) before the final push checkpoint; push only with Jesse's authorization.
