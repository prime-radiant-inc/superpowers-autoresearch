# Codex efficiency fix cycle — closeout

**Branch:** `codex-efficiency-fixes` (superpowers, off `dev`)
**Spec:** `docs/superpowers/specs/2026-07-30-codex-efficiency-fixes-design.md`
**Hypothesis log (append-only, the primary record):**
`logs/2026-07-30-codex-efficiency-fixes.md`
**SDD ledger:** `.superpowers/sdd/2026-07-30-codex-efficiency-fixes/progress.md`
**Prior campaign closeout:** `reports/2026-07-codex-efficiency-campaign.md`
**Dates:** 2026-07-30 → 2026-07-31
**Spend:** $262.61 across 89 measured battery reps (see §3), against the
campaign's shared $1000 line — combined with the prior campaign's $153.2,
≈$415.81 spent, ≈42%.

## 1. Executive summary

The prior eval campaign closed with a treatment table: twelve fix
candidates, each with a scorer and a `dev` baseline. This cycle shipped the
five evidence-strong ones (T1, T2, T3, T4, T5) as graded skill/doc changes,
took three of them through an honest FAIL on their first battery, fixed the
root cause, and re-ran until every pre-registered criterion passed. All five
treatments are **PASS** as of the last battery round. Six branches are built
and pushed against `origin/dev`; **no PRs are open** — every PR needs Jesse's
per-branch go, per the plan's own scope decision ("no merge without Jesse's
per-PR approval").

