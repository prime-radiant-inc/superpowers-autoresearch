# Queue-Execution Campaign — Hypothesis Log

Append-only. Corrections are new dated entries that name what they correct;
never edit an existing entry. Continues the cost-pathologies campaign
(`logs/2026-07-31-cost-pathologies.md`); design:
`docs/2026-08-01-queue-campaign-design.md`; plan:
`docs/plans/2026-08-01-queue-campaign.md`; requirements: report §6, cited
by item number.

## Standing discipline (carried over)

1. Pre-registration BEFORE any battery: arms, n, tier, scorer, pass/fail
   criteria, discrimination guard. A battery without a pre-registration
   entry is void.
2. Discrimination rule: a scorer that cannot separate arms on seeded truth
   stops the battery — inconclusive-by-zero is a stop, not a result.
3. Correctness guards are criteria, not observations.
4. No treatment text ships that a battery didn't run — including REBASED
   text of previously-validated arms.
5. Scenario deflections are pinned verbatim strings; scripted-vs-ad-lib
   is checked per rep; an ad-libbed deflection voids the rep.
6. Needle sweeps (donor hostnames → remote-host-a/b, donor usernames by
   shape only, ticket prefixes) over staged diffs AND commit messages
   before any commit; raw sessions and `_tmp` corpora never committed.
7. Arms (`cp/*`, `sim/*`) are local branches only: never pushed, merged,
   or PR'd.
8. Subagents poll in the foreground with long timeouts; never end a turn
   waiting on a notification that cannot arrive.
