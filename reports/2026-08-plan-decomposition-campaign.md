# Plan-Decomposition Campaign — Closeout Report

**Dates:** 2026-08-03 → 2026-08-05. **Spend:** ≈$420 across ~70 container
reps + micro-batteries + elicitations (per-battery figures in the log).
**Log:** `logs/2026-08-03-plan-decomposition-campaign.md` (append-only;
every battery pre-registered before launch; corrections published in
place). **Arms:** `campaigns/cost-pathologies/arm-manifest.md`.
**Model:** the `codex_sub` lane never pinned a model — recorded served
models were gpt-5.6-terra (146 reps) and gpt-5.6-sol (81 reps); see the
2026-08-05 served-model census CORRECTION entry in the log (per-rep
model is now a mandatory scoring covariate).

The campaign set out to redo writing-plans/SDD in the direction of radical
decomposition, walking-skeleton ordering, knowledge-forwarding,
review-rathole relief, and verification dedupe. It closed most of those
axes — several negatively, with the negative results being the campaign's
most transferable findings.

## Headline results

### 1. The authority gap is closed by artifacts, not text (SHIP: PR #2086)

Same seeded-incoherence plan, five configurations:

| configuration | seeded conflicts resolved |
|---|---|
| specless, stock skills | 0/5 ×3 |
| specless + P2 value-table gate | 1/5, 0/5, 0/5 |
| specless + p2s spec-anchored rows | 0/5 ×3 |
| specless + p2g (the dismissers' own elicited counter) | 0/5 ×3 |
| **spec present, stock skills** | **4-5/5** |
| spec present + gate text | 5/5 + autonomous resolution |

Four texts — including the failing sessions' own elicited
counter-rationalization — cannot move the specless wall; the bare spec
moves it for free. Each side of a plan-internal contradiction is
individually plan-mandated, so with the plan as the only authority in
scope, incoherence is unfalsifiable. Hand-reads sharpened this: specless,
the coherence-gate text often never even deploys; spec-present, the same
skill base enumerates and resolves without special text. **The spec's
presence is what makes process text bind.** Ship: the plan header names
its spec; SDD reads it (PR #2086, draft).

### 2. Arm-design doctrine: where prose binds (the campaign's transferable finding)

Three elicited-counter arms, three outcomes, one pattern:

- **Reclassify an act at a moment the agent already attends to → works.**
  x13 ("about to re-run → that's regenerating evidence you failed to
  read; re-read instead"): 0/31 reviewer re-runs vs 7/~59 in control
  (5/8 control reps affected). PASS → PR #2089.
- **Require a new procedure at an unprompted moment → fails.** x12
  (enumerate every anchor instance before verdict): 1/8 catches = the
  pooled baseline rate; reviewers with the text in their template never
  grepped an anchor. Same class: d1p (identity check before re-run;
  2/4 uptake), and the earlier x1a/b/c review-policy arms (0 effect).
- **Substitute text for missing authority → fails hardest.** The p2
  family above.

Attention is routed by artifacts, task structure, and what scripts print —
not by instructions about where to look. K1 confirmed the doctrine's
uptake half from the positive side (attended-moment hooks bound fully)
while showing binding ≠ outcome (below).

### 3. Verification dedupe: the raw-count narrative was wrong (published correction)

A pre-registered split scorer (redundant same-tree / fresh post-change /
focused; `git add`/`commit` are not tree changes; merges of tested
branches are evidence-carrying; ledger writes don't invalidate) reframed
the "3-14 controller re-runs per rep" story: **truly redundant same-tree
runs are ~1/rep in every arm including control.** Most raw "re-runs" were
legitimate fix-loop and post-change runs. Controller-side dedupe has no
headroom to buy (d1s parked; d1p's raw-count "conditional efficacy" claim
corrected in the log). The reviewer seat was the one live leak
(evidence-illegibility class, 6/16 treatment reps) — closed by x13.

### 4. Plan-artifact shape: closed negative (granularity adaptation)

Nobody writes the 32-task plan: authors compress task-count to fit the
writing budget while execution preserves full scope (34/34 modules in
every arm). Monolith / directory / incremental plan formats are
indifferent on every measured axis; the incremental variant costs +26%.
The return-window overflow model this axis was built on is refuted at
these scales.

### 5. Knowledge-forwarding (K1): mechanism binds, efficiency null

The handoff file was read by 5-6/6 implementers and appended every task
(attended-moment placement worked) — and implementers then re-read every
primary source anyway: 32/38*/44 cross-implementer re-reads vs control
41/46/51 (*truncated rep). Supplementary, not substituted, reading;
cost-neutral. The unmeasured axis where the observed "integration
decisions" blocks suggest real value: **decision-consistency across
tasks** — a specified K1' seeds a cross-task binding decision and measures
its survival. Not run (campaign closed).

### 6. Review-rathole triage (R1 micro): the fix is free at the judgment layer

64-call micro-battery: every triage policy (plain, suppress, downgrade,
cleanup-wave) protects the seeded real bug 8/8 — and a genuine defect
flips the review's posture so structure-noise gets raised alongside it
regardless of policy. Downgrade-to-deferred / cleanup-wave achieve
non-blocking structure handling with zero measured guard cost;
suppression buys nothing further and destroys information.
Recommendation: formalize SDD's deferred-minor ledger into explicit
triage classes (text drafted at synthesis; per the standing rule it needs
a verbatim battery run before shipping as a PR).

### 7. Parked with evidence (not silently dropped)

- **P3 walking-skeleton / P4 right-sizing:** current fixtures complete at
  ceiling regardless of plan shape; a battery is inconclusive by
  construction. A discriminating fixture is specified (seeded integration
  trap; rework-after-first-integration-failure metric).
- **d1s structural evidence lease:** arm built; no measurable headroom
  (see 3).
- **T9 tooling ask:** two drafted texts; placement recommendation =
  brainstorming, batched into the design presentation, answer recorded in
  the spec's Global Constraints — on the campaign's own evidence that
  execution-seat asks become stalls or ride-along bundles. Empirical
  A-vs-B cell needs the interactive path (~$40-60), queued as optional.

### 8. The interrogation method: scope bounded empirically

Seven interrogations produced five convergent rationalization classes
(post-merge habit, green-as-waiver, single-instance generalization,
evidence-illegibility, ride-along bundling; plus
scope-statement-as-verification-waiver and plausibility-fill from the
CLAUDE.md-lift campaign's probes). Method scope, now measured: elicited
counters repair mis-specified triggers and produce working arms when
their counter lands at an attended moment (x13); they do not create new
procedures (x12) or substitute for missing authority (p2g). The
`--seat controller/reviewer/implementer` selection is now in the promoted
instrument after a seat-misattribution artifact was caught and struck.

### 9. Instrument integrity (5 new artifact classes found and fixed)

Annotation-blind value regex; heading-variant section swallowing;
DEVIATION_RE undercount (corpus-calibrated fix + regression tests);
seat misattribution; stale-tree vacuity (a 0/5 rep initially scored 5/5
— scan now resolves worktrees, all 15 prior reps re-validated, zero
verdict flips). Standing disciplines added: validators exercise the real
checks.sh; headroom scans before arm-build; scorers built and baselined
before their battery launches.

## Composed ship battery: PASS

`cp/pd-ship` (the exact #2086 + #2089 texts co-present) ×3 on
cp-x10-spec: **5/5 seeded conflicts resolved in every rep**
(hand-verified non-vacuous), post-checks 19/19 ×3, gauntlet pass ×3,
$20.24. No regression from the 4-5/5 stock-with-spec baseline —
matches the gated arms' uniform 5/5. #2086's SDD sentence is thereby
battery-run verbatim, co-present with #2089's paragraph.

## Ship state

| item | status |
|---|---|
| PR #2086 spec-travels-with-plan | draft, evidence complete + composed battery PASS (5/5 ×3) |
| PR #2089 x13 illegibility row | draft, battery PASS |
| PR #2080 X7-A evidence-bearing preflight | draft (earlier) |
| PR #2077 / x9a2 thread text | x9a2 mechanism now confirmed from the failure side (ride-along interrogation); text held for the thread |
| PR #2078 X6-A batching | merged to dev upstream |
| R1 triage classes text | drafted; needs verbatim battery before PR |
| green-as-waiver shared doctrine | candidate text for a future doctrine pass |
| K1' decision-consistency, P3 integration-trap fixture, T9 A/B cell | specified, unfunded |
