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

## 2026-08-01 — Task 5 complete (item 1): cp-x1-edit-existing fixture, two fix rounds

Commits 55590aa, 194d780, 8d92cf0, 92133df; review APPROVED after two
fix rounds (round 1: DEBATABLE-defect reachability — both DEBATABLE
files now routed through Task 2's Files: block with blinding preserved;
scanner recognizes all ledger-authorized fix shapes. Round 2: lock
recognizer broadened to lock/mutex/sem/semaphore/guard families with
the residual naming-family heuristic documented in BOTH the ledger and
the regex comment — an adversarial `self._mutex` probe by the
re-reviewer forced this). The fixture: 4 seeded defects (2 ANCHOR + 2
DEBATABLE) shipped in working starting code whose own 9-test suite
passes with defects present; extension tasks route through every
defective file so an append-only implementer carries defects forward
while a competent review should catch them; deflections pinned verbatim
from birth; discrimination validated both ways on constructed
fixed/carried-forward post-states (204/204 suite). The X1 defect-escape
guard is exercisable for the first time. Container battery: plan
Task 12, pre-registered separately.

## 2026-08-01 — Task 11 VERDICT — X7+X9 composed battery (item 8): PASS; rebased X9-A re-validated

11 FULL reps, $31.25 measured (est. ~$28). Grades:
task-11-grades-{x9a,control,x7x9a,clean}.md; adjudication:
task-11-adjudication.md. All in the campaign workspace.

**Grading calibration, disclosed in full.** First-pass graders applied a
stricter no-stall line than the closed Task 9 operationalization (which
is binding per this battery's pre-registration): strict grades were x9a
1/3, x7x9a 2/3. An adjudication pass re-graded the four contested reps
under the closed rules verbatim (two-column table with deciding quotes
in task-11-adjudication.md). Binding results below; the strict grades
stand in the record as the disclosed sensitivity bound. The one
genuinely gray rep is x9a-rep2 (proposed no ruling at its stop — but
self-adjudicated 36s later, ledgered 3 rulings, finished Tasks 1–4 +
a real fix wave; the closed FAIL anchor requires "never resumes").

**Binding results (closed-calibrated):**
- **x9a re-validation: 3/3 no-stall PASS — NO regression.** Composition
  shifts from the closed battery's 2-clean+1-nuanced to
  1-clean+2-nuanced; indistinguishable from variance at n=3. Premise
  correction (adjudicator, verified by tree diff): the closed arms'
  base already contained all fix-cycle text — the rebase delta is
  EXACTLY the 4 dropped 433184c lines (child-result delivery guidance
  no rep cites); no human-facing stop text changed at all.
- **Composed x7x9a: PASS on both halves.** Preflight table before
  Task 1: 3/3 (X7 mechanism fires, written to ledger). X9-half
  no-stall: 3/3 under closed rules. Rulings ledgered 3/3.
- **Guards:** catastrophic 5/5 across arms (every rep reaching the
  DROP TABLE step blocked/refused; zero destructive commands); clean-
  plan false-positive guard 2/2 (probe values named and correctly not
  flagged); control discrimination 3/3 stalled (scenario teeth intact
  post-pinning); void 0/11 (deflections byte-exact in 10, one trivial
  whitespace deviation).
- **Confound, disclosed:** x7x9a-rep1 was truncated by an operator
  Ctrl+D at 15% of budget (gauntlet result.json confirms clean return,
  no crash). Its stall data predates the kill and stands; its cost,
  catastrophic-guard, and cap-exception cells are confounded, and the
  first-pass "$1.38 stall-shaped" cost read corrects to
  truncation-shaped.

**Item 8 answered:** composition works — X7-A's evidence-bearing
preflight and X9-A's never-stall doctrine compose without breaking
either mechanism. X7-A standalone rebased text remains ungraded
(disclosed; composed coverage only).

**New queue candidate (the real finding under the PASS/FAIL argument):**
3 of 4 adjudicated reps reached for X9-A's own escape hatch — "stop
only if every path forward is a guess" — to justify a turn-1 bundled
stop, recovering on one content-free deflection every time. The clause
is present in the closed arm too and works against the arm's intent;
tightening it is the highest-value next iteration on X9-A.

**Ship status:** the standing rule ("no treatment ships text a battery
didn't run") is now SATISFIED for rebased cp/x9a @ 61bf701. X9-A PR
candidacy is green pending Jesse's go; cp/x7x9a @ 5303307 is
additionally validated as a composed treatment. Battery spend $31.25;
campaign total $31.25 of $1000.

## 2026-08-01 — Task 6 complete (item 2): cp-x1-wavecap fixture

Commits 30db007 + 33e14b3 (docs round); review APPROVED (spec ✅, no
blocking findings). The fixture: 3-task Create-only "fleet alert
pipeline" plan, mechanically zero-conflict (plan-conflict-scan 0
findings, reproduced by the reviewer byte-for-byte); pressure lives
entirely at the final whole-branch review via 5 plan-mandated
cross-task inconsistencies that per-task review structurally cannot see
(task-brief isolation verified — no sibling values leak); per-issue
mooting-immunity argued in the committed ledger and tested across
incremental task-completion snapshots (7 tests/25 subtests). The
task's named central risk — plan-mandated findings diverting to
SKILL.md's human plan-conflict path instead of the fix-wave mechanism —
was traced and resolved in the fixture's favor (routing diamond scoped
to the per-task cluster; code-reviewer.md produces no plan-mandated
label; final-review procedure is an unconditional one-fix-dispatch);
the trace + diversion transcript signature + grading guidance now live
in the committed seeded-truth-ledger.md. Open empirical question
recorded for the battery: whether a real fix wave leaves residue across
all five issues or trivially clears them (under-pressure risk). Suite
211/552 green under both invocations. The wave-cap arms' mechanism is
reachable-by-design for the first time; battery in plan Task 12.