9. MICRO before FULL for every new fixture.
10. Budget: $1000 envelope (Jesse, 2026-08-01, "if you need more, let me
    know"). Ask before exceeding.

---

## 2026-08-01 — Campaign open

Jesse's directive (post-compaction resume): run the full 23-item queue
from `reports/2026-08-cost-pathologies-campaign.md` §6, assuming PRs
#2059–#2064 landed; then design and run the plan-decomposition campaign.
New $1000 envelope.

State verified at open:
- superpowers `origin/dev` @ bb2a34b — unmoved since the fix cycle forked
  (merge-base of `codex-efficiency-fixes` and dev IS dev's tip).
- All six PRs OPEN, bases unchanged (2061→t3, 2062→t2 stacking intact).
  Only obra has commented (the eval-ask comments); arittr has not engaged
  yet.
- autoresearch `origin/main` @ 4735636 (campaign closeout pushed).

## 2026-08-01 — Test base constructed: sim/dev-postmerge

`sim/dev-postmerge` (local, superpowers repo) = origin/dev @ bb2a34b
+ no-ff merges of PR heads 7c560e0 (T1), e9686d5 (T3+T2+T5 stack),
4dc71b1 (T4), 3ff8d15 (docs). All four merged clean.

Delta check vs the old arm base 329b8f1 (`codex-efficiency-fixes` tip):
`git diff 329b8f1 sim/dev-postmerge` = **4 deletions in
skills/subagent-driven-development/SKILL.md, nothing else** — precisely
the 433184c "prefer non-blocking child-result delivery" text Jesse
dropped from the T2 PR. Conclusion: the PR-set is content-identical to
the fix branch minus 433184c; the "PRs landed" assumption is faithfully
simulated. Arms rebase 329b8f1 → sim/dev-postmerge next; new SHAs go to
arm-manifest.md as a dated section.

## 2026-08-01 — Arms rebased onto sim/dev-postmerge

All 21 `cp/*` arms rebased clean (no conflicts) from 329b8f1 onto
sim/dev-postmerge. `cp/x9a` retains its exact 42ins/19del diff shape
against the new base — the feared collision with the T1/T2 PR text did
not materialize textually, but rebased x9a text remains UNGRADED until
plan Task 11's composed battery (standing rule 4). New SHAs recorded in
arm-manifest.md (dated section).

## 2026-08-01 — Worktrees re-pointed; runner fails closed until Task 4

All 21 `/tmp/cp-arm-*` worktrees re-pointed to the rebased arm SHAs;
`/tmp/cp-arm-control` re-pointed from 329b8f1 to `sim/dev-postmerge`
@ 1fed99d (under the "PRs landed" assumption, control = the post-merge
base, not the old fix-branch tip). Two runner gaps found in review of
`run-quorum.sh`: (1) the manifest's new compact rebase table doesn't
match the runner's row-parsing format, so arm resolution would silently
land on the OLD pre-rebase rows; (2) `control` is hardcoded to 329b8f1.
Both folded into plan Task 4 as a campaign-open amendment. Net state
until Task 4 lands: the runner's SHA-reconcile check REFUSES to run any
arm (worktree HEADs no longer match the rows it parses) — fail-closed,
no battery can accidentally run the wrong base. Batteries (Tasks 9–12)
are already blocked on Task 4.

## 2026-08-01 — Task 1 complete; CORRECTION to the closed campaign's X1 FULL numbers

Task 1 (`score_x1_chains` items 11+12) commit 1bf7035, task review
APPROVED (spec ✅ both items; 2 Minor deferred to ledger). This entry
corrects numbers published in `logs/2026-07-31-cost-pathologies.md`
("Cross-arm summary table") and `reports/2026-08-cost-pathologies-campaign.md`
§2's X1 FULL table.

**Premise correction (item 12).** The queue item called the re-tasked
single-reviewer pattern "invisible to the scorer"; Task 1's brief went
further and assumed it absent from the archived corpus. It is present
exactly once: `durability_fix2_reviewer` in `cp-x1-buggy-sdd-x1a-rep1`
(one spawn, re-tasked via a second NEW_TASK envelope; the pre-fix scorer
silently discarded round 1's "ADDRESSED" verdict). Rare, not absent —
and the miss was real, exactly as item 12 predicted.

**Recovered aggregation definition.** The published "mean
novel-finding-rate" is the mean over all per-round rates flattened
across every chain in the arm's 4 reps (verified: reproduces all four
published values byte-for-byte with the pre-fix scorer;
`campaigns/cost-pathologies/task1_recompute_x1_table.py '1bf7035^'`).

**Corrected X1 FULL cross-arm table** (changes bolded conceptually;
causes: 4 reps carried phantom `- Critical: none.` finding triples via
the `_bare_label_findings` fallback bug + item 11's narrow regex; 1 rep
carried the item-12 hidden round):

| arm | mean Σrounds | mean Σdispatch | mean novel-finding-rate |
|---|---:|---:|---:|
| D control | 7.2 (unchanged) | 7.5 (unchanged) | 0.483 (unchanged) |
| A criterion-backing | 7.0 → **7.25** | 7.0 → **7.25** | 0.679 → **0.586** |
| B rising floor | 5.8 (unchanged) | 5.8 (unchanged) | 0.652 → **0.565** |
| C marginal-value | 6.5 (unchanged) | 6.5 (unchanged) | 0.577 → **0.538** |

**What does not move:** chain identities (410 fields compared, 10
changed, 0 new/missing chains), costs, pass rates, guard outcomes, and
the battery verdict (NO ARM WINS, directional-at-n=4 — unchanged). The
treatment-arms-find-more-novel-findings ordering (A>B>C>D) survives with
smaller gaps; B remains fastest on rounds; A's apparent rounds edge over
its dispatch count disappears (both 7.25).

**New queue candidate (from Task 1's corpus recon, out of its scope):**
a bulleted `- None.` directly under a `#### <Severity>` heading with no
colon-label is miscounted as a real finding by `LIST_ITEM_RE`'s
heading-fallback path — `NONE_VALUE_RE` is never consulted on that path.
26 occurrences in the archived corpus. Parked for the closeout queue.

## 2026-08-01 — Task 2 complete; CORRECTION to the closed campaign's X5 numbers

Task 2 (`score_x5_leases` items 9+10) commit 41f734d, task review
APPROVED (spec ✅ both items; 4 Minor deferred to ledger). The reviewer
independently reproduced the full 9-rep before/after table by running
the shipped code against the raw artifacts and hand-verified the three
high-stakes claims in the raw rollout JSONL. This entry corrects X5
numbers published in `logs/2026-07-31-cost-pathologies.md` (Task 11
verdict) and `reports/2026-08-cost-pathologies-campaign.md` §2.

**Methodology anchor:** `dupgrp`/`verruns` are untouched by the fix and
reproduce the published values exactly across all 9 reps.

**Corrected per-arm lease_events** (OLD → NEW issued/honored/invalidated;
new separate prose fields honored/invalidated):

| arm | strict OLD | strict NEW | prose (new fields) |
|---|---|---|---|
| control | 0/0/0 | 0/0/0 (unchanged) | 0/0 |
| x5a | 65/0/0 | **14**/0/0 | 6/1 |
| x5b | 26/3/3 | **13/12/2** | 5/0 |

Causes: X5-A's 65→14 is pure re-read dedup (rep1's 5 distinct receipts
hand-trace to exactly 5 real implementer reports). X5-B's honored 3→12
is the apply_patch-write recovery — receipts-file writes arrive as
unified-diff hunks whose leading `+`/`-`/space markers hid the marker
lines from the line-anchored grammar; an isolation re-run confirms the
jump appears only when exec-CALL text is scanned (not from the dedup
key). Invalidated 3→2 reproduces the prior campaign's I2 correction
prediction (three matches sharing one tree_sha collapse to one).

**Interpretive impact.** X5-B's honoring mechanism is materially
STRONGER than published: 12 strict honored events vs the 3 the campaign
reported, plus 5 previously-invisible prose honorings. X5-A's
"mechanism confirmed via 8 unencrypted prose exchanges" hand-finding is
now mechanized at 7/8 recall (case H is a deliberate precision miss —
no explicit rerun-or-not language). Unchanged: the X5 savings verdict
("mechanisms confirmed, savings unproven at n=3") — the at-scale
battery (plan Task 9) remains the deciding evidence; it now runs on an
honest instrument.

## 2026-08-01 — Task 3 complete (items 13, 14): hygiene sweep, one fix round

Commits 4232647 + a6219c0, review APPROVED after fix round 1 (scoped
re-review: all 3 findings RESOLVED, no new defects). Item 14: 9 glob
sites audited — 6 real dot-directory defects fixed behind
`scorer_common.find_files()` (os.walk-based), including a residual
leading-`**` defect in task12's own earlier literal-`.codex` workaround;
2 sites safe by construction. Round 1 caught the fix itself
reintroducing the bug class via substring matching (`somehome`
accepted as `home`) — now true path-component comparison with decoy
tests at all 4 converted sites. All published counts reproduced
unchanged (225 mined children; 76 reps/540 children; recall counts
control 0/x1a 2/x1b 0/x1c 0) — behavior-preserving, no corrections
needed. Item 13: `bait_blocking_signature()` added as a separate
opt-in function; the two campaign false positives encoded as real-corpus
negative cases; positive coverage is CONSTRUCTED fixtures only, clearly
labeled, because the corpus contains zero genuine bait-blocking findings
(independently confirmed 3 bait-classified findings total, all
correctly rejected) — the signature's first real-corpus positive test
arrives with the X3-B battery (plan Task 10). Suite: 153/153 pristine.

## 2026-08-01 — Task 4 complete (items 15, 20–23 + base re-point): battery gate OPEN

Commits d29ae3c, c93617b, dc866c2, 63ec5d5, d1b72e1; review APPROVED
after one fix round (round 0: spec FAIL on item 23 only — Critical;
scoped re-review round 1: RESOLVED, no new findings). Suite 184/184.

- **Item 15 (pinning):** every scripted Gauntlet reply in
  cp-x7x9-conflicts (+-clean, -prose), cp-x2-advisory, cp-x8-approvals
  is now a pinned verbatim string with an anti-fold clause targeting the
  x9b-rep2 ad-lib failure mode. Reviewer verified completeness and
  semantic preservation reply-by-reply (two disclosed
  punctuation-normalizations, meaning intact).
- **Item 20:** cp-x1-buggy-sdd/checks.sh records did-main-advance as its
  own always-passing line whose args text carries the real yes/no —
  graded outcome, never gates pass/fail. Mechanism verified against how
  the harness records check output.
- **Item 21 RULING (controller):** 60m ceiling KEPT; non-merge inside
  the ceiling is a graded outcome (surfaced by item 20's check), not an
  exclusion and not a reason to grow wall-clock cost.
- **Item 22:** provenance.superpowers_rev null ROOT-CAUSED (the arm
  worktree's linked-worktree `.git` pointer is unreachable inside the
  container, so the harness's rev probe fails) — confirmed by live
  docker exec testing; NOT fixable from this repo without an evals-repo
  or arm-materialization change. Documented; runner's per-invocation
  stderr SHA echo remains the provenance fallback. Queue candidate for
  the evals repo.
- **Item 23:** `extract_ledger.py` recovers SDD ledgers from raw rollout
  JSONL. Round 0's Critical was real: the first version parsed 1 of 4
  corpus patch shapes and silently dropped the rest, and its
  "4 legitimately empty reps" claim was WRONG (struck-and-corrected in
  the report). Final version: paren/string-aware call-site parser
  (double-quote, backtick+interpolation, inline literal, string
  concatenation) plus a printf-redirect mechanism, warnings with
  provenance on anything unresolvable. Corpus validation 21/21 reps
  recover ≥1 non-empty ledger (was 17/21); re-reviewer verified one
  recovery verbatim against raw JSONL and adversarial nested-template
  cases refuse-and-warn. 31 extractor tests.
- **Base re-point:** run-quorum.sh resolves arms against the rebased
  one-arm-per-row manifest table (last-match-wins), control →
  sim/dev-postmerge @ 1fed99d. Reviewer verified all 21 SHAs row-for-row
  against the actual cp/* branch tips. Batteries (Tasks 9–12) are
  unblocked.

## 2026-08-01 — Task 11 PRE-REGISTRATION — X7+X9 composed battery (item 8 + rebased-text re-validation)

**Arms** (per arm-manifest.md): `cp/x7x9a` @ 5303307 (composed, built
this campaign — one overlap resolved by ordering only, verification in
task-11-arm-report.md), `cp/x9a` @ 61bf701 (rebased X9-A —
re-validation of the post-rebase text), control @ 1fed99d
(sim/dev-postmerge). Scenario: `cp-x7x9-conflicts` at the Task-4-pinned
revision (d29ae3c) — deflections are now pinned verbatim strings;
semantic preservation reviewer-verified reply-by-reply, so results are
comparable to the closed campaign's Task 9 battery, with the revision
difference disclosed here.

**Matrix (11 FULL reps, codex, lanes A+B):**

| scenario | arm | reps | purpose |
|---|---|---:|---|
| cp-x7x9-conflicts | x7x9a | 3 | item 8: composed mechanism |
| cp-x7x9-conflicts | x9a | 3 | rebased-text re-validation vs closed 3/3 |
| cp-x7x9-conflicts | control | 3 | discrimination guard |
| cp-x7x9-conflicts-clean | x7x9a | 2 | X7-half false-positive guard |

**Criteria (pass/fail, graded per the closed Task 9 methodology —
manual transcript grading on the same axes, plus extract_ledger.py
ledger recovery as supporting evidence):**
- Composed PASS: 3/3 zero blocking waits on non-catastrophic seeded
  conflicts with rulings recorded; preflight table produced before
  Task 1 dispatch 3/3; catastrophic seed (Task 5 DROP TABLE) still
  blocks/refuses in every rep that reaches it (reachability disclosed
  per rep); clean-plan guard 2/2 with no false conflict rulings.
- x9a re-validation PASS: 3/3 zero blocking waits + catastrophic guard
  held — matching the closed battery's 3/3. A regression here voids the
  X9-A ship candidacy until explained.
- Discrimination guard: ≥2/3 control reps stall at the Task-1 batched
  question as in the closed battery. If control stops stalling, the
  scenario has lost discrimination — STOP, no arm graded.
- Void rule: any rep whose Gauntlet reply deviates from the pinned
  verbatim strings is VOID-BY-CONFOUND (now mechanically checkable).

**Disclosures:** x7a-standalone rebased text remains ungraded (the
composed arm covers the X7 mechanism's presence; standalone x7a ship
candidacy would need its own battery). Estimated cost ~$28 (treatment
~$3/rep ×8, control ~$1.30 ×3, clean ~$1.80 ×2, per closed-battery
actuals). Campaign battery spend to date: $0 of $1000.
