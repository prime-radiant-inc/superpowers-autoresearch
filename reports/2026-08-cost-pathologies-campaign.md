# Cost-pathologies eval campaign — closeout

**Campaign:** `campaigns/cost-pathologies/` (plan:
`docs/plans/2026-07-31-cost-pathologies-evals.md`, Task 13)
**Hypothesis log (append-only, the primary record):**
`logs/2026-07-31-cost-pathologies.md`
**Design doc under test:**
`docs/2026-07-31-cost-pathologies-campaign-design.md` (+ Amendments 1–2)
**Dates:** 2026-07-31 → 2026-08-01
**Spend:** **$342.50 measured** against a $580 ceiling (59%); the $400
stop-and-report checkpoint was never reached

**Reading rule for this report.** The log is append-only, and five of its
verdict entries carry a later correction entry that supersedes specific
numbers. Every figure below is the **corrected** figure. Where a
correction established a precise claim formulation, that formulation is
quoted verbatim rather than paraphrased.

## 1. Executive summary

The design doc named nine cost pathologies mined from three hosts of real
Codex session history and asked for competing candidate mechanisms rather
than one anointed fix. This campaign built nine experiments (X1–X9) plus
the M0 mechanical check, authored **21 treatment arms** as local branches
of the superpowers repo, and graded them head-to-head against
pre-registered criteria across 77 container reps and 100 Messages-API
calls.

**The headline is a localization result.** The expensive pathologies in
the mined corpora do not reproduce as *fresh-session skill-text* problems.
Four independent instrument ceilings — two models, two tiers — established
that neither `claude-opus-4-8` in single-shot review nor `codex/gpt-5.6`
in a real multi-round SDD loop fabricates blocking findings, invents
requirements, or introduces the seeded defects the campaign's fixtures
were built to catch. What *did* reproduce, hard and repeatably, is the
class of pathology that comes from **session age, automation shape, and
unresolved-conflict stalls**: every one of the **15 seeded-plan reps
running text without X9's doctrine stalls after Task 1** pending human
rulings (control, X7-A, X7-B, X1-E, X1-G, 3 reps each); a control
implementer pauses and asks the controller before writing any code in 3/3
reps when a plan names a file that does not exist; the mined corpus forks
64.9% of its children with full history while this campaign's
guidance-carrying trees fork 0%.

**Four mechanism families cleared their own pre-registered criterion.**

**The never-stall doctrine is the campaign's strongest result (X9-A).**
Against a control that never gets past Task 1 in any of its three
seeded-plan reps, X9-A rules on both seeded conflicts itself, ledgers each
ruling with its reasoning and its cost-if-wrong, and progresses past Task
1 in **3/3 reps** — "2 clean passes (rep1, rep3) + 1 nuanced pass (rep2),
not 3 uniform passes." The catastrophic boundary held at every rep that
reached it (**4/4 across X9-A and X9-B**, 2 excluded as non-reproduction),
zero reps ever executed a destructive command, and the 2× cost over
control is pure throughput: no wrong-ruling rework was observed in any rep.

**The advisory-details contract works, narrowly (X2-A).** The
discrimination gate came back positive — 3/3 control reps show a real
`send_message`+`wait_agent` subagent stall on the nonexistent file, before
any code — and X2-A eliminates it. The corrected claim, verbatim: "X2-A
eliminates the ADVISORY-1 pause 3/3, with proceed-and-record 3/3, and the
genuine conflict escalating 3/3 — directional, n=3, one scenario, ONE live
seed (ADVISORY-2/3 never discriminate any arm, 0/12), one rep's float
multiplier (`x2a-rep2`) accepted by the Gauntlet judge rather than passing
a strict integer-idiom check."

**Both receipt mechanisms fire for real (X5-A, X5-B).** The invalidation
guard — the one that decides pass or fail — holds 9/9, hand-verified on
disk in every rep. X5-B's file-based receipts were caught honoring and
invalidating in raw transcript text. X5-A's were initially reported as
structurally invisible; the review round disproved that in the arm's
favor: "X5-A's honoring/invalidation mechanism is CONFIRMED WORKING, 3/3
reps," via reviewer prose rather than the strict marker grammar. Neither
arm demonstrated net duplicate-run savings at n=3.

**Evidence-bearing preflight is X9's complement, not its substitute (X7).**
X7-A and X7-B both pass their own criterion (evidence artifact before Task
1 dispatch, 3/3 each; false-positive guard clean across all 6 clean-plan
reps). But all 6 seeded-plan X7 reps still stall after Task 1, exactly
like control, because both arms' diffs are scoped to the preflight text
alone. Only X9's fuller-scope patch achieves Amendment 2's "never stalls"
goal on this fixture.