One commit was held back from what ships: `433184c` ("prefer non-blocking
child-result delivery"), because no battery's pre-registered criterion ever
graded it — see §4. A whole-branch review of the full `bb2a34b..70120d5`
diff found the five treatments mergeable with no blockers, and parked seven
findings (two Important, five Minor) for a future tightening round rather
than editing eval-graded skill text outside a battery — see §5.

## 2. Verdict table

Every criterion was pre-registered in the hypothesis log before its battery
ran (standing rule carried over from the eval campaign).

| # | Treatment | Criterion | Baseline (from the eval campaign) | Final result | Rounds |
|---|---|---|---|---|---|
| **T1** | SDD worker-review prohibition | 0 worker-issued depth-2 spawns AND review coverage preserved | 9/9 depth-2 spawns worker-issued across 4 corpora, all 9 same-task duplicates, 0 counter-examples | **PASS** — 0/51 then 0/67 spawns, 0/8 reps in both clean rounds; coverage 8/8 (exactly one reviewer per task, incl. 6/8 reps with a genuine fix-and-re-review wave) | 3 (round 1 FAIL 2/6 reps → round 2 PASS → round 3 PASS as regression guard) |
| **T2** | Event-driven waiting | timeout rate < 25%, no completion loss, and (added round 3) no silent gap > 12 min | dev 67.1% timeout rate; external corpora 74.5% / 78.3% | **PASS, full conjunction** — 0.0% timeouts (0/73 paired), 67/67 children `task_complete`, 8/8 gauntlet pass, max silent gap 3.91 min | 3 (round 1 FAIL 65.1% → round 2 FAIL on completion-loss clause only → round 3 PASS) |
| **T3** | codex-tools.md corrections | source citation + no scorer regression on the shared battery | 5 claims in `dev`'s guidance contradicted by Codex source | **PASS** — all 5 file:line-verified against source; carried through 38 battery reps with zero attributable regression | 1 |
| **T4** | Brainstorming three-path router (variant C: approval always) | L1 micro cells; L2 bounded 0 docs + strict approval, arch two-doc + completion; L3 four cross-harness criteria; L4 triggering 3/3 per harness | bounded wrote 2 ceremony docs unconditionally in every rep; the prior hard-gate text forced bounded→FULL 5/5 | **PASS, all four layers** — micro 5/5 every cell incl. 2 adversarial briefs; Codex bounded 0 docs 6/6 and strict approval 3/3; arch two-doc 3/3 on all 3 harnesses; layer 3 36/36 all 4 criteria; triggering 7/7 both clauses on all 3 harnesses | Layer 2 x2, layer 4 x2 (both round-1s FAILed and produced fix commits) |
| **T5** | Explicit model+effort on child spawns | every spawn at every depth carries explicit model + effort | root already 100% at CLI 0.146 (14/14); depth-2 0/2 | **inconclusive-by-zero at depth-2 (pre-registered branch) + PASS on the root backstop** — 51/51 then 67/67 depth-1 explicit in the two clean rounds; T1's fix removed the depth-2 population T5 was measuring | 3 (round 1 FAIL 48/50 → rounds 2/3 inconclusive-by-zero + PASS) |

T1's round-1 FAIL and T5's round-1 FAIL trace to the same root cause: commit
`62c0180`'s "you do not dispatch subagents" contract was scoped only to
`implementer-prompt.md`; reviewer roles (`task-reviewer-prompt.md`,
`re-review-prompt.md`, `code-reviewer.md`) had no such rule, so a
controller-dispatched `final_reviewer` spawned two depth-2 sub-reviewers of
its own — a real, previously-undocumented pathology distinct in shape from
the same-task-duplicate pattern the original fix targeted. Commit `c07cf7e`
extended the contract to every reviewer role; round 2 confirmed the fix
(0/51 depth-2 spawns).

T2's round 2 introduced a genuine second-order side effect: converting short
polls into one long wait means the Gauntlet-Agent QA judge — a separate LLM
watching the transcript live — now sees 20-38 minute silent stretches while
real work continues underneath, and 3/8 reps exhausted the judge's own
testing-time budget before a legitimate (not stalled) review finished.
Commit `43ec25f` bounded the wait to 5-10 minutes with a
`list_agents`/status-line reconciliation step; round 3 confirmed the fix
(0/8 indeterminate, max silent gap 3.91 min).

## 3. Battery cost history and reconciliation

Every dollar figure below is read from a rep's own `verdict.json.economics`
block — nothing estimated, per the campaign's standing rule.

| Battery | Reps | $ |
|---|---:|---:|
| Shared SDD round 1 (T1/T2/T5) | 6 of 8 pre-registered (Docker Desktop crash cost reps 4/7) | 26.82 |
| Shared SDD round 2 (T1/T2/T5) | 8 | 24.89 |
| Shared SDD round 3 (T1/T2/T5) | 8 | 33.47 |
| T4 layer 2, Codex ceremony round 1 | 9 | 15.23 |
| T4 layer 2, Codex ceremony round 2 | 7 | 16.87 |
| T4 layer 3, cross-harness matrix | 36 completed and scored (**33 with a cost figure**; 3 unmeasured, see below) | 141.04 |
| T4 layer 4, triggering round 1 | 8 runs (1 blocked codex, 1 invalid-fixture claude, both counted) | 2.27 |
| T4 layer 4, triggering round 2 | 7 valid (1 interrupted codex rep excluded, unmeasured) | 2.02 |
| **Total measured** | **89 reps with a dollar figure** | **262.61** |

**Reconciliation performed for this report, against the log's own ledger
rows (`grep -A6 '\*\*Ledger row'` on the hypothesis log):** summing the
eight ledger-row dollar figures gives 26.82+24.89+33.47+15.23+16.87+141.04+
2.27+2.02 = **262.61**, matching the total stated throughout the cycle
exactly. Summing the corresponding rep counts (6+8+8+9+7+36+8+7) gives
**89**, matching the "89 runs" figure — but that 89 is a count of *reps
that produced a battery record* (completed and scored, whether the rep's
own economics figure is present or not), not a count of reps with a
dollar figure. Two disclosed gaps sit inside the totals above rather than
being additive on top of them:

- **T4 layer 3's 36-rep row is $141.04 for only 33 measured reps.** The
  ledger row itself says so explicitly: "$141.04 (33/36 reps measured; 3
  Claude-spike indeterminate reps have no economics block, unmeasured)."
  Those 3 reps are real, non-zero spend (part of the pre-existing
  Claude+spike investigation-scoping pathology described in §5) that is
  disclosed as unmeasured rather than folded into the total as zero.
- **Round 1's 2 Docker-crash reps (4/7)** and **triggering round 2's 1
  interrupted codex rep** are excluded from both the rep counts and the
  dollar figures above, each disclosed at the point they occurred, not
  backfilled or estimated.

**Also excluded from both the run count and the $262.61 total, and worth
stating plainly rather than leaving implicit:** T4 layer 1's MICRO (75
`claude-opus-4-8` Anthropic Messages API calls, the router-text
differentiation test that gated whether layers 2-4 were allowed to spend at
all) reports no cost — the script captures no token/cost totals and none
were read from the API response at run time, so no figure is
reconstructible after the fact. This is the same limitation the eval
campaign's own E4 MICRO carried.

