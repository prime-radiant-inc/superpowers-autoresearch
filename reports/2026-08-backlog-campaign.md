# Backlog Campaign — Closeout Report (2026-08-03)

One session, 2026-08-02 → 2026-08-03. Ran the 12-item queue from
`reports/2026-08-queue-campaign.md` §6 under SDD (implementer/reviewer
subagents for build tasks; batteries and arm text by controller,
disclosed per-entry). Log: `logs/2026-08-02-backlog-campaign.md` (every
claim below has a dated entry). Test base `sim/dev-postmerge` @ 1fed99d;
zero deflection voids; zero infra-lost reps.

## 1. All 12 items closed

| # | item | disposition |
|---|---|---|
| 1 | X9-A escape-hatch tightening | **ANSWERED-WITH-CAVEAT** — cp/x9a2 SAFE (no-stall 3/3, DROP guard 5/5, rulings ledgered, 0/3 bundled ruling-asks) but attribution INCONCLUSIVE: contemporaneous x9a controls 0/2 (T11's 3/4 baseline didn't reproduce; base rate draw-unstable). Text held for PR #2077's thread, not shipped separately |
| 2 | X6-A boundary gate | **PASSED + SHIPPED** — dispatch parity 14/14/13 vs 16/13, completion parity 5/5 → **PR #2078** (eval-ask posted to @arittr) |
| 3 | X10 mechanical consistency scan | **ANSWERED (negative as review-time treatment)** — scan closes the ATTENTION gap (candidates 14/14 with file:line reach the reviewer) but 100% dismissed under PLAN AUTHORITY; checklist arm 2/3 praised drift as design. Scanner re-aimed at plan time (campaign 2) |
| 4 | Real-defect final-review fixture | **FIXED** — cp-x10-consistency (5 plan-induced greppable defects, MICRO-validated, blinded; reviewer-verified) + general x10-consistency-scan.py (5/5 detect, 0 FP) |
| 5 | X2-B review-only micro-battery | **ANSWERED** — x2b lens suppresses structure-only findings **10/10 → 0/10** (noise floor 0/20, ~$5, 40 calls); plain reviewers escalate structure conformance to the controller — the rathole ask-class. Suppress-vs-downgrade is now a campaign-2 policy question with clean effect size |
| 6 | Aged-session replay harness | **DESIGNED** — `docs/2026-08-03-aged-session-replay-design.md` (commit-boundary cuts, compacted-replay primary, in-distribution + fresh-prefix negative-control validation; first consumer X3-B) |
| 7 | Behavioral re-verification treatment | **ANSWERED (negative)** — X11 "verification is read, not re-run" text: controller pytest counts unmoved (control 8/9 vs treatment 5/7/16/6, median 6.5 vs bar ≤2); one controller read the rule then re-ran anyway. THIRD informational negative at the verify moment → the fix class is STRUCTURAL |
| 8 | `- None.` LIST_ITEM_RE false positive | **FIXED** — corpus delta 320 findings/82 reps (cited subset exactly 26); X1 table correction published (control .483→.448, x1b .565→.435, no verdict flips) |
| 9 | Evals-repo provenance fix | **FIXED + LIVE-VERIFIED** — host-side QUORUM_SUPERPOWERS_REV/_DIRTY resolution; fresh verdicts carry the worktree SHA where they carried null. Commits LOCAL in the lane-A evals clone — **push awaits Jesse** |
| 10 | Runner hardening | **FIXED** — exec-bit preflight before container launch + tolerant-chaining rule documented in run-quorum.sh |
| 11 | Vendored-scan drift discipline | **FIXED** — sibling-copy header rule in the vendored copy |
| 12 | Residual grading depth | **DONE** — 50 per-rep narratives (X5 24, X6 17, X2 9); three campaign-shaping discoveries below |

## 2. Headline findings

1. **The authority gap.** Wave-cap's 0/45 reviewer blindness decomposes
   into two gaps. The mechanical scan CLOSED the attention gap — every
   seeded inconsistency reached the final reviewer as a file:line
   candidate. Plan authority then dismissed 100% of them ("the plan
   explicitly requires 30 and 90"): each side of a plan-induced
   inconsistency is individually plan-mandated, so implementation
   review — correctly applying its own spec-compliance rubric —
   blesses the incoherence. Consistency defects born in the plan are
   structurally invisible to post-hoc review; they must be caught at
   PLAN time. This is campaign 2's empirical cornerstone, joining the
   attention-routing thesis.
2. **Verification duplication is behavioral and controller-seated.**
   Narratives localized the 3-14×/rep duplicate test-running to the
   controller (reviewers already decline); a direct prohibition in the
   controller's own instructions changed nothing (X11 null — third
   informational negative after X5's receipts and leases). Dedupe
   requires removing the redundant run from the action space:
   dispatch design, tooling, or harness.
3. **The x2b review lens works — completely.** 10/10 → 0/10
   suppression of structure-only findings at zero false-positive cost,
   measured for ~$5 by a review-only micro-instrument after $26 of
   full sessions couldn't see it (no natural deviations, 0/9). Two
   campaign-2 inputs: the lens (or a downgrade variant) as the
   review-triage mechanism, and micro-instruments as the first resort
   for judgment-layer questions.
4. **X9-A's stall pathology is draw-unstable.** Same arm text: 3/4
   turn-1 bundling in one draw, 0/2 in the next. Treatments validated
   against single-draw baselines can be chasing variance; a-priori
   base-rate replication belongs in pre-registration when the
   pathology is the treatment's whole justification.
5. **Instrument doctrine held its streak.** The 4th strict-grammar
   undercount (DEVIATION_RE 1/10 vs true 10/10) was caught by the
   mandatory hand-rescore before any conclusion; the X11 scorer's
   payload-shape miss (all-zeros) was caught by an implausibility
   check. Neither reached a published number.

## 3. Ship state

- **PR #2078** (X6-A batching) — open against dev, eval-ask posted.
- **PR #2077** (X9-A never-stall) — open; x9a2 tightening text held
  for its thread (safe, unproven benefit).
- **Evals-repo provenance commits** (c7d9e77/0323d4f, lane-A clone) —
  reviewed, live-verified, awaiting Jesse's push authorization.
- Closed negative: cp/x11, cp/x10a, cp/x10b (as review-time
  treatments), cp/x9a2 (as standalone PR).

## 4. Budget

Batteries this campaign: gate $40.86 + x9a2 $15.87 + X2-B micro ~$5 +
X11 $49.66 + X10 $66.56 = **$177.95**. Envelope: $1000 original −
$486.06 (queue campaign) + $500 added − $177.95 = **≈ $836 remains**.

## 5. Campaign 2 inputs (writing-plans/SDD redo)

Empirical foundation now in hand: attention-routing thesis + authority
gap (consistency is a plan-time property); structural-dedupe
constraint; x2b lens effect size + suppress-vs-downgrade policy
question; X6-A batching shipped and boundary-proven; W hypothesis
(authoring-side right-sizing) registered; plan-as-directory +
scope-auditability designs on file; replay-harness design for
aged-session claims; MINE dispatch floor-ratio 79,504× cost anchor.
Jesse's directive adds: walking-skeleton ordering, knowledge-forwarding
between implementers, cleanup-wave ledger triage, per-task plan files
(return-window failures), and the tooling-setup ask
(brainstorming vs writing-plans placement).