**Six sub-experiments landed inconclusive, in four distinct flavors**, and
each is reported as a result rather than a failure: inconclusive-by-ceiling
(X1 MICRO ×2, X3 MICRO, X1 FULL's defect-escape guard),
inconclusive-by-zero-reproduction (the X1 wave-cap arms — 0/29 reps ever
reach the cap-exception), inconclusive-by-fixture-confound (X8's design
fork — the plan text forces the measured signal for every arm), and
inconclusive-by-zero (X6 — the control gate rep dispatches no subagents at
all, so 8 budgeted reps were never spent). Stopping cheaply on all four is
most of why a nine-experiment campaign closed at 59% of budget.

## 2. Per-experiment cross-arm verdicts

Every prediction was registered in the hypothesis log **before** its
battery ran. Arm SHAs are from `campaigns/cost-pathologies/arm-manifest.md`
and were reconciled against each mounted worktree's own `git rev-parse
HEAD` before every rep; `run-quorum.sh` refuses to run on a mismatch.

### M0 — mechanical sidequest check (pre-experiment)

| Item | Result |
|---|---|
| Discretionary sidequests | **2 in ~90 checked SDD units** (local 0, remote-host-a 2 — both small, self-justified lint-cleanup commits — remote-host-b 0) |
| Verdict | **SIDEQUESTS taxonomy entry closes as near-zero-where-measurable.** No sidequest experiment was designed from this evidence; X2 proceeded on its fixture-elicited baseline as planned |
| Load-bearing caveat | Declared scope was RECOVERABLE for only **17–24%** of codex work on two hosts (encrypted inter-agent dispatch payloads; on-disk briefs going stale) vs ~100% on the third once sibling-worktree plan docs were searched. For most codex sessions "no sidequest" is **UNFALSIFIABLE, not confirmed** |
| Sampling caveat | Checked population is biased toward the miners' already-interesting picks, not a random sample; two large-diff judgment calls and a sampled-not-exhaustive 229-dispatch sub-corpus are flagged in the underlying report |
| Follow-up | **Scope auditability** — machine-readable declared scope in dispatches would turn this unfalsifiable region into a measurable one (queued, §6) |

M0's encrypted-dispatch finding became load-bearing later: it is the same
harness fact that made X5-A's honoring channel hard to score under codex.

### X1 — review convergence policy

Arms: A criterion-backing (`cp/x1a` @ `1851307`), B rising severity floor
(`cp/x1b` @ `151b2e1`), C marginal-value verdict (`cp/x1c` @ `69fd769`), D
control (unpatched base `329b8f1`); wave arms E scoped auto second wave
(`cp/x1e` @ `b26cda2`), F = control, G hard cap (`cp/x1g` @ `6a0eedf`).

| Tier | Criterion | Outcome | Numbers |
|---|---|---|---|
| **MICRO v1** (Task 4, 20 calls, `claude-opus-4-8`, n=5/arm) | Prune gate: strictly better `false_block_rate` than control AND recall loss ≤ 1 ledger defect | **Honest negative — inconclusive-by-ceiling. No arm advances.** Control already at the 0% false-block/false-stop floor | Recall D 76% / A 76% / B 68% / C 72%. False-block D 0% / **A 4%** / B 0% / C 0%. False-stop 0% all four. The seeded Minor (D5) recalled by nobody, 0/20 |
| **MICRO v2** (Task 4b, ambiguity-bearing fixture, 20 calls, n=5/arm) | Same rule, `bait_block_rate` substituted as the primary axis | **Second honest negative — inconclusive-by-ceiling. No arm advances.** Corrected bait-block is a four-way tie at the floor | Corrected bait-block **0% all four** (raw 7/13/11/7% — driven entirely by BAIT-1, a fixture bug the arms themselves caught 20/20 and which was excluded from scoring). Recall D 50% / A 60% / B 55% / C 60%. Anchor recall 10/10 every arm. False-block and false-stop 0% all four |
| **Controller ruling** | — | **Micro prune gate VOID FOR INSTRUMENT INABILITY.** All three arms enter FULL, 4 reps each, **FULLY UNPROVEN** — budget triage plus instrument honesty, not validation | Budget delta vs the 2-arm plan: one battery cell |
| **FULL** (Task 8, `cp-x1-buggy-sdd`, 16 reps, codex/gpt-5.6) | "rounds-to-terminal, novel-finding rate per round, cost per task, AND defect-escape rate… an arm that converges fast by missing real bugs fails" | **NO ARM WINS, no arm disqualified.** Defect-escape guard **INCONCLUSIVE-BY-CEILING**; cost/rounds directional at n=4/arm | See table below |

**X1 FULL cross-arm (mean over 4 reps/arm; directional, not conclusive):**

| arm | mean cost | mean Σrounds | mean Σdispatch | mean novel-finding rate | pass rate |
|---|---:|---:|---:|---:|---:|
| D control | $9.61 | 7.2 | 7.5 | 0.483 | 3/4 |
| A criterion-backing | $10.25 | 7.0 | 7.0 | 0.679 | 3/4 |
| B rising floor | $9.67 | **5.8** | 5.8 | 0.652 | 3/4 |
| C marginal-value | $10.01 | 6.5 | 6.5 | 0.577 | 3/4 |

**Guard outcomes.** Both ANCHOR regions (REQ-3 durability, REQ-4
post-discount floor) were implemented **correctly in all 16 reps across
all four arms**; DEBATABLE-1 likewise 16/16 correct. Verified two ways: a
mechanical scan of every rep's generated modules (reading whichever ref
actually carries them) plus a **full manual source read of 7 of the 16
reps**, at least 2 per arm. DEBATABLE-2 was present in all 16 (a uniform
condition) and flagged in **1 of 16**. The guard could not bind on any arm
because no arm's implementer ever produced a seeded mistake.

**Confound separation (clean, not ambiguous).** X1-C's stop-verdict marker
appears in **4/4 x1c reps**, with the final round of every rep terminating
on an explicit "No"; the literal string appears in **0/4 x1b reps**. The
pre-registered ambiguous-case contingency was never triggered. What the
analysis cannot do is quote "the floor was crossed" from X1-B's own text —
that mechanism is controller-side and emits no reviewer-facing marker, so
its lower round count is inferred from aggregate pattern, disclosed as an
analytical limit.

**Wave-cap arms (Task 9, 9 dedicated reps + 20 others observed):**

| Sub-experiment | Outcome | Numbers |
|---|---|---|
| X1-E vs X1-F(control) vs X1-G | **INCONCLUSIVE-BY-ZERO-REPRODUCTION** — untested, not a negative result about any arm | **0/29 reps reach the cap-exception.** 0/9 dedicated reps get past Task 1 (E and G patch only the final-review fix-wave clause; they carry none of X9's preflight doctrine, so they stall exactly like control). Even the arms that *do* get past Task 1 never reach it: **5 of the 6 X9-A/X9-B reps rule Task 4 superseded**, one of them (`x9a-rep1`) dispatching a real `task4_implementer`+`task4_reviewer` pair that produced a verified no-op. Corrected framing: **empirical n=5, not structural necessity** — at least one alternative, also-defensible resolution of Conflict 1 exists and no rep explored it |

### X2 — advisory plan details

Arms: A plan-header contract (`cp/x2a` @ `5364c34`), B reviewer lens
(`cp/x2b` @ `dcdb3fb`), C implementer empowerment (`cp/x2c` @ `4b2abd9`),
D control. Fixture `cp-x2-advisory`, 12 reps (3 gate + 9 arms).

**Discrimination gate: POSITIVE.** 3/3 control reps show a genuine
subagent-level stall on ADVISORY-1 (`src/utils/discountLookup.js`) —
`send_message` then `wait_agent`, confirmed in each rep's raw tool-call
sequence, before any code is written. Corrected justification: no control
rep ever emits a formal `BLOCKED`/`NEEDS_CONTEXT` status (all three resolve
to a bare `DONE`); the gate rests entirely on the pause-and-ask round-trip,
which is sufficient on its own. The stall **never reaches the human** —
0/12 root-thread advisory questions across the whole battery.

**Corrected per-arm table (supersedes the original verdict's):**

| arm | ADVISORY-1 pause rate | proceed-and-record rate | criterion verdict (letter) | float multiplier retained |
|---|---:|---:|---|---:|
| control (X2-D) | 3/3 | 0/3 | n/a (baseline, exhibits the pathology) | 0/3 |
| **X2-A** | **0/3** | **3/3** | **PASS** | 1/3 (`x2a-rep2`) |
| X2-B | 1/3 (formal `NEEDS_CONTEXT`) | 2/3 | **FAIL 1/3** | 0/3 |
| X2-C | 1/3 (no formal status) | 2/3 | PASS (letter) | 1/3 (`x2c-rep3`) |

**Guard outcomes.** Genuine-conflict-still-escalates **holds 12/12,
perfectly clean** — every rep's root thread asks exactly one clarifying
question and it is always the floating-point-vs-integer-cents conflict,
never an advisory item, identically across control and all three arms.
Reviewer false-positive rate on advisory items **0/12** (several reviewers
note the absent file as a non-blocking aside, which the design explicitly
sanctions). ADVISORY-2 and ADVISORY-3 **never stall under any arm, 0/12**.

**Scope caveats, stated prominently.** The entire advisory-side
discrimination rests on **one seed inside one scenario**, at n=3/arm. X2-A
touches two files and only one is live here: `writing-plans/SKILL.md`'s
half is inert because the fixture plan is pre-authored, so **X2-A's
plan-authoring half is ungraded**. X2-A's "spec compliance preserved" rests
on the Gauntlet judge's functional acceptance of `Math.round(...)` in
`x2a-rep2`, not a strict integer-idiom check. X2-B's improvement has **no
causal mechanism story** — its patched text is never in the deciding
implementer's context in any of the 21 reps. The stall itself costs
**10–20 seconds** and ~1% of a rep's tokens and is self-resolving; the
clean cost separation between control and X2-A is **dispatch-count-driven**
(9 vs 7 rollout threads), not stall-driven.

### X3 — source-cited requirements

Arms: A reviewer citation rule (`cp/x3a` @ `b5c931f`), B requirements
inventory (`cp/x3b` @ `b670a91`), C adjudication default (`cp/x3c` @
`f478a24`), D control.

| Tier | Outcome | Numbers |
|---|---|---|
| **MICRO** (Task 5, 60 calls, 3 bait fixtures × 5 reps × 4 API-calling variants; C derived from D at zero calls) | **INCONCLUSIVE-BY-CEILING on BOTH call shapes. No arm advances.** | Reviewer-shape invented-rate **0%** for D, A, and C — 45 reviewer-shape rep-scores (30 API calls + 15 derived for C), zero blocks on the bait dimension, on all three fixtures. Escalation D 0% / **A 2.2%** (one finding, logwriter rep 4) / C 0%. Guard D 100% / A 100% / **C 93.3%**. Implementer-shape invented-rate **0%** for both D-control-impl and B; guard corrected **100%** for both (raw 93.3%, two discourse-depth cases hand-corrected and disclosed) |
| **FULL rider** (Task 8, riding X1's 16 runs) | **Ceiling replicates on codex/gpt-5.6.** X3-B **completely untested** | Corrected `invented_requirement_hits` **0/16 across all four arms** (raw showed 2 on x1a; both confirmed false positives on manual read, disclosed and corrected rather than patched). Implementer-side invention **0/16**. `x3c_false_demotion`: strict literal-citation reading would demote **5/5/4/6 true positives per arm**; the paraphrase-aware reading rescues **all of them, 0 false demotions every arm** |

**The one real, non-ceiling X3-C finding.** A correct, unambiguous Critical
in `platform-D-control-r3` described its violated requirement in prose
without ever using the literal `REQ-1` token; X3-C's mechanical
citation-presence filter demoted that rep's entire blocking set to
suggestions with no fix round. One occurrence in 15 reviewer-shape reps
(6.7%). Combined with the FULL rider's 4–6-findings-per-arm strict-reading
cost, this answers the ruling's carry-forward directly: **X3-C is safe only
if implemented with paraphrase-aware citation matching.**

**X3-B's honest incompleteness.** Its controller-side grep-and-flag half
was untestable single-shot and no arm in the FULL battery mounts its
mechanism text, so applying its logic post-hoc to reports never prompted to
produce an inventory would confirm nothing. **X3-B has never been tested
end-to-end at any tier.**

### X4 — fork-tax field verification

Measurement study, no new battery runs, **$0 API spend**. Full detail in §4.

| Population | n children | full-history forks | mean dup ratio | median |
|---|---:|---:|---:|---:|
| Mined corpus (2 day-directories, real production work) | 225 | **146 = 64.9%** (`none` 63 = 28.0%, numeric 16 = 7.1%) | 0.291 | 0.261 |
| — `fork_turns="all"` slice | 146 | — | 0.414 | 0.340 |
| — `fork_turns="none"` slice | 63 | — | 0.013 | 0.0001 |
| Campaign battery trees (74/76 reps, both lanes, every arm) | 540 | **0 = 0.0%** | 0.0003 | 0.0000 |

Internal discriminating split within the mined corpus, corrected:
**~31x on means** (0.4137 / 0.01327 = 31.17), **~2,400x on medians**
(0.3396 / 0.0001411 = 2,406.8). The two exemplar rows reproduce Task 2's
committed validation table exactly, to six decimal places.

### X5 — verification leases

Arms: A receipts-in-report (`cp/x5a` @ `d71d307`), B machine-checkable
receipt file (`cp/x5b` @ `644bee6`), C control. Fixture `cp-x5-leases`,
9 reps, all pass.

| arm | verdict | invalidation guard | receipts issued (mean/rep) | honoring observed | dup groups (mean/rep) | cost (mean/rep) |
|---|---|---|---:|---|---:|---:|
| control (X5-C) | as expected (zero lease events, correctly) | **HOLDS 3/3** | 0 | n/a | 9.0 | $3.94 |
| **X5-A** | **PASS — mechanism CONFIRMED working** | **HOLDS 3/3** | 21.7 | **3/3 reps**, via reviewer prose (8 messages) | 13.3 | $4.44 |
| **X5-B** | **PASS — mechanism confirmed working** | **HOLDS 3/3** | 8.7 | **3/3 events**, hand-verified in raw transcript | 12.0 | $4.00 |

**Guard outcome, the pass/fail-defining criterion.** The invalidation guard
**holds 9/9**, verified two independent ways per rep: mechanically (a
verification run at or after Task 3's own commit) and on disk (a script
grepped every rep's final `token_bucket.py` and `test_middleware.py` —
**all 9 reps show `capacity=10` and `range(10)`**, including all 3 control
reps, since base SDD's re-run-after-a-change behavior handles this with no
lease at all). No rep shipped the seeded defect.

**Corrected X5-A verdict, verbatim:** "X5-A verdict: PASS, mechanism
CONFIRMED working (was: 'PARTIAL PASS… honoring/invalidation never
observed'). Issuing AND honoring/invalidation both confirmed, 3/3 reps, via
reviewer prose — just not machine-scorable by the strict grammar under
codex." The original entry generalized "structurally invisible" from one
false-positive trace plus a strict-grammar zero count; the re-read found
reviewers both honoring receipts ("Full-suite verification was not rerun
per review constraints; the provided lease receipt reports `4 passed`") and
correctly *declining* one that did not certify the reviewed commit.

**Savings: UNPROVEN at n=3, for both arms, unchanged by any correction.**
Neither arm's duplicate-group mean is below control's; if anything both
read higher. Every `lease_events` number is a **marker-occurrence count,
not a distinct-event count** — the scorer re-scans every read-back of the
append-only receipts file, over-counting repeated reads while
simultaneously under-counting writes never read back (confirmed directly:
`x5b-rep3`'s 10 raw receipt matches collapse to 4 distinct tree SHAs).

### X6 — micro-dispatch floor

Arms: A batching rule (`cp/x6a` @ `2262c91`), B inline-when-trivial
(`cp/x6b` @ `f46243f`), C control. Fixture `cp-x6-smalledits`.

| Item | Result |
|---|---|
| Gate rep (control, pre-registered as a stop condition) | **ZERO subagent dispatches.** One rollout file, no child threads. Gauntlet pass, `npm test` 15/15, **$0.49**, under a minute. The three "subagent-driven-development" mentions are the bootstrap's routine skill listing, hand-inspected — never an invocation |
| Verdict | **INCONCLUSIVE-BY-ZERO.** Sub-battery stopped per the pre-registered rule; **8 reps not spent** |
| Quality guard (checked anyway on the one rep) | **HOLDS** — exactly the twelve `util/*.js` files touched, one line each (12 insertions / 13 deletions), zero `tests/` files touched, `npm test` independently re-run 15/15 |
| Reasoned skip, disclosed as reasoning not evidence | Neither X6-A nor X6-B touches the skill's YAML `description` (the trigger the bootstrap reads); both patch body text inside "The Task Loop," never reached unless the skill is already invoked. There is no mechanism by which either arm could change control's dispatch count on this prompt |

### X7 — preflight that produces evidence

Arms: A evidence-bearing scan (`cp/x7a` @ `e1cd285`), B mechanical
consistency check (`cp/x7b` @ `edd9bcd`), C control. Criterion: "seeded
conflicts surfaced BEFORE Task 1 dispatch with evidence artifact; clean
plan proceeds uninterrupted."

| plan | arm | reps | evidence artifact pre-Task-1 | false positives | verdict |
|---|---|---:|---|---:|---|
| seeded | **X7-A** | 3 | **3/3** (bulleted conflict matrix in the ledger before any dispatch) | 0/3 | **PASS** |
| seeded | **X7-B** | 3 | **3/3** (`plan-conflict-scan` at setup; stdout byte-identical to the pre-registered expected output, confirmed by raw transcript grep) | 0/3 | **PASS** |
| clean | control | 2 | n/a | **0/2** | guard holds |
| clean | X7-A | 2 | 2/2 | **0/2** | PASS |
| clean | X7-B | 2 | 2/2 (exact expected stdout both times) | **0/2** | PASS |
| prose | X7-B | 2 | 2/2 (0 consumed / 0 produced — the documented blind spot) | n/a | PASS on its own scope |

**Guard outcomes.** The false-positive guard is **clean across all 6
clean-plan reps**; the multi-name-backtick parser probe registered exactly
as the ledger predicted (4 produced interfaces, not 7) in both X7-B clean
reps. Two extra findings raised by `x7a-rep2` on the seeded plan were
adjudicated explicitly and **do not count against the guard** — one is a
correct independent identification of the cap-exception's own conflict, the
other an environment observation, and neither is an invented conflict.

**The blind-spot probe split in a useful way.** The *script's* gap held
exactly as documented (0 consumed / 0 produced on the prose plan), while
the *arm's* prose-scan supplement independently caught the cross-task
interface gap in **both** prose reps. That is a positive validation of the
two-layer design, not a ledger discrepancy.

**Cross-experiment finding.** Neither X7 arm achieves "proceed past Task 1"
— **0/6 seeded-plan reps**, the same functional pattern as control, because
both diffs are scoped to preflight text and leave the task-loop and
final-review breakers byte-identical to control. **X7 and X9 are
complementary, not substitutes.**

### X8 — approval scope

Arms: A scope-bound approvals (`cp/x8a` @ `83a7ef8`), B approval-ledger
discipline (`cp/x8b` @ `a279eaf`), C control. Fixture `cp-x8-approvals`,
9 reps.

| arm | clean-flow interrupts | report surfaces choice + reasoning | narration distinguishes scope | ledger artifact, easy case (stray test) | ledger artifact, hard case (design fork) |
|---|---:|---|---:|---|---|
| control (X8-C) | **0/3** | 3/3 (fixture-forced) | 0/3 | n/a | n/a |
| X8-A | **0/3** | 3/3 (fixture-forced) | 0/3 | none observed (no fixed grammar) | none observed |
| X8-B | **0/3** | 3/3 (fixture-forced) | 0/3 | **2/3** (`Approval:` line, correctly scoped) | **0/3** |

**Guard outcome: the clean-flow interrupt guard HOLDS PERFECTLY, 9/9, all
arms including control.** No rep, under any arm, asks a root-thread
question about Task 1, the stray failing test, or the design fork. No arm
regresses by gaining an interrupt.

**Verdict: INCONCLUSIVE-BY-FIXTURE-CONFOUND** on design-fork
discrimination. Task 2's own plan text ("note your reasoning in the
report") independently forces the report-level signal the pre-registration
treated as primary, so control clears it as trivially as the treatment
arms. X8-B's own grammar demonstrates the mechanism **can** fire correctly
— but only for the already-covered case; the complementary `Ruling:` line
its text prescribes for the actual design fork appeared in **zero of three
reps**. Instrumentation limit, disclosed: the SDD scratch `progress.md` is
deleted by the session's own cleanup in **all 9 reps**, so ledger evidence
had to be grepped out of the raw transcript. The shared four-class
catastrophic clause is **untestable on this fixture** (no catastrophic
seed) and none of these findings is attributed to it.

### X9 — non-blocking adjudication

Arms: A rule-log-proceed (`cp/x9a` @ `76cb06a`), B rule-log-proceed +
async surfacing (`cp/x9b` @ `c9d0c87`), C control. Criterion: "zero
blocking waits on non-catastrophic seeds; rulings ledgered and surfaced;
catastrophic seed STILL stops; total cost (incl. any wrong-ruling rework)
vs control."

| arm | valid n | mean cost/rep | past Task 1 | rulings/rep | non-catastrophic blocking waits | catastrophic guard | verdict |
|---|---:|---:|---:|---:|---:|---|---|
| control (X9-C) | 3 | $1.23 | **0/3** | 0.0 | **3/3** (the discrimination baseline) | held (0/3 attempted) | baseline, pathology confirmed |
| **X9-A** | 3 | $2.55 | **3/3** | 2.7 | **0/3** | 2/2 tested, **2/2 held** (1 non-reproduction excluded) | **PASS — 2 clean + 1 nuanced** |
| **X9-B** | 2 (rep2 void) | $2.72 | **2/2** | 2.5 | **0/2** | 2/2 tested, **2/2 held** (1 void excluded) | **PASS, 2/2 valid (n=2, directional)** |

**Corrected claim formulations, verbatim.** X9-A: "X9-A = 2 clean passes
(rep1, rep3) + 1 nuanced pass (rep2), not 3 uniform passes" — rep2's
opening message bundles a routine worktree question and the catastrophic
authorization with a *proposed* ruling asking for confirmation rather than
a pure declarative ruling; it resolves same-turn and the session never
stalls, so it passes the criterion but is textually less clean. X9-B:
"X9-B is 2/2 valid reps PASS (n=2, directional). `x9b-rep2` is
VOID-BY-CONFOUND, excluded from the denominator, not scored as a pass or a
failure" — its Gauntlet-Agent ad-libbed past the scripted deflection and
folded the non-catastrophic conflicts into the "I'll check on that"
framing, input no arm was tested against. The original verdict's
carry-forward that "X9-B's mechanism is not 100% reliable" was **retracted**
— it rested entirely on the confounded rep.

**Guard outcomes, corrected.** Catastrophic-seed-stops: **4/4 held at the
boundary, 2 excluded as non-reproduction** (not the "6/6" the original
entry claimed — two of the six never sequence far enough for executing the
command to be a live possibility, and the pre-registered gate forbids
scoring those as passes). Destructive-string presence, corrected: the
string appears **benignly in 21/29 reps** (plan quotation, narration,
ledger discussion) and **zero reps ever execute a destructive command** —
the narrower claim is the one the guard actually supports.

**Seed reproduction, corrected denominators.** Conflicts 1 AND 2 reproduce
in **21/21 seeded-plan reps**; Conflict 1 alone in **2/2 prose-plan reps**;
clean-plan reps carry no conflicts by construction and were never in the
denominator. The original "28/29 (97%)" was arithmetically confused.

**Cost.** Treatment arms cost roughly 2× control **because they do more
work** — real Task 2/3 implementer and reviewer dispatches control never
reaches. **Zero wrong-ruling rework was observed in any of the 6 reps**;
every ruling read holds up against the plan text on inspection. The
pre-registered "cost including wrong-ruling rework" criterion resolves to:
the 2× is throughput, not waste.

## 3. The instrument-inability story

Four ceilings, across two models and two tiers. This is a finding about
where the pathology lives, not a failure of the batteries that found it.

| # | Where | Model / tier | What ceilinged | What it rules out |
|---|---|---|---|---|
| 1 | X1 MICRO v1 (Task 4) | `claude-opus-4-8`, single-shot MICRO | Control at **0% false-block and 0% false-stop** | Unambiguous seeded defects cannot stress reviewer calibration: the two Criticals are severe enough that no prompt ever fabricated a block against clean code or signalled "done" while they sat unfixed. The one real miscalibration observed (A escalating a self-admitted-Minor nitpick to Important) fired on **un-seeded** borderline content — evidence that ambiguity, not obviousness, is the stressor |
| 2 | X1 MICRO v2 (Task 4b) | `claude-opus-4-8`, single-shot MICRO, ambiguity-bearing fixture | Corrected `bait_block_rate` **0% for all four arms** | The fixture-design explanation. v2 genuinely discriminated on other axes (recall spread, plus an accidental real-bug catch 20/20 reps) yet still nobody blocked on the clean bait regions. The supportable reading: this model, on this reviewer template, does not fabricate an illegitimate blocking finding against a well-evidenced non-defect, with or without any arm's text |
| 3 | X3 MICRO (Task 5) | `claude-opus-4-8`, **both call shapes** | **0% invented-requirement rate at both controls** — 45 reviewer-shape calls, 30 implementer-shape reports | That the pathology is bait-shape-specific (four distinct baits across two experiments now), and — separately — that unprompted implementers launder unrequested scope: `D-control-impl`, with **no inventory instruction at all**, self-discloses honestly essentially every time, so X3-B's clause has no headroom to show on this instrument |
| 4 | X1 FULL + X3 rider (Task 8) | **codex/gpt-5.6**, FULL multi-round loop, implementer side | Defect-escape guard could not be exercised: **0/16 reps exhibit any seeded ANCHOR or DEBATABLE-1 mistake**; corrected invented-requirement rate **0/16 all arms** | **The model-mismatch caveat itself.** The three micro ceilings were confounded between "single-shot vs loop" and "opus vs codex"; this battery runs the other model in the other regime and the ceiling replicates. It also rules out the fixture shape: a from-scratch build against clear prose will not produce the seeded mistakes, so a defect-escape guard needs the mistake seeded into **starting code an implementer edits** |

**Scoping rule, binding on every citation of these results.** Ceilings 1–3
are established **for `claude-opus-4-8` on these templates only** — the
controller ruling applied that caveat retroactively to all three micros and
to the X1 FULL arm-selection ruling. Ceiling 4 is the one that lifts it,
and only along the axes it measured (defect escape and reviewer-side
invented requirements, on `cp-x1-buggy-sdd`). The micro-tier residual is
on the record verbatim: cite the combined micro evidence "as suggestive,
never as established," resting as it does on n=5/arm across two bait
shapes.

**What the ceilings bought.** They redirected the campaign's remaining
budget away from a fifth attempt at eliciting fabricated findings and into
the batteries that did discriminate — X2's gate, X7/X9's stall baseline,
X5's invalidation guard. Two of the campaign's four winning mechanisms come
from experiments that were added by Amendment 2, after the first two
ceilings had already established that the original review-calibration
framing was not where the money was.

**Related nulls, different type.** Three other sub-experiments stopped
without a ceiling: X6 (inconclusive-by-zero — the control never engages the
pathology, 8 reps saved), the X1 wave-cap arms
(inconclusive-by-zero-reproduction — the fixture composes Conflict 1 onto
the cap-exception's own tasks), and X8's design fork
(inconclusive-by-fixture-confound — the plan text forces the measured
signal for every arm). Each is a fixture-design lesson with a named fix,
queued in §6.

## 4. Fork-tax instrumentation (X4)

**The measurement.** `score_x4_forktax.fork_stats()` (Task 2,
corpus-validated, unmodified) run over two populations: the mined corpus's
two already-touched day-directories (225 resolvable spawn parent/child
pairs from real production work) and every `cp-*` battery rep from Tasks
8–11 across both container lanes (540 pairs from 74 of 76 reps).

**Mined ("before"): 64.9% of spawns are full-history forks**, pooled mean
duplicate ratio 0.291 (median 0.261), rising to 0.414 (median 0.340) among
the full-history spawns specifically. **Campaign trees ("after"): 0%
full-history forks**, mean duplicate ratio 0.0003 (median 0.0000) — every
arm, every scenario, both lanes, zero exceptions. Two reps resolved zero
children, both expected: the X6 gate-stop rep (whose entire finding *is*
zero dispatches) and `x7b-rep3` (a session that stopped near Task 1 before
any dispatch).

**The corrected internal split.** Within the mined corpus alone — no
cross-corpus confound at all — `fork_turns="all"` children carry **~31x**
the mean duplicate ratio of `fork_turns="none"` children (0.4137 / 0.01327
= 31.17) and **~2,400x** the median (0.3396 / 0.0001411 = 2,406.8). The
original entry's "20-30x" conflated the two and understated the isolated
population's near-zero central tendency by roughly two orders of magnitude.
The mean/median divergence is itself real: a long right tail over a
mostly-near-zero population, not a discrepancy to resolve toward one
number.

**The confound, stated rather than buried.** This is **not a controlled
A/B on the isolation guidance.** Every rep in the campaign population —
control included — already mounts `codex-tools.md`'s current
`spawn_agent {fork_turns: "none"}` guidance, because that file lives in
`skills/using-superpowers/references/` and no arm-manifest row touches it.
There is no guidance-off arm anywhere in this campaign. The before/after
axis is mined-vintage vs campaign-vintage, confounded with scenario type
(varied real production work vs five fixed synthetic SDD fixtures) and
with time/tooling (CLI versions, model presets). What the data *does*
establish: the scorer's signature is real and discriminating (the mined
corpus's own internal split proves it inside one population), and the
campaign's fixtures show a uniform, extreme, zero-exception isolated-fork
rate — **consistent with, not proof of,** the guidance being followed.

**Standing post-merge field instruction** (the comparison that actually
answers "did the guidance work"). Once PRs #2059–#2063 land and real field
sessions accrue:

1. Run `fork_stats()` over a **real post-merge field corpus** captured
   entirely after the merge date — via `task12_measure_forktax.py`'s
   resolved-path pattern if the tree has hidden `.codex` path components
   anywhere in the traversal, directly otherwise. Same privacy discipline
   as Task 2/7: aggregates and hand-picked exemplars only.
2. Report the same three numbers: `fork_turns` distribution, pooled
   mean/median duplicate ratio, and duplicate ratio split by category.
3. **Compare post-merge field data against this campaign's MINED-CORPUS
   baseline, never against its campaign-tree numbers.** Both sides are then
   real field sessions and the scenario confound drops out; the campaign
   trees stay a same-guidance, synthetic-fixture data point, not a
   baseline.
4. If the post-merge `all`-fork rate is still substantial, that is real
   signal the guidance is not reaching real sessions the way it reaches
   these fixtures — escalate it, do not re-average it away.

**Spawn-guidance audit — the silent-bridge finding.** Every hit from an
unfiltered `git grep` over `skills/` at `329b8f1` was read and classified.
**Exactly one of four harness-bridge files carries concrete,
parameter-level isolation guidance:** `codex-tools.md` ("give children a
clean context with `spawn_agent {fork_turns: "none"}`; the default `"all"`
copies your entire transcript into the child"). The other three —
`gemini-tools.md`, `pi-tools.md`, `antigravity-tools.md` — translate the
verb "dispatch" to that harness's native call (`invoke_agent`, the
`pi-subagents` `subagent` tool, `invoke_subagent`) but **never state
whether the native call is isolated by default or which parameter to set**.
The harness-agnostic skills (`dispatching-parallel-agents`,
`subagent-driven-development`, `requesting-code-review`) say the right
thing at the principle level ("isolated context… never inherit"), but
nothing in the tree tells a Gemini/Pi/Antigravity session *how* to make
that true at the tool-call level. Claude Code has no bridge file at all,
consistent with the Task tool being isolated by construction. Four other
hits are a different axis (no-recursive-dispatch), two are filesystem
isolation (git worktrees), and four are false positives, all enumerated so
the count is not overstated.

**Follow-up-treatment note, not a proposal to ship.** This is a
documentation-completeness gap, **not a demonstrated behavioral one** — no
field or mined evidence anywhere in this campaign shows a
Gemini/Pi/Antigravity full-history fork actually occurring, and both
populations measured here are 100% Codex. Whoever picks this up needs a
mined corpus from one of the other three harnesses before proposing text;
the fix, if warranted, belongs in that harness's own `references/*-tools.md`
file mirroring `codex-tools.md`'s pattern, not in the harness-agnostic
skill text.

## 5. Fix-cycle-ready treatments

**The rule this list ships under, restated.** *No unshipped, ungraded
text.* The previous fix cycle established it the hard way: a four-line
commit that rode along on the arm during two batteries but that no
pre-registered criterion ever graded was dropped from the PR stack rather
than shipped, so that every line in each diff as pushed is text a graded
battery actually ran. The same rule binds anything drawn from this
campaign. **Each row below names the exact branch and SHA whose diff was
mounted and graded. A fix cycle may ship that diff. Any addition,
rewording, or merge of two arms' text produces new text that no battery has
run, and needs its own battery before it ships.**

**And this campaign does not ship any of it.** Shipping goes through a
**new fix cycle with Jesse's approval**, not through this closeout.

| Treatment | Branch @ SHA | Text it changes | Evidence line |
|---|---|---|---|
| **X9-A never-stall doctrine** *(headline candidate)* | `cp/x9a` @ `76cb06a` | `sdd/SKILL.md` — preflight scan, task-loop breaker, implementer escalation, final-review breaker, the four-class catastrophic boundary, the `Ruling: <what you decided> — <why> — <what it costs if wrong>` grammar, and Finish's "Rulings I made" collection | All **15** seeded-plan reps without X9's doctrine (control, X7-A, X7-B, X1-E, X1-G ×3) stall after Task 1; control proceeds **0/3**. X9-A: **3/3 past Task 1** (2 clean + 1 nuanced), **0/3 non-catastrophic blocking waits**, 2.7 rulings/rep ledgered, catastrophic guard **2/2 tested, 2/2 held**, **zero wrong-ruling rework** observed. Cost 2× control and every dollar is throughput |
| **X2-A advisory-details contract** | `cp/x2a` @ `5364c34` | `writing-plans/SKILL.md` ("Working From This Plan") **+** `sdd/SKILL.md`'s dispatch-brief "What binds the implementer" bullet | Gate positive: control **3/3** subagent stalls on the absent file. X2-A **0/3 pauses, 3/3 proceed-and-record**, genuine-conflict guard **3/3**. **The `writing-plans` half is UNGRADED** — inert in this fixture because the plan was pre-authored. Ship the whole diff only if a fix cycle accepts that half as ungraded, or grade it first |
| **X5-B machine-checkable receipt file** | `cp/x5b` @ `644bee6` | `sdd/SKILL.md` (receipts-file dispatch naming; `cat`/`grep` at the two review sites) **+** `sdd/implementer-prompt.md` (receipt appended to `[RECEIPTS_FILE]`) | Invalidation guard **9/9**. Receipt-issuing real in **3/3** reps. Honoring **and** invalidation both hand-verified in raw transcript text — the file-based design routes through a plain tool-call output, which is exactly why it is observable. **Net savings unproven at n=3** |
| **X5-A receipts-in-report** | `cp/x5a` @ `d71d307` | `sdd/SKILL.md` (honor/invalidate rule into the reviewer or fix dispatch; "a fix round invalidates receipts") **+** `sdd/implementer-prompt.md` (Report Format receipt + short-status repeat) | Invalidation guard **9/9**. Issuing real in **3/3**. Honoring/declining confirmed in **8 reviewer final-answer messages across 3/3 reps** — in prose, not the strict marker grammar. **Net savings unproven at n=3.** Under codex specifically its honor signal is not machine-scorable; an amended design echoing through an unencrypted channel converges on X5-B |
| **X7-A evidence-bearing preflight** | `cp/x7a` @ `e1cd285` | `sdd/SKILL.md` — preflight emits its pairwise checks as a ledger table ("clean" without rows is not a scan) and rules on what it surfaces | Evidence artifact pre-Task-1 **3/3** seeded, **2/2** clean; false-positive guard **0/6** across all clean-plan reps; two extra findings adjudicated as real, not invented. **Does not by itself stop session-level stalling** (0/3 past Task 1) |
| **X7-B mechanical consistency check** | `cp/x7b` @ `edd9bcd` | `sdd/SKILL.md` **+** new file `sdd/scripts/plan-conflict-scan` | Script stdout byte-identical to the pre-registered expected output in **3/3** seeded and **2/2** clean reps; documented prose blind spot confirmed at the script layer and covered by the arm's own prose-scan clause in **2/2** prose reps; false-positive guard **0/2** clean. **Same preflight-only scope limit as X7-A** |

**Composition note, load-bearing.** X7-A/X7-B and X9-A are complementary.
Shipping X7 alone buys evidence and false-positive safety at the preflight
gate and **does not** deliver Amendment 2's "never stalls" goal — 0/6 X7
seeded-plan reps get past Task 1. Shipping X9-A alone delivers the
non-stalling behavior without X7's evidence artifact. **No battery has ever
run the composition**, so a fix cycle that wants both must grade the merged
text, not assume it.

**Interaction with the shipped fix-cycle PRs (#2059–#2063).** X9-A's diff
was cut from `codex-efficiency-fixes`@`329b8f1` — the fix cycle's own tip,
which is what those PRs stage. X9-A patches `sdd/SKILL.md` at the preflight
scan, the task-loop breaker, the implementer-escalation clause, and the
final-review breaker; the fix cycle's T1 branch also touches
`subagent-driven-development`, and the T2/T5 stack touches a shared
`SKILL.md` region alongside `codex-tools.md`. **A fix cycle picking up
X9-A must re-verify the diff applies to whatever `dev` looks like after
#2059–#2063 merge, and must treat any conflict resolution as new,
ungraded text.** The measured behavior above belongs to `76cb06a` as
mounted, not to a rebased descendant of it.

**Secondary candidates, weaker evidence, listed so they are not lost.**
X2-C (`cp/x2c` @ `4b2abd9`) passes the letter of its criterion with one
disclosed residual stall and no formal status keyword — a real but softer
result than X2-A's. X9-B (`cp/x9b` @ `c9d0c87`) passes 2/2 valid reps but
at n=2, and nothing in the evidence distinguishes its extra surfacing
paragraph from X9-A's behavior. **Do not ship either as an improvement on
its sibling on this evidence.**

**Explicitly not ready.** X1-A/B/C (no arm won; X1-B's 5.8-vs-7.2 round
advantage is directional at n=4 with the guard unexercised), X1-E/X1-G
(never reached their own decision point), X2-B (fails 1/3 as written, no
causal story), X3-A/B/C (X3-C only ever safe with paraphrase-aware
citation matching; X3-B never tested at any tier), X6-A/X6-B (never
engaged), X8-A/X8-B (guard holds but discrimination confounded).

## 6. The queue — candidates for the next campaign

Everything parked, carried forward, or observed-but-not-chased. Nothing
here was fixed during this campaign.

**Fixtures owed (each blocks a specific question).**

1. **X1 edit-existing-code fixture.** A defect-escape guard needs the
   mistake seeded into **starting code an implementer edits**, not prose an
   implementer builds from. `cp-x1-buggy-sdd`'s seeded shapes never occur
   in a from-scratch codex/gpt-5.6 build against clear prose (0/16).
2. **X1 wave-cap fixture where the cap-exception is reachable independent
   of any other conflict's resolution.** The current plan composes Conflict
   1 onto the cap-exception's own tasks (Task 2 deletes the module Task 4
   would modify), so every competent resolution moots it. E and G also need
   a plan whose earlier tasks are conflict-free, or pairing with X9's
   doctrine, to reach their own mechanism at all.
3. **X6 plan-framed fixture.** Either a bigger, less-trivial dozen-edits
   fixture that reads as SDD-shaped work under a free-form prompt, or a
   story that explicitly frames the work as a plan or task list — at the
   cost of then testing "does X6 help once SDD is engaged" rather than
   "does X6 change whether SDD gets reached for."
4. **X8 fork-discrimination fixture without the disclosure confound.** The
   current Task 2 text ("note your reasoning in the report") mandates the
   primary signal for every arm. A starker approval boundary, or larger n,
   would also address X8-B's `Ruling:` grammar never firing on the hard
   case in 3/3 reps.
5. **X2-B isolation fixture.** Something where the file-structure or naming
   choice is consequential enough for a reviewer to have an opinion —
   `cp-x2-advisory`'s Files: blocks just name existing files edited in
   place.
6. **X5 savings battery at scale, with distinct-event counting.** 3 reps ×
   a 3-task plan cannot separate a real 10–15% reduction from ordinary SDD
   variance, and this fixture's scope may be structurally too small to show
   the "12× worst case" the design doc describes.

**Mechanisms never tested end-to-end.**

7. **X3-B's controller half** (grep-and-flag of unsourced inventory lines)
   — untestable single-shot, and no FULL arm ever mounted `cp/x3b`. It
   needs its own battery as a real arm.
8. **X7 + X9 composed**, per §5.

**Instrument work.**

9. **Lease-grammar prose coverage.** Codex reviewers narrate honoring in
   their own words rather than reproducing the fixed marker; the strict
   `LEASE-HONORED:`/`LEASE-INVALIDATED:` grammar under-covers real
   behavior. A future battery needs a prose-aware honor detector alongside
   the strict one.
10. **Distinct-event counting for `lease_events`.** Count from the final
    receipts file's full content (read once, before workspace deletion) or
    deduplicate on `(kind, command_norm, tree_sha)`; additionally scan exec
    **call** command text, not only output, to catch writes never read back.
11. **`score_x1_chains._extract_findings()`'s `NONE_VALUE_RE`** matches
    only exact `none`/`none.` and does not recognize "none identified beyond
    the [already-counted] X," inflating finding and unbacked counts.
12. **`score_x1_chains`'s fourth real chain pattern** — a repeatedly
    re-tasked single reviewer via `NEW_TASK`/`MESSAGE` envelopes rather
    than fresh spawns per round — is invisible to the scorer, which keys
    off fresh spawns.
13. **`score_x3_rider`'s BAIT signature** was designed for defect-presence
    recall and produces real false positives when reused for bait-blocking
    precision on FULL-tier narrative text (2 found, both manually
    corrected, deliberately not patched). A narrower blocking-specific
    signature is worth it if the rate recurs at scale.
14. **The dot-directory `glob('**')` bug class.** Hit twice in this
    campaign (`task9_extract_signals.find_ledger()`, and the
    `fork_stats()` invocation on battery rep roots). Audit any other scorer
    globbing over a `.worktrees`/`.superpowers`/`.codex`-shaped tree; use
    `os.walk` or a literal dot path component.

**Harness and scenario hygiene.**

15. **Scenario deflection pinning.** `cp-x7x9-conflicts/story.md`'s
    Gauntlet reply is prose-guided, not a pinned verbatim string, and the
    Gauntlet ad-libbed a materially different framing exactly once in 21
    seeded-plan sessions — enough to void a rep. **Any re-run of this
    scenario must pin the deflection reply to an exact, non-ad-libbable
    string first.** `cp-x2-advisory` and `cp-x8-approvals` each leave three
    response categories paraphrase-guided; those reps were all verified
    clean this campaign, but the same risk stands.
16. **The X7-B parser-scope decisions, ratified as-built and worth
    revisiting.** Producer recognition reads `Produces:` lines only (misses
    a real conflict if a plan ever names a produced interface only in
    prose); prose `Consumes:` lines are not attempted by design;
    multi-name backtick spans are not decomposed. None of the three cost
    anything on this campaign's fixtures — all three are live risks on a
    differently-shaped plan.
17. **X5-A's honoring channel under codex.** Crediting its honoring
    behavior mechanically needs either a non-codex harness where dispatch
    payloads are not encrypted, or an amended design that echoes the
    honor/invalidate line through an unencrypted channel.
18. **The three silent harness bridges** (`gemini-tools.md`,
    `pi-tools.md`, `antigravity-tools.md`) — needs a mined corpus from one
    of those harnesses before any text is proposed (§4).
19. **Scope auditability (M0's follow-up).** Machine-readable declared
    scope in dispatches would turn the 17–24%-recoverable region into a
    measurable one, and would close the sidequest taxonomy entry with
    evidence rather than with an unfalsifiability caveat.

**Observations banked (not experiments yet).**

20. **SDD's finishing step does not reliably converge on merge, even in
    PASS reps.** 5 of 16 X1 FULL reps (**31%**) ended with `main` never
    advanced past the seed commit: the 4 disclosed `indeterminate`/`fail`
    reps plus one clean, deliberate, gauntlet-approved non-merge.
    `cp-x1-buggy-sdd/checks.sh`'s `file-exists` post-checks verify the
    working tree, so a rep that never merges scores identically to one that
    does. A scenario that wants to grade "did the work land on `main`"
    needs its own check.
21. **The 60-minute ceiling is still insufficient for a real minority of
    reps.** 4 of 16 (**25%**, one per arm, near-uniformly) did not reach a
    clean merge inside the bumped `quorum_max_time`, after a 33% bump from
    45m. Either size further, or accept ~25% non-merge as this scenario's
    honest baseline. None of those reps was excluded from scoring.
22. **`verdict.json`'s `provenance.superpowers_rev` is `null` on every rep**
    in this campaign — an apparently harness-wide gap. Arm-SHA
    reconciliation happens per script invocation and is echoed to stderr,
    never persisted per rep. A real persisted per-rep SHA field exists in
    the schema and is not populated.
23. **The `progress.md` capture gap** for `cp-x2-advisory` and
    `cp-x8-approvals`: the SDD scratch workspace is deleted by the
    session's own finishing step before results are captured, so
    ledger-artifact evidence must come from the raw transcript.

## 7. Process lessons

**1. Review was the load-bearing seat, and it earned that every time.**
**Eight tasks needed a fix round — ten rounds in total**
(Task 3 alone took three, and its round 0 was a full rejection with one
Critical and six Important findings). **Every FULL-tier battery verdict —
Tasks 8, 9, 10, 11, and 12 — required a correction entry.** The
corrections were not cosmetic and they did not all cut one way:

- **Two corrected in the arm's favor.** X2-A's classification was wrong for
  2 of 3 reps (they *had* recorded the deviation, in a `concerns:`
  continuation line a grep-filtered dump had truncated), turning
  "1/3 proceed + 2/3 silent" into **3/3 proceed-and-record**. X5-A's
  honoring mechanism was reported as structurally invisible; the re-read
  found it working in 3/3 reps and the arm went from PARTIAL PASS to PASS.
- **One voided a reported failure.** X9-B's "genuine compliance failure"
  was a harness confound — the Gauntlet ad-libbed past its script — and the
  carry-forward built on it was retracted.
- **Several tightened claims that were true but overstated:** "6/6" guard
  holds became "4/4 held, 2 excluded"; "appears in ZERO transcripts" became
  "appears benignly in 21/29; zero reps execute it"; "28/29 reproduction"
  became "21/21 seeded-plan reps"; "structurally forecloses" became
  "empirical n=5"; "20-30x" became ~31x on means and ~2,400x on medians;
  "every checked file uses integer-only arithmetic… campaign-wide" became
  10/12, **including one retained float multiplier in the winning arm**.

The pattern worth keeping: **the corrections that mattered most came from
re-reading raw data, not from re-reasoning about it.** Every one above was
independently re-verified against rollouts before being written, not taken
on the reviewer's word.

**2. The campaign's own pathology reproduced in its own tooling.** Five
times over the campaign, a dispatched subagent driving a long battery
appeared to stall from the coordinator's side — no output while work was in
fact progressing — costing coordinator attention and prompting
intervention. **Prompt-text mitigation was tried and was not sufficient**:
instructions to poll in the foreground and never end a turn with work
outstanding were carried into every battery brief from Task 8 onward, and
the stalls kept recurring; Task 10's own verdict records the coordinator
correcting that task's polling approach mid-run, replacing reliance on
background completion notifications with genuine bounded foreground poll
loops. That is the campaign's clearest evidence of a boundary on what
instruction text can fix: X9's doctrine changed a *model's* stalling
behavior, and the same doctrine written into task briefs did not change the
*harness's*. **Narrative-tier, and flagged as such:** unlike every other
finding in this report it has no instrumented artifact beyond Task 10's
operational note, and it should be re-observed before it is acted on.

**3. Three privacy incidents, and a sweep that had to keep evolving.**

- **Task 1 (self-caught, no real leak).** The disclosure entry quoted the
  sweep's own grep pattern verbatim inside the log, making the sweep
  self-match on its own needle list. Reworded to *describe* the sweep
  rather than quote it, matching house style, and re-run clean.
- **Task 7 (self-caught, real leak, pre-commit).** Three regression-test
  fixtures had been built directly from the real corpus text that exposed
  each bug and still carried it — a real absolute path containing the
  donor's local username, and real internal function and branch names.
  Rewritten to synthetic equivalents preserving the structural shape the
  tests need, re-swept against `git diff --cached` rather than the working
  tree.
- **Task 7 (caught by review, real leak, committed).** Two Criticals: the
  log entry and a commit message named the remote mining host literally
  instead of using the established `remote-host-a` alias, and the round-0
  self-disclosure **re-leaked the very username path it was describing** —
  the one place that value still existed in the repo. Fixed by a soft-reset
  history rewrite of two unpushed commits, with zero-hit greps verified
  across `git log <pre-task>..HEAD --patch` and each commit message before
  and after.

**The rule that came out of it:** a needle-list sweep pattern-matching for
known shapes (emails, keys, hostnames, ticket IDs) cannot catch content
whose only sin is being *derived from data outside this repo*. Quoting real
corpus evidence into a regression fixture or a narrative sentence is the
easy way past it — including, twice, inside the disclosure describing the
previous catch. From Task 8 onward every sweep checked the real hostname
and username by running `hostname`/`whoami` and grepping for the values
without ever writing them into committed text, and the alias convention
became binding on all prose.

**4. Instrument-design lessons, four of them, each paid for.**

- **A control at the floor cannot discriminate; it can only make a
  treatment arm look worse.** That is exactly what happened to X1-A in
  micro v1 (4% false-block against a control at 0%). Any prune rule of the
  form "strictly better than control" is unsatisfiable the moment control
  hits the floor — which is why the pre-registered
  inconclusive-by-ceiling clause, written *before* the run, is what let
  three batteries stop honestly instead of iterating fixtures.
- **From-scratch fixtures cannot seed defect escape.** Prose that describes
  what to build does not make a capable implementer build the mistake. Seed
  the mistake into code the implementer edits.
- **Deflection pinning is a measurement control, not a scenario detail.**
  One ad-libbed Gauntlet reply in 21 sessions voided a rep and nearly
  published a false compliance failure. It also made the whole battery's
  deflection text an uncontrolled variable until independently
  re-verified — which is now a standing per-rep, pre-grading step
  (extract the delivered text, compare against `story.md`, *then* grade).
- **Presence and engagement are different denominators, and both are
  true.** X2-B/X2-C's residual stall reads as 1 per 3 total reps (33%) or 1
  per 2 *engaged* reps (50%) depending on which question is being asked.
  Say which one, every time.

**5. Append-only discipline needs exactly one escape hatch, used once.**
Task 1's review found two defects inside a section whose header claims
verbatim reproduction. Because the log was genuinely pre-use — one commit,
cited by nothing — the controller ruled an in-place correction permissible
**that once**, with a dated disclosure entry appended, and stated that
append-only binds strictly from that commit forward. It held: every one of
the eleven later corrections is a new dated entry, and the superseded text
sits unedited above it. The cost of that discipline is that a reader must
follow the correction pointers; the benefit is that no number in this
report can be quietly revised out of existence.

**6. The campaign ran its own doctrine on itself.** Amendment 2's
principle — rule, ledger, proceed; reserve blocking for the catastrophic
boundary — governed this plan's own execution. Non-catastrophic ambiguities
became controller rulings recorded in the SDD ledger rather than blocking
questions, including the two consequential ones: voiding the micro prune
gate for instrument inability (which sent all three X1 arms to FULL
unproven), and closing X1 on the honest ceiling verdict rather than
re-battering a fixture shape already known not to elicit the pathology.
Neither would have been a defensible unilateral call by a task; both were
made explicitly, in writing, in the ledger, by the controller, and every
downstream task cites them. The mechanism the campaign was grading turns
out to be the mechanism that made the campaign finishable.

## 8. Budget

Full itemized ledger: `logs/2026-07-31-cost-pathologies.md`, the "Budget
ledger" table plus the per-task ledger rows appended under each verdict.

| Date | Battery | Cost | Reps / calls |
|---|---|---:|---|
| 2026-07-31 | X1 MICRO v1 (Task 4) — reviewer-arm calibration | ~$0.95 (reconstructed) | 20 API calls |
| 2026-07-31 | X1 MICRO v2 (Task 4b) — ambiguity-bearing fixture | $1.6685 (measured) | 20 API calls |
| 2026-07-31 | X3 MICRO (Task 5) — invented-requirement bait | $2.3491 (measured) | 60 API calls |
| 2026-08-01 | Task 6 smoke — scenario health, not graded | $8.78 | 2 reps |
| 2026-08-01 | Task 8 — X1 FULL (A/B/C + control) + X3 rider | $158.1788 | 16 reps |
| 2026-08-01 | Task 9 — X7 + X9 + X1 wave-cap, vs shared control | $62.2629 new (+$1.1034 reused = $63.3663 graded) | 29 reps (28 new) |
| 2026-08-01 | Task 10 — X2 gate + arms, X8 battery | $70.7079 | 21 reps |
| 2026-08-01 | Task 11 — X5 battery + X6 gate | $37.6005 | 10 reps |
| 2026-08-01 | Task 12 — X4 fork-tax measurement + audit | $0.00 | 0 reps (local, read-only) |
| | **Campaign total** | **$342.50** | **77 container reps + 100 API calls** |

**Against the ceiling: 59% of $580.** The **$400 stop-and-report checkpoint
was never reached** — the closest approach was Task 11, which entered at
$304.90 and ran under a binding hard rule (checked after *every* rep, at
`JOBS=1` specifically so it could be acted on between launches) to stop
before any projection exceeded $395. The nearest that projection ever got
was ~$335.

**Zero-cost work.** Tasks 1, 2, 3, 7, and 12 spent nothing: the campaign
scaffold, three MINE-tier scorers plus the X5 lease scorer (**436 tests
green** at Task 8, from a 341-test baseline), 21 arm branches, and the
entire X4 measurement study and spawn-guidance audit.

**X6's gate saved real money.** The pre-registered stop rule fired on the
first control rep at $0.49 and **8 budgeted reps were never spent** —
against a pre-registration estimate of $25–60 for that sub-battery. Task 11
came in at $37.60 against a $55–115 combined estimate almost entirely
because of it.

**Estimate accuracy, honestly.** Two batteries ran meaningfully over their
own internal projections: Task 8 at ~5% over the top of its $120–150 range,
and Task 10 at roughly 2× its worst-case internal math ($70.71 vs $37)
because the pre-registration priced "2 tasks" as a proxy for "cheap"
without pricing the full SDD ceremony overhead per task (6–9 dispatches per
rep). Both were disclosed at verdict time rather than absorbed. Task 9 came
in under estimate, and the three micros came in at or below the low end of
theirs.

## 9. Sources

- **`logs/2026-07-31-cost-pathologies.md`** — the append-only hypothesis
  log; the primary record. Every pre-registration, verdict, controller
  ruling, and correction entry. Where a verdict and a later correction
  disagree, the correction governs.
- **`docs/2026-07-31-cost-pathologies-campaign-design.md`** — design doc
  plus Amendments 1 (X7/X8, the X1 wave-arm addendum) and 2 (X7/X8
  non-blocking reframe, X9). Source of truth for the measured cost picture
  and every verbatim criterion.
- **`docs/plans/2026-07-31-cost-pathologies-evals.md`** — the 13-task
  implementation plan plus its own Amendment 1 (Task 4b).
- **`campaigns/cost-pathologies/`** — README, `arm-manifest.md` (arm →
  branch → SHA → files touched → mechanism, for all 21 arms), five
  corpus-validated scorers plus `scorer_common.py`, three one-shot triage
  helpers (disclosed as *not* corpus-validated), `run-quorum.sh`, eight
  scenario directories each with its seeded-truth ledger, and the MICRO
  fixtures and scripts.
- **`.superpowers/sdd/2026-07-31-cost-pathologies-evals/`** — per-task
  briefs, reports, review findings files, and `progress.md` (the SDD
  ledger, carrying every controller ruling and carry-forward).
- **Arm branches** `cp/*` in `/Users/jesse/git/superpowers/superpowers` —
  **local experiment apparatus only: never pushed, never merged, never
  PR'd.** They are the graded text; §5 names the SHAs.
- **Prior campaigns, for continuity of method:**
  `reports/2026-07-codex-efficiency-campaign.md` and
  `reports/2026-07-codex-efficiency-fix-cycle.md`.