**Net effect of both gaps:** the true total spend for this fix cycle is
somewhat higher than $262.61 — by an amount that is real but was never
captured for 3 T4-layer-3 reps, 2 Docker-crash reps, 1 interrupted
triggering rep, and the entire 75-call layer-1 micro. None of the five
gaps changes any verdict; all five are the kind of gap this cycle's
standing rule treats as "state honestly, do not estimate," not as a defect
to paper over.

**Attribution:** $85.18 to the shared SDD battery (T1/T2/T5 jointly, three
orthogonal scorers on one battery); $177.43 to T4 (all four layers); $0
dedicated to T3 (it rode the shared battery's 38 reps with no separate
spend). Combined with the prior eval campaign's $153.2, cycle-to-date
spend is ≈$415.81 against the shared $1000 budget line — never near the
$250 checkpoint that would have triggered a stop-and-reassess.

## 4. What was not shipped, and why

**`433184c` — "fix(sdd): prefer non-blocking child-result delivery over
any wait"** (4 lines, `skills/subagent-driven-development/SKILL.md`) was
written during this cycle but landed *after* round 3's battery had already
run and passed. It sat on the arm during T4 layer 2 round 2 and T4 layer 3
incidentally (as arm state those batteries happened to run against), but no
battery's pre-registered criterion was ever written to grade the
non-blocking-delivery preference itself — no T2 clause measures "delivery
without waiting" as distinct from "one long wait instead of many short
ones." The whole-branch review flagged this as finding **I3: an ungraded
commit riding along with graded ones**, and left the drop-or-keep call to
Jesse.

**Jesse ruled: drop it.** `fix/t2-codex-event-waits` and
`fix/t5-codex-spawn-routing` were rebuilt without `433184c` and
force-pushed (`--force-with-lease`; both were unmerged prep branches with
zero PRs open, so nothing was orphaned). Verified four independent ways
(blob-identity, a union-merge diff against the working branch, a `grep -c`
for the dropped sentence, and re-confirming the T5 `codex-tools.md` blob
is unaffected since `433184c` touched only `SKILL.md`) that the branches
now differ from the `codex-efficiency-fixes` working branch by exactly
those four lines and nothing else.

The sentence itself is not lost — it stays on `codex-efficiency-fixes` and
is queued into the parked-findings list below (§5) as a candidate for the
next tightening round, where it can get its own battery before it ships.
**Consequence stated in the T2 PR body:** every line in the T2 diff as
pushed is now text a graded battery actually ran — a stronger claim than
the disclosure it replaced.

## 5. Parked findings — the queue for the next tightening round