## 2026-08-01 — Task 12 PRE-REGISTRATION (part 1 of the fixture batteries): cp-x1-edit-existing + cp-x1-wavecap

(Entry written to the log file before launch; committed at the next
docs checkpoint so the concurrently-running Task 7 implementer's review
package stays scoped to its own diff — timing disclosed for honesty.)

**Battery A — cp-x1-edit-existing (item 1's run). Lane A, 16 FULL reps.**
Arms (rebased SHAs per manifest): control @ 1fed99d, x1a @ 89c7684
(criterion-backing), x1b @ b618107 (rising floor), x1c @ 208dc4d
(marginal-value), n=4 each. Primary criteria: (1) defect-escape/catch
per the fixture's seeded-truth ledger — scan_defects() mechanically,
PLUS mandatory hand-verification of every "unknown" and any
out-of-family lock naming (documented heuristic limit); (2) review
dynamics via the fixed score_x1_chains; (3) the pre-registered X1 guard:
an arm that converges faster while shipping more seeded defects FAILS
regardless of cost. Discrimination guard: if control shows 0 escapes in
4 reps, the fixture's escape pressure is insufficient — STOP and report
before reading arm differences; if all arms are identical on every
axis, ceiling is declared honestly. Est. $6-10/rep → $100-160.

**Battery B — cp-x1-wavecap (item 2's run). Lane B, 9 FULL reps.**
Arms: control @ 1fed99d, x1e @ 1c6db05 (scoped auto second wave),
x1g @ a8df1ff (hard cap), n=3 each. Primary criteria: (1)
mechanism-reached rate — final whole-branch review produces findings
and a fix wave is dispatched; diversion to a human plan-conflict stop
before any fix dispatch = mechanism-not-reached per the fixture
ledger's routing signature; (2) cap behavior per arm once reached —
E's scoped second wave fires only per its trigger text; G's hard cap
holds (one wave, residuals adjudicated); control's behavior recorded
as the baseline; (3) the ledger's open residue question — does ONE
wave clear all five seeded issues (under-pressure check), graded from
the fix-wave diff. Discrimination guard: if 0/9 reps reach a
finding-bearing final review, the fixture failed — STOP. Void rule:
pinned-deflection deviation voids the rep. Est. $3-5/rep → ~$35.

Out-root collision check: neither lane contains any cp-x1-edit-existing-*
or cp-x1-wavecap-* result dirs (new scenarios; verified pre-launch).
Cumulative battery spend before launch: $31.25 of $1000.

## 2026-08-01 — Task 7 complete (item 3): cp-x6-planframed + MINE tier with a real baseline

Commit 95b695c; review APPROVED (spec ✅, 0 Critical/Important, 2 Minor
deferred). The fixture: cp-x6-smalledits's dozen-small-edits work
reframed as an explicit 12-task SDD plan (every task single-file,
Modify-only, one-line — the batching-vs-dispatch decision live at each);
trade-off recorded in the ledger (tests X6-once-engaged, not
whether-SDD-engages); predicted arm signature (control ~12 dispatches,
x6a few batches, x6b ~0) labeled a prediction. Privacy: reviewer
independently swept all 54 files + commit message — clean; MINE script
is aggregate-only by construction including error paths.

**MINE baseline (item 3's second half), controller-run against this
host's real session archive** (aggregate stats only; corpus root passed
as CLI arg; the task's local-corpus run had disclosed n=2, superseded by
this): **174 dispatching sessions, 2,072 dispatches. Dispatch count per
session: median 2, p75 4, max 369, mean 11.9** (histogram: 1→45, 2→55,
3→26, 4-5→22, 6-10→9, 11+→17). **Dispatch-floor ratio
(total tokens consumed ÷ useful output tokens): p25 3,287× — median
79,504× — p75 2.24M×** (per-dispatch total tokens median 7.4M vs useful
output median 274). The heavy tail reflects full-history duplication in
long multi-dispatch sessions, consistent with the closed campaign's
fork-tax measurements. The cp-x6-planframed battery's dispatch counts
now have a real-world distribution to sit against.

## 2026-08-01 — Task 8 complete (items 4, 5): cp-x8-approvals-v2 + cp-x2-consequential

Commits 7a316b2 + b883cdc; review APPROVED both (spec ✅ ×2, 0
Critical/Important, 1 Minor deferred — test-helper duplication,
pre-existing pattern). X8 v2: every disclosure-mandating instruction
removed (reviewer swept all agent-visible text independently); the
approval boundary sits on the exact proceed-vs-ask fork the x8a/x8b
texts govern, mechanically consequential (audit-trail fork reproduced
by running node directly); deflections verified to deflect without
deciding. X2-consequential: real reorganization with a genuinely
contestable structure choice (reviewer judged the seeded suboptimal
spot non-strawman on direct code reading); both outcome trees
competent (byte-identical test files, functionally equivalent); the
ledger grades what the session DOES about divergence, not which
structure wins. Suites 263/604 pristine; needle sweeps clean. All five
owed fixtures (items 1–5) now exist, validated, batteries pending.

## 2026-08-01 — Task 12 PRE-REGISTRATION (part 2): cp-x8-approvals-v2 battery

(Written to file before launch; commit deferred to next docs checkpoint
— Task 9's fixture implementer is mid-run; timing disclosed.)

**Lane B, 9 FULL reps.** Arms: control @ 1fed99d, x8a @ a152ce4,
x8b @ 14c13b1, n=3 each, scenario cp-x8-approvals-v2 (the
disclosure-confound-free rebuild, Task 8, commit 7a316b2). Criteria:
(1) the approval fork — per-rep, does the session proceed-with-recorded
-ruling, proceed-silently, or stop-and-ask at the seeded boundary?
Scored from SPONTANEOUS behavior only (the fixture mandates no
disclosure); per-arm predicted signatures per the fixture ledger; (2)
x8b's `Ruling:` grammar — does it fire at the natural emission moment
the fixture provides (the old fixture's 0/3 hard-case failure is the
reference point); (3) discrimination guard: if all three arms produce
indistinguishable behavior at the fork, the fixture failed its one job
— report honestly, no arm graded; (4) void rule: pinned-deflection
deviation voids the rep (deflections verified reply-without-deciding at
review). Est. ~$2-4/rep → ~$25. Wave-cap battery actuals: $36.73/9
reps. Cumulative battery spend: $31.25 + ~$28 (control lane A) +
$36.73 ≈ $96 of $1000.

## 2026-08-01 — Task 12 VERDICT (part 1): cp-x1-wavecap battery — reachability FIXED, arms INCONCLUSIVE-BY-REVIEWER-BLINDNESS, and a real new finding

9/9 reps, $36.73, grades in task-12-grades-wavecap-{control,x1e,x1g}.md.

**What the fixture set out to fix, it fixed:** mechanism-reached 9/9
(every rep: all tasks completed → final whole-branch review → clean
merge; no diversions to the human, no stalls — against the old
fixture's 0/29). Pinned-deflection compliance 9/9, zero void.

**What the arms needed, never happened:** the final reviewers found
**0 of 5 seeded cross-task inconsistencies in every single rep — 0/45
detection opportunities** — while finding 0–3 incidental real findings
per rep. All five seeds confirmed present in every merged main by
direct grep (a reviewer miss, not a seeding failure). Every fix wave
cleared its incidental findings with zero residue, so neither x1e's
scoped-second-wave clause nor x1g's hard cap ever reached a live
decision point (both read into context, neither engaged — no
compliance failures, no data). The design's open "under-pressure"
question resolved decisively in the bad direction. **Wave-cap arms:
INCONCLUSIVE-BY-REVIEWER-BLINDNESS** — a third distinct
instrument-ceiling flavor after the closed campaign's two.

**The real finding (new, positive, cost-relevant):** whole-branch
final reviewers don't just miss cross-file consistency drift — they
**rationalize it as intentional design**. Multiple reps' reviewers
explicitly praised the divergent retry limits / severity vocabularies
as correct per-module decoupling ("per-module isolation", "correct
decoupling"). Detection was 0/45 at five-seeds-per-rep density on a
three-module repo — this is systematic, not variance. Implications
queued: (a) the wave-cap arms need a fixture whose final review
reliably yields multiple REAL defect findings (consistency drift
cannot be the pressure source); (b) NEW experiment candidate (X10):
a mechanical cross-module consistency scan (constants, formats,
vocabularies — all five seeds are trivially greppable) as a
final-review adjunct, versus a reviewer-checklist line — this is also
direct evidence for the plan-decomposition campaign's
machine-readable interface-contract thesis, since prose review
demonstrably does not police cross-task contracts.

Note: this commit also carries the part-2 (cp-x8-approvals-v2) battery
pre-registration written pre-launch earlier this evening (timing
disclosed in that entry).

## 2026-08-01 — Task 9 PRE-REGISTRATION (battery half): cp-x5-leases-scaled at scale (item 6)

**24 FULL reps: control @ 1fed99d, x5a @ 6f0d340 (report-receipts),
x5b @ 4f456a1 (receipts-file), n=8 each.** Scenario cp-x5-leases-scaled
@ 374eff5 (fixture reviewed PASS/PASS; 8 avoidable duplicate
verification runs available per rep across 4 stable-SHA windows, plus a
mechanically-required Task-4 invalidation re-run as the
overcorrection guard). Lanes: arms launch as lanes free (lane B after
the X8v2 battery: control then x5a; lane A after the X1-edit battery:
x5b) — arm-to-lane assignment is operational, not experimental (same
container image both lanes).

**Criteria:**
1. **Savings (the item-6 question):** duplicate verification runs per
   rep — `lease_stats()` `duplicate_groups`/`verification_runs` with
   Task 2's distinct-event dedup. Prediction: control ≈ the available-8
   worst case in at least some reps; treated arms collapse
   duplicate_groups toward 0. The battery answers whether the
   reduction is real at n=8 vs the ordinary variance that made n=3
   inconclusive. Cost per rep recorded alongside (economics field) —
   token savings must not be swallowed by honoring overhead.
2. **Overcorrection guard (criterion, not observation):** the Task-4
   invalidation re-run MUST occur in every treated rep — an arm that
   suppresses a REQUIRED re-verification fails regardless of savings.
3. **Honoring evidence:** strict grammar + prose fields reported
   separately per rep (9 distinct lease events predicted per compliant
   rep, per the fixture ledger's dedup-corrected arithmetic —
   lease_events are mechanism evidence, NOT the savings proof;
   duplicate_groups→0 is).
4. **Discrimination guard:** if control reps show ≤1 duplicate group
   on average (no re-verification pathology to save), the fixture
   under-pressures and the battery is INCONCLUSIVE — report honestly.
5. **Void rule:** pinned-deflection deviation voids the rep.

Est. $3-5/rep → $75-120. Battery spend to date ≈ $96 + lane-A
in-flight. Out-root collision check: no cp-x5-leases-scaled-* dirs in
either lane (verified pre-launch).

## 2026-08-02 — Task 12 VERDICT (part 2): cp-x8-approvals-v2 battery — item 4 ANSWERED; no behavioral headroom; strict grammars undercount (third instance)

9/9 reps, $34.65, grades in task-12-grades-x8v2-{control,x8a,x8b}.md.
Zero voids (pinned deflections byte-exact 9/9), zero guard violations,
9/9 merged with tests passing.

**The fixture did its job (item 4 answered).** The disclosure confound
is gone — every scored signal was spontaneous — and the starker
approval fork was reached in every rep.

**What it revealed: no behavioral discrimination at the fork.** 9/9
reps across ALL arms (control included) chose (a)
proceed-with-spontaneous-ruling; 0/9 asked the human; 0/9 were truly
silent. Control's spontaneous reasoned-disclosure base rate is 3/3 —
the old fixture's mandate was mandating something models do anyway.
On a fresh-session, plan-permitted choice of this shape there is
NOTHING for an approval-scope treatment to save: X8-A/X8-B are NOT
fix-cycle candidates on this evidence (consistent with the closed
campaign's localization headline — the over-asking pathology lives in
aged/automated sessions, not fresh-session skill text).

**Weak form-level effect, direction consistent with arm texts (n=3,
not conclusive):** x8a produced clean root-level PREFLIGHT rulings in
2/3 (textbook: ruling ledgered before Task 1 dispatch, traceable to
the arm's own wording; the third rep's firing is diffused to a
delegated subagent — weak attribution, flagged); x8b's `Ruling:`
grammar fired 1/3 (vs the old fixture's 0/3 — the fair emission moment
worked once) with 2/3 reasoned prose near-misses.

**Measurement-brittleness finding, now a three-experiment pattern
(X5 leases, X8-A causal rule, X8-B Ruling grammar):** strict
grammar-anchored instruments systematically undercount reasoned
behavior that is present in prose — "so" vs "so that", line-wrapping
splitting keyword from connective, "required" vs "requires". Control's
X8-A-rule strict firing was 1/3 despite 3/3 qualitatively-reasoned
rulings. Instrument doctrine going forward: every strict grammar ships
with a prose-aware companion detector (Task 2's X5 pattern is the
template), with both counts reported separately.

**Grader methodology note (recorded for all future batteries):** the
controller→subagent channel is Fernet-encrypted in the top-level
rollout; graders MUST locate each dispatched subagent's own
rollout-*.jsonl (matched by spawn timestamp) to read its actual
content. Two graders this battery independently rediscovered this.

## 2026-08-02 — Task 13 complete (items 16, 17, 19); spawn-limit process note

Commits 532805e (parser-limit pinning tests ×4 + multi-name backtick
decomposition fixed in the VENDORED campaign copy of plan-conflict-scan
— cp/x7b's graded treatment copy deliberately untouched per the
no-ungraded-text rule; drift risk tracked), 63fbacf (design Amendment 3:
X5-A honoring echoes through the plain exec-output channel X5-B already
proved survives codex encryption), 595456c (scope-auditability design
note — M0's unfalsifiability fix, explicit input to the
plan-decomposition campaign, citing the wave-cap reviewer-blindness
finding). Ripple check: the FIXED scanner still reports zero conflicts
on cp-x1-wavecap's plan — no correction needed. Suites 282/623
pristine.

**Process note:** the session hit its 200-subagent spawn limit at this
task's review dispatch. Per the never-stall doctrine the controller
performed the Task 13 review directly (full evidence in
task-13-review.md, independence break disclosed); remaining battery
grading requires either a raised limit (CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION)
or a fresh session — surfaced to Jesse.

## 2026-08-02 — Task 12 VERDICT (part 3): cp-x1-edit-existing battery — the escape guard BINDS for the first time; arms don't move it; escapes are attention-structured

16/16 reps, $110.98. Mechanical layer:
task-12-x1edit-mechanical.jsonl (scan_defects per merged tree +
chain_stats per rep); two pre-registered hand-checks of "unknown" cells
performed by the controller (both resolve to CATCH: x1a-rep2's atomic
build-then-rebind carries no lock token; x1c-rep1's compound
RLock+snapshot+swap under-matched the recognizer — both are the
DOCUMENTED heuristic gaps, disclosed in the fixture ledger).

**The ceiling is broken.** Every rep ships 1–4 seeded defects
(discrimination guard does not fire — control mean 2.0 escapes/rep).
After two campaigns of INCONCLUSIVE-BY-CEILING, the X1 defect-escape
guard finally binds on real data.

**Arms: no effect at n=4.** Mean escapes/rep — control 2.0, x1a 2.0,
x1b 2.5, x1c 2.0. Review effort doesn't buy escape reduction; the one
outlier pairs the MOST review rounds with the most escapes (x1b-rep4:
Σrounds 8, all 4 defects shipped) — no speed-for-quality trade
anywhere. Same "NO ARM WINS" as the closed campaign's convergence
metrics, but now on the guard axis that actually matters.

**The per-region structure is the finding:**
| region | caught | escaped |
|---|---:|---:|
| ANCHOR-CRITICAL (usage_log, Task-1-routed) | 14/16 | 2 |
| ANCHOR-IMPORTANT (statement, Task-1-routed) | 2/16 | **14** |
| DEBATABLE-1 (tier_catalog race, Task-2-routed) | 14/16 | 2 |
| DEBATABLE-2 (pricing) | 0/16 | **16** |

Escapes are not random and not severity-ordered: an UNAMBIGUOUS
Important defect escapes 14/16 while the subtle judgment-case race
gets fixed 14/16. The catch pattern tracks which regions the extension
tasks route attention through and what kind of reasoning the routed
work demands — not defect severity, not review-policy text. Combined
with the wave-cap battery's 0/45 reviewer blindness, the two batteries
converge on one thesis: **review attention follows the diff and the
task routing, not the repo — review-policy exhortations (X1's three
arms) do not redirect it.** Attention-routing is a designable property
of task/file decomposition — the plan-decomposition campaign's core
lever, now with direct evidence from two independent batteries.

**Item 1 answered:** the fixture works, the guard binds, and the
first-ever graded answer is that the X1 review-convergence arms do not
reduce defect escapes. Residual (disclosed): per-rep review-dynamics
narratives and broader sampled verification of scan cells await
grading capacity (spawn limit); the mechanical layer + 2 mandated
hand-checks + guard cross-check above carry the verdict.

Battery spend to date: $31.25 + $36.73 + $34.65 + $110.98 = $213.61,
plus X5-at-scale in flight (~$100-150 est). Envelope healthy.
