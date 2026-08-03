# Backlog Campaign Implementation Plan (2026-08-02)

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development.

**Goal:** Execute the 12-item new queue from `reports/2026-08-queue-campaign.md` §6
(item 2, the X6-A gate, closed same day — PR #2078).

**Method:** Same discipline as the queue campaign: pre-registration before every
battery in `logs/2026-08-02-backlog-campaign.md`, append-only log with dated
corrections, guards as criteria, discrimination rule, pinned deflections, needle
sweeps (diffs AND commit messages) before every commit, no ungraded shipped text.
Test base `sim/dev-postmerge` @ 1fed99d; arms local-only (cp/*); lanes A+B.

**Budget:** ~$973 available; battery estimate ~$220.

## Tasks

### Task 1: Instrument + runner hardening (items 8, 10, 11)
- Fix LIST_ITEM_RE heading-context `- None.` false positive (26 corpus
  occurrences) in the X-series scorers; corpus-validate before/after counts.
- Runner hardening in `campaigns/cost-pathologies/run-quorum.sh`: invoke
  setup.sh via `bash` explicitly (exec-bit failure class); never gate arm
  chains on rep exit codes (check-fail = data, not infra-fail).
- Vendored plan-conflict-scan drift note: document the touch-both-copies rule
  at the top of both copies.

### Task 2: Evals-repo provenance fix (item 9)
- In the evals repo (`evals/`): make in-container runs record provenance even
  from a linked worktree whose `.git` pointer is unreachable — resolve
  gitdir before containerizing or pass provenance in env. Commit locally;
  push needs Jesse (standing auth covers autoresearch only).

### Task 3: X9-A escape-hatch tightening battery (item 1)
- Controller drafts cp/x9a2 = cp/x9a + tightened "every path forward is a
  guess" clause in all three sites (stop-list ¶, digraph node, adjudication
  ¶). Operational core: a ruling you can write down is not a guess;
  confirm-asks on rulings already made are stalls.
- Battery on `cp-x7x9-conflicts` (pinned): x9a2 ×3 (lane B) + x9a ×2
  contemporaneous control (lane A). Full pre-registration in the log before
  launch.

### Task 4: X2-B review-only micro-battery (item 5)
- Adapt the x1-review-micro API pattern to the committed X2 deviation trees;
  n≥10 review calls/arm; grade deviation-detection rate. ~$10.

### Task 5: Real-defect final-review fixture + X10 arms (items 4, 3)
- Fixture: multi-task plan seeding ≥4 REAL cross-module defects that a
  whole-branch final review should catch (the 45 missed seeds were all
  greppable — encode that class).
- Arms: control / reviewer-checklist line / mechanical consistency scan run
  at final review. Battery ×3 per arm after fixture review.

### Task 6: Behavioral re-verification treatment (item 7 + Jesse's dedupe directive)
- Design an arm that changes the ACT at the re-verify moment: reviewer and
  controller do not re-run tests/linters the implementer already ran on the
  same commit — they read the implementer's test transcript; re-running is
  reserved for changed code or contested claims.
- Battery on `cp-x5-leases-scaled`: treatment ×4 + control ×2. Metric:
  duplicate-run rate (same suite, same tree-SHA, different agent), completion
  parity, cost.

### Task 7: Aged-session replay harness (item 6)
- Design doc + prototype: replay a mined aged-session prefix into a live
  session to test late-session pathologies (unlocks X3-B and the
  localization thesis's direct test). MICRO-tier validation only this
  campaign.

### Task 8: Residual grading depth (item 12)
- Grader subagents write per-rep review-dynamics narratives for the X5/X6/X2
  batteries into a log appendix; no new batteries.

## Order
T1 → T2 (parallel with T1's review; different repo) → T3 (battery early,
wall-clock) → T4 → T8 → T5 → T6 → T7 → closeout. Batteries overlap with
instrument tasks wherever lanes are free.
