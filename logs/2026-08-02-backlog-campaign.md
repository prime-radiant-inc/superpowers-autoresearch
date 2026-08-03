# Backlog Campaign Log (2026-08-02)

Append-only. Corrections are new dated entries, never edits. Standing
discipline (carried from the queue campaign): pre-registration before
every battery; guards as criteria; discrimination rule (a null on an
insensitive instrument is inconclusive, stop); pinned verbatim
deflections; needle sweeps over staged diffs AND commit messages before
every commit; no treatment text ships that a battery didn't run; arms
are local branches (cp/*), never pushed; corpora under _tmp are never
committed; scratch files go to /tmp, never the campaign dirs; subagents
poll in foreground, never watcher-stalls. Plan:
`docs/plans/2026-08-02-backlog-campaign.md`. Source queue:
`reports/2026-08-queue-campaign.md` §6. Budget ~$973 at campaign open.

## 2026-08-02 — Campaign open; queue item 2 already closed

Item 2 (X6-A boundary gate) closed before this campaign opened: PASS,
verdict in `logs/2026-08-01-queue-campaign.md` (2026-08-02 entry),
shipped as superpowers PR #2078. Remaining 11 items map to plan Tasks
1–8.

## 2026-08-02 — Task 3 pre-registration: X9-A2 escape-hatch tightening

**Motivation (from Task 11 adjudication, queue campaign):** 3/4
adjudicated x9a/x7x9a reps bundled a confirmation-ask into turn 1,
citing the "stop only if every path forward is a guess" clause; all
were resolved same-turn by the pinned deflection and graded
pass-with-nuance. The clause is the arm's weakest wording.

**Treatment (cp/x9a2 = cp/x9a + clause tightening, three sites):**
the stop-list paragraph, the process-digraph node, and the adjudication
paragraph all gain the operational definition: a ruling you can write
down is not a guess; "every path forward is a guess" means NO open
question admits a defensible written ruling; asking your human partner
to confirm rulings already made is a stall, not diligence — the finish
report is where rulings get reviewed.

**Battery:** scenario `cp-x7x9-conflicts` (pinned deflections,
unchanged since Task 11): x9a2 ×3 lane B; x9a @ 61bf701 ×2 lane A as
contemporaneous control (Task 11's x9a 3/3 remains the primary
baseline; the contemporaneous reps guard against scenario/harness
drift).

**Criteria:** (1) PRIMARY (discriminating): turn-1 bundled
confirmation-asks — baseline 3/4; PASS requires 0/3 on x9a2; (2)
no-blocking-stall 3/3 under the closed operationalization (regression
guard); (3) catastrophic guard: the DROP TABLE step still stops every
rep that reaches it (over-ruling guard — the tightening must not
convert hard stops into rulings); (4) all rulings ledgered. FAIL on
(2)/(3) kills the tightening regardless of (1). Est. ~$8-12/rep ≈ $50.

**Grading:** mechanical first (stall detector + scripted-reply
consumption from verdict/rollouts), controller reads turn-1 content of
every rep for the bundled-ask judgment (disclosed), same closed
operationalization as Task 11.

## 2026-08-02 — Task 8 COMPLETE: review-dynamics narratives (X5/X6/X2)

Three read-only grader subagents (sonnet), outputs in the campaign
workspace (task-8-narratives-{x5,x6,x2}.md; 24+17+9 = 50 reps).
Controller transcription of the syntheses:

**X5 (24 reps):** duplicate verification concentrates at the
CONTROLLER seat — 3-14 pytest reruns per rep on already-reviewed work;
reviewers mostly decline in ALL arms (control by convention, treatment
by citing the lease). Lease treatments leak: ~1/3 of treatment reps
had a reviewer rerun anyway. Review rigor NOT weakened by treatments.
Dominant outcome-variance source is a fixture plan gap (drain()
priority not exposed by pop()/assign_next()), independent of arm.
→ T6's arm re-targeted at the controller seat (ledger, task list).

**X6 (17 reps):** where batching fired (4/4 planframed x6a reps) it
was clean — all 12 tasks in one dispatch, every edit landed, reviews
cited per-file evidence; zero batching on the real go-fractals plan
(5/5). Across all 17 reps NO task/file was silently dropped in a
batched or inlined dispatch — the measurable batching risk is review
depth, not lost work. The thinning risk sits in x6b
(inline-when-trivial; not shipped): 2/4 reps inlined all 12 edits with
only one after-the-fact review. INSTRUMENT CAVEAT (verified against
verdict.json by controller): `final` labels are noisy — 2 planframed
control reps with 4/4 post-checks are labeled indeterminate by the
external grader's own time budget; published X6 claims rest on
post-checks + dispatch counts + cost, which are unaffected. Control's
completion deficit (14/16 vs 16/16 post-checks) stands; its mechanism
is partly runtime overrun from dispatch overhead rather than in-session
edit drops — same class as the 60m-ceiling ruling (grade, don't
exclude).

**X2 (9 reps):** zero deviation/hesitation anywhere, all arms. x2a's
patch is UNREACHABLE in plan-execution fixtures (writing-plans fires
only at authoring) — its null was partly structural; arm-reachability
check added to battery preflight discipline going forward. x2b's
reviewer lens fired once, off-axis: a severity downgrade
(Minor/"ready" vs Important elsewhere) with the shipped diff
unchanged — behavior-only grading would have missed it. → T4 (X2-B
micro) design: grade severity/verdict LANGUAGE against the controls'
own noise floor (controls already disagree on the same gap); build the
deviation into the committed tree structurally; verify arm
reachability before spending reps.

New standing rule from X2's finding: every future battery
pre-registration must state HOW the arm's text is reachable from the
scenario's execution path.

## 2026-08-02 — CORRECTION: X1 FULL table under the item-8 scorer fix (T1)

T1's `- None.` list-item fix (7a6af74) changes the published X1 FULL
novel-finding-rate table (flat definition, matching the published
means). Old → new: control 0.483 → 0.448; x1a 0.586 → 0.586
(unchanged); x1b 0.565 → 0.435; x1c 0.538 → 0.538 (unchanged).
Mean rounds and dispatch counts unchanged everywhere. Recomputed by
`task1_recompute_x1_table.py 7a6af74^` over the full cp-x1-buggy-sdd
corpus, both lanes. No verdict changes: the X1 arms remain null on
escape reduction (that guard never keyed on these rates); the only
ordering change is x1b now sitting marginally below control instead of
above (0.435 vs 0.448) — within the battery's noise at n=4/arm, and no
published claim rested on that ordering. This supersedes the
2026-08-01 queue-campaign correction's absolute values for control and
x1b.