A final whole-branch review ran against the full `bb2a34b..70120d5` diff
(all five treatments, the shape they'd take merged onto `dev`) before the
branches were split and pushed. **Verdict: mergeable, no blockers.** Seven
findings were raised and every one was parked rather than fixed inline,
because each edits text a battery already graded — the review's own
recommendation was that any change to graded text get its own
pre-registration and battery, not a same-session patch. This is the
queue, as recorded in the SDD ledger (the fuller review discussion was not
persisted to a standalone file in this workspace, so the label below is
the full record available for each):

- **I1 (Important) — process-scoping vs. the bounded-path definition.**
  Whether "bounded" in the router text is scoped correctly relative to
  process-level (as opposed to code-level) changes.
- **I2 (Important) — classify-before-explore vs. repo-empirical bounded +
  ratchet.** Whether the router asks the model to classify a task before
  or after it has looked at the repo, and how that interacts with the
  "when in doubt, take the heavier one" ratchet rule.
- **M1 (Minor) — spike path has no negative test.** No battery cell
  currently checks that a spike-shaped task does *not* get pulled into
  bounded/architectural ceremony.
- **M2 (Minor) — graph defects.** Unspecified defects in the router's
  decision-flow diagram (`## Three Paths`'s embedded graph), flagged but
  not detailed further in the ledger.
- **M3 (Minor) — single sub-floor wait; "chase" looseness.** Round 3's own
  correction (§6) already surfaced one wait call at 120000ms, below
  `43ec25f`'s stated 300000-600000ms floor; this finding is the reviewer
  independently flagging the same looseness in the wait-discipline
  wording, plus looseness in "chase" (a term used loosely in the
  controller-loop text).
- **M4 (Minor) — SKILL.md controller text is implementer-only.** Some
  controller-loop wording added this cycle reads as addressed to an
  implementer role rather than genuinely harness/role-agnostic.
- **M5 (Minor) — final-review fix subagent uncontracted.** The
  fix-and-re-review wave a `final_reviewer` triggers (observed in 6/8 of
  round 3's reps) has no explicit dispatch contract of its own the way
  task-level review does.

**M6 was reviewed and found correct as shipped** — not parked, no action
needed. Deferred minors beyond these seven are all autoresearch-side
(scorer/tooling nits already listed in the eval campaign's own "known
scorer limitations" section) and do not block anything here. Disclosure
obligations (baselines, caveats, what each PR does and does not prove)
were confirmed present in the T4 and T5 PR bodies during the same review.

**Also carried into this queue, not from the whole-branch review but from
the batteries themselves:**

- **The pre-existing Claude+spike investigation-scoping pathology** (T4
  layer 3, cross-harness matrix, Task 11): of Claude's 6 total
  `cc-ceremony-spike` reps (3 `dev` + 3 `fix`), only 1 passed cleanly. 3
  reps made zero tool calls and answered a Python-stdlib question in
  Node.js/TypeScript/Bun terms instead of reading `server.py`; 2 reps
  investigated the wrong codebase entirely (`/workspace/evals/packages/
  dashboard/src/index.ts`, the eval harness's own source, visible as a
  sibling directory in the mounted tree). Symmetric across `dev` and
  `fix` (dev 0/3 gauntlet-pass, fix 1/3) and explicitly not attributable
  to T4's router-text change — a real, reproducible Claude-specific
  weakness on this exact spike-class story, worth a scenario fix (harden
  the fixture against the harness's own source being visible) before this
  scenario is reused for anything that needs Claude+spike to be a clean
  signal.
- **T4's arch scenario margin (2.4%).** The `quorum_max_time` bump from
  30 to 45 minutes that fixed round 1's scenario-timeout left one round-2
  rep with only ~65 seconds of headroom (43m55s gauntlet duration against
  a 45-minute ceiling) while independently choosing the same
  11-child SDD-subagent path that timed out at the old 30-minute ceiling.
  Recorded as a live risk, not a closed question: a slightly slower
  model or network day could still reproduce the timeout at the new
  ceiling. Flag before any future round reuses `cc-ceremony-arch` without
  re-checking actual rep durations against whatever ceiling is in force.

## 6. Phase 2 queue, restated from the spec

The design spec's own Phase 2 section (baseline-first; not in this
cycle's tasks) listed five items. Restated here with what each one
specifically still needs, since none of the five treatments shipped this
cycle touch them:

1. **Dispatch routing / long-session drift.** Needs a long-session
   elicitation rig — fresh sessions do not reproduce this pathology at
   Codex CLI 0.146 (confirmed repeatedly across this cycle's own
   batteries, none of which ran long enough to elicit it).
2. **Verification leases / evidence receipts.** Needs the
   substring-aware duplicate counter added to `score_e3.py` first; the
   current baseline (1/23 exact-string duplicate pairs in SDD loops) is
   too weak a signal to grade a fix against on its own.
3. **Remediation cap.** The existing baseline is small-n (0,1,2 cycles,
   2/3 reps) and needs more reps before a cap's effect could be measured
   confidently.
4. **Cross-task-race probe redesign.** `score_e5.py`'s current probe is
   inconclusive-by-zero by a design tradeoff in how it's constructed;
   needs a genuinely stronger probe before it can grade anything.
5. **E5 D4 shell-command parser.** The fix-review-scope classifier
   cannot parse compound/chained shell commands, so one baseline label
   in the eval campaign (`repair_scoped`, rep1) is flagged suspect. This
   is scorer engineering work, not a skill change.

**Explicitly out of scope, restated from the spec:** adopting the
externally-authored spinout-stack PRs' text directly (cited as evidence
only, never adopted); RoboRev and Codex token telemetry (separate
codebases); a `close_agent` hygiene checklist (V2 has no such tool —
closed as do-not-ship in the prior campaign); and Claude Code/Gemini-
specific efficiency treatments beyond the T4 cross-harness regression
battery this cycle already ran.

## 7. PR staging state

**Six branches, all pushed to `origin`, based on `origin/dev`
(`bb2a34b`). Zero PRs opened** (`gh pr list --state all --head <branch>`
returns 0 for all six, verified at staging time).

| Branch | Head SHA | Base | Diff |
|---|---|---|---|
| `fix/t1-sdd-no-worker-reviewers` | `7c560e048b85e5bfa4d59a7f71d0bd012d7b834` | `origin/dev` | 5 files, +46/-0 |
| `fix/t3-codex-tools-corrections` | `75756d2900fc17e338f243886ade5998f5a4d78` | `origin/dev` | 1 file, +28/-1 |
| `fix/t2-codex-event-waits` | `d8189d1587ed29cbf7b01ed4138edc8799164898` | `fix/t3-...` | 2 files, +34/-0 over T3 |
| `fix/t5-codex-spawn-routing` | `e9686d5c09b80323bfdc44be8804081e46ea0986` | `fix/t2-...` | 1 file, +19/-0 over T2 |
| `fix/t4-brainstorming-three-paths` | `4dc71b10b325637e8eba673184d4f57eb70ac865` | `origin/dev` | 1 file, +106/-7 |
| `fix/docs-codex-efficiency-campaign` | `6a39375cee878ad5bf062e9cee73774be003469f` | `origin/dev` | 2 files, +1,260/-0 |

**Merge order:** T1 and T4 are independent of everything else. T3 -> T2 ->
T5 is a stack on one file (`codex-tools.md` plus one shared `SKILL.md`
region) and must merge in that order. The docs branch has no code
dependency and cannot conflict (`docs/` only) — it can merge alongside or
after the five treatments.

**The docs branch carries a naming/trust blocker that is not resolved.**
`fix/docs-codex-efficiency-campaign` adds the design spec and
implementation plan, at their final state (all four amendments included),
as the in-tree record of what the five treatment PRs shipped and why.
Two things in those already-committed documents need Jesse's call before
this branch's PR opens — flagged, not edited unilaterally, because they
are reviewed committed content and the fix is a judgment call:

1. **A named contributor with a stated trust judgment.** The spec's
   Sources section reads "[name]'s spinout stack (PRs #2036, #2035) is
   evidence, not adopted text: Jesse does not trust those fixes," with
   the name repeated twice more (Phase 2 queue's item 1, and the Out of
   scope list). Publishing that to `dev` would put a public
   characterization of a named contributor's open work in the tree.
   Suggested rewrite (staged, not applied): drop the name and the trust
   clause, keep "PRs #2036/#2035 are evidence, not adopted text; their
   approach was not adopted (see each treatment PR for the specific
   differences)." Nothing technical is lost.
2. **Machine-specific paths and one internal tool name.** The plan's
   Task 6 section carries two `/Users/jesse/...` absolute host paths and
   several `/tmp/sp-arm-fix` eval-arm references; the spec's out-of-scope
   list names an internal tool (RoboRev). Harmless, but they read as
   leftovers in a document meant for public consumption.

Neither blocks the five treatment PRs, which carry no such content.

**What was not done, stated plainly:** no PRs opened; no pushes to `dev`
or `main` (`origin/dev` still `bb2a34b`, `origin/main` still `44c9b2d` as
of staging); no subagents dispatched during PR staging; no edits made to
committed spec/plan content. Branch pushes only, plus the two
`--force-with-lease` pushes Jesse authorized for the `433184c` drop.

## 8. Process lessons

**1. Three full battery rounds of honest FAIL -> fix -> PASS, on three
separate treatment/layer pairs, each following the same discipline:
pre-register the criterion, run the battery, report the FAIL exactly as
measured, root-cause it, fix, re-run.** Shared SDD battery (T1/T2/T5):
round 1 FAIL/FAIL/FAIL(96%) -> round 2 T1 PASS, T2 FAIL on the
completion-loss clause only, T5 inconclusive-by-zero -> round 3 all three
clean. T4 layer 2 (Codex ceremony): round 1 FAIL (bounded 1/3 strict
approval-gate compliance; arch completion 2/3 on a scenario timeout) ->
round 2 PASS on both (3/3 and 3/3, the arch fix landing with only 2.4%
timing margin — see §5). T4 layer 4 (triggering acceptance): round 1
Claude FAIL 0/3 on the architectural-classification clause (a genuine
cross-harness divergence — the identical router text produced "bounded"
on Claude and "architectural" on Gemini for the same canonical prompt) ->
Task 20's tightened bounded-path wording -> round 2 PASS 3/3 on all three
harnesses. No round's FAIL was smoothed, reworded, or quietly excluded
from a later summary; every FAIL is still readable at its original log
entry, unedited, per the log's append-only rule.

**2. A narrative-overclaim, caught and corrected append-only.** Round 3's
own verdict entries (and `task-8c-report.md`) stated that all 73
`wait_agent` calls that round used `timeout_ms:300000`. A task-reviewer
audit re-derived the true distribution directly from already-committed
data: 55/73 at 300000ms, 7 at 600000ms (rep18), 10 at 360000ms (rep19),
and 1 at 120000ms (rep23) — that last one *below* the fix's own stated
300000-600000ms floor, an undisclosed compliance deviation the original
2-rep manual spot-check happened not to catch. The correction entry is
explicit that no pass/fail verdict or underlying duration/timeout/
completion number was wrong — only the "consistently at the 300000ms
floor" prose claim was — but it is exactly the kind of overclaim that
compounds if left uncorrected, and it was caught by re-deriving from
committed data, not by re-running anything.

**3. Two audit-trail corrections, both about attribution rather than
results.** First: a Task 11 task-review pass found that one of three T4
layer-3 commits (`163ac30`, the score-fix commit) shipped without the
required pre-commit privacy sweep having been run at all — confirmed
clean only after the fact via a post-hoc sweep against the actual commit
diff. The other two commits in that entry had genuinely run the sweep
but never stated so in their own log text; the addendum states plainly
which of the three did which, rather than asserting all three followed
the same procedure. Second: a Task 12b correction found that the
round-2 triggering pre-registration's claim "no refresh performed" (of
the `/tmp/sp-arm-fix` worktree) was accurate about what the implementer
session itself did, but wrong as a claim that no refresh happened at
all — the controller session had moved the arm from `433184c` to
`70120d5` six minutes before dispatch, during a prior task's
bookkeeping. Neither correction changed any battery result; both are
recorded because the standing rule treats a wrong attribution the same
as a wrong number — corrected in a new append-only entry, not edited in
place.

**4. A wrong-checkout incident, caught and repaired without losing
work.** Task 16's implementer committed its wait-discipline paragraph in
the wrong checkout (the `codex/codex-efficiency-audit` branch rather than
the fix branch). The controller cherry-picked the commit onto the correct
fix branch and reset `codex/codex-efficiency-audit` back to its prior
tip (`54f5392`) to undo the stray commit, per the SDD ledger's Task 16
entry. The commit itself (`3da65fb` on the fix branch) is unaffected and
was carried through every subsequent battery round.

**5. Monitor-stall friction persisted across this cycle, unresolved.**
The prior campaign's closeout recorded this as narrative-tier and
uninstrumented: long battery tasks driven through subagents repeatedly
appeared to stall from the coordinator's side while actually progressing.
This cycle's log shows the same friction, now instrumented as a repeated
methodological choice rather than an incident: at least five separate
battery tasks (8, 8b, 9, 9b, 11, 12b) explicitly record that no `Monitor`
tool call was made, and that the coordinator instead polled in-session via
repeated foreground `kill -0`/`sleep 30` loops or bounded `until <condition>`
shell loops against a written sentinel file. This kept every battery's
actual progress directly visible turn-by-turn, at the cost of coordinator
attention spent re-polling rather than working other tasks while long
batteries ran. Still un-re-observed as a target for fixing (same
recommendation as the prior campaign's closeout): whether a `Monitor`-based
wait would reduce that cost without reintroducing the "no output for a
long stretch reads as stalled" problem the prior campaign flagged is an
open question, not answered by this cycle either.

## 9. Sources

Every number above is traceable to one of: this repo's
`logs/2026-07-30-codex-efficiency-fixes.md` (the primary, append-only
record — its own `**Ledger row:**` entries were re-summed for §3 rather
than trusted from a secondary summary); the SDD ledger
(`.superpowers/sdd/2026-07-30-codex-efficiency-fixes/progress.md`) in the
superpowers worktree; `pr-summary-for-jesse.md` and `task-13-report.md` in
the same SDD directory (branch/SHA verification, PR staging detail); and
the design spec (`docs/superpowers/specs/2026-07-30-codex-efficiency-
fixes-design.md`, Phase 2 queue and Out of scope sections, quoted
verbatim in §6). Nothing in this report is estimated or reconstructed;
where a figure genuinely does not exist (the layer-1 micro's cost, the
Docker-crash reps, the interrupted triggering rep, the 3 unmeasured T4
layer-3 reps), this report says so rather than guessing.
