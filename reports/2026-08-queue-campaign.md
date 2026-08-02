# Queue-Execution Campaign — Closeout Report (2026-08-02)

One session, 2026-08-01 → 2026-08-02. Directive (Jesse, post-compaction):
run the full 23-item queue from
`reports/2026-08-cost-pathologies-campaign.md` §6 assuming PRs
#2059–#2064 landed; $1000 envelope. Test base: `sim/dev-postmerge`
@ 1fed99d (dev + the four PR heads; delta vs the old arm base = exactly
the 4 dropped 433184c lines). All arms rebased; log:
`logs/2026-08-01-queue-campaign.md` (every claim below has a dated entry
there). Authorship disclosure: campaign executed via SDD
(implementer/reviewer subagents per task, 10 fix rounds across 9
reviewed tasks); after the session's 200-subagent limit, Task 13's
review and all Task 9/12 mechanical scoring + verdicts were performed
directly by the controller, disclosed per-entry.

## 1. All 23 items closed

| # | item | disposition |
|---|---|---|
| 1 | X1 edit-existing fixture | **FIXED + ANSWERED** — fixture built (T5, 2 fix rounds); battery: escape guard BINDS for the first time (control 2.0 escapes/rep); X1 arms null (2.0/2.0/2.5/2.0); escapes are attention-structured |
| 2 | X1 wave-cap fixture | **FIXED + ANSWERED** — reachability fixed 9/9 (vs 0/29); arms INCONCLUSIVE-BY-REVIEWER-BLINDNESS (0/45 seeded-drift detection) |
| 3 | X6 plan-framed + MINE | **FIXED + ANSWERED** — MINE host baseline (174 sessions, median 2 dispatches, floor-ratio median 79,504×); battery: **X6-A batching = 73% cost cut, 87% dispatch cut, better completion — ship candidate** |
| 4 | X8 confound-free fixture | **FIXED + ANSWERED** — confound removed; 9/9 all-arms proceed-with-spontaneous-ruling; no behavioral headroom; X8 arms closed as candidates |
| 5 | X2-B isolation fixture | **FIXED + INCONCLUSIVE-BY-UNIFORM-CONFORMANCE** — 9/9 plan-conformant trees; natural-deviation base rate ~0; review-only micro-battery queued as the right instrument |
| 6 | X5 savings at scale | **ANSWERED (negative)** — n=8/arm: mechanisms fully confirmed (x5b strict honoring 53/58 end-to-end), savings REFUTED with wrong-direction dose-response; X5 ship candidacy closed |
| 7 | X3-B controller-half | **PARKED WITH EVIDENCE** — 3-tier convergence (MICRO 0%, FULL 0/32 reps, X8v2 9/9); aged-session replay harness queued |
| 8 | X7+X9 composed | **ANSWERED** — composition works (preflight 3/3, no-stall 3/3 closed-calibrated); rebased x9a re-validated 3/3 — **X9-A PR-ready** |
| 9 | Lease prose coverage | **FIXED** (T2 prose detector; 7/8 corpus recall) |
| 10 | Distinct-event counting | **FIXED** (T2; corrected published X5 numbers: x5b honored 3→12) |
| 11 | NONE_VALUE_RE | **FIXED** (T1; corrected published X1 table: A 0.586, B 0.565, C 0.538) |
| 12 | Re-tasked chain pattern | **FIXED** (T1; premise corrected — present once in corpus, silently mis-scored) |
| 13 | BAIT blocking signature | **FIXED** (T3; separate opt-in function, corpus-negative-validated) |
| 14 | Dot-directory glob class | **FIXED** (T3; 6 real defects behind `scorer_common.find_files()`, component-boundary matching after a fix round) |
| 15 | Deflection pinning | **FIXED** (T4; validated in production: 0 voids across all 66 battery reps) |
| 16 | X7-B parser scope | **DESIGNED + PARTIALLY FIXED** (T13; 3 limits pinned by tests; multi-name spans fixed in the vendored analysis copy — arm copy untouched per the no-ungraded-text rule) |
| 17 | X5-A honoring channel | **DESIGNED** (Amendment 3: echo through the unencrypted exec-output channel X5-B proved survives) |
| 18 | Harness bridges | **PARKED** — no gemini/pi/antigravity corpus exists on any reachable host; unchanged |
| 19 | Scope auditability | **DESIGNED** (`docs/2026-08-01-scope-auditability-design-note.md`; explicit input to plan-decomposition) |
| 20 | Merge-landed check | **FIXED** (T4; live in every battery's check output) |
| 21 | 60m ceiling | **RULED** — kept; non-merge graded, not excluded |
| 22 | Provenance null | **ROOT-CAUSED + DOCUMENTED** — linked-worktree `.git` pointer unreachable in-container; evals-repo fix queued; runner stderr echo is the fallback |
| 23 | Ledger capture | **FIXED** (T4 `extract_ledger.py`, 4 patch shapes + printf redirects after a Critical fix round; 21/21 corpus reps recover) |

## 2. Headline findings (in order of consequence)

1. **X9-A re-validated; PR-ready.** Rebased text reproduces the closed
   3/3 no-stall under the binding operationalization; catastrophic
   guard 5/5; the composed X7+X9 arm passes both halves. Next
   iteration queued: 3/4 adjudicated reps reached for the arm's own
   "stop only if every path forward is a guess" escape hatch.
2. **X6-A batching is the program's first clean positive cost
   treatment**: 73% cost / 87% dispatch reduction with better
   completion than control, against a MINE baseline showing the median
   dispatch consumes ~79,500× its useful output. Ship candidacy gated
   on one normal-plan boundary-regression check.
3. **The attention-routing thesis** (two independent batteries):
   whole-branch reviewers detected 0/45 seeded cross-task
   inconsistencies (praising drift as design), and defect escapes are
   attention-structured (unambiguous Important defect escapes 14/16
   while a routed judgment-case race is caught 14/16). Review-policy
   text does not redirect attention; task/file routing does. This is
   plan-decomposition's empirical foundation.
4. **X5 savings refuted; re-verification is behavioral.** Sessions
   re-verify ~10× the mandated rate; receipts get issued, read, and
   honored — and the tests run again anyway. More lease machinery =
   more runs. Treatments must change the act, not the information.
5. **Fresh-session null results keep localizing the pathologies**:
   models don't over-ask (X8: 9/9 proceed), don't invent requirements
   (X3: 3-tier zero), don't deviate from plan-named structure (X2:
   9/9 conform). The corpus pathologies live in aged/automation-heavy
   sessions — the closed campaign's localization headline, now
   reinforced by four more cells.
6. **Instrument doctrine: strict grammars undercount** (X5 leases,
   X8-A causal rule, X8-B Ruling — three experiments): every strict
   grammar now ships with a prose-aware companion, counts reported
   separately.

## 3. Corrections published to the closed campaign's numbers

X1 FULL cross-arm table (item 11/12 fixes): A 7.25 rounds / 0.586
novel-rate, B 0.565, C 0.538, control unchanged; no verdict flips.
X5 lease events (item 10): x5a issued 65→14; x5b 26→13 issued,
honored 3→12, invalidated 3→2 — X5-B's mechanism stronger than
published. Both transcribed as dated correction entries.

## 4. Ship recommendations for Jesse

- **X9-A: open the PR** (stacks on #2059–#2064's text; battery-green).
- **X6-A: one boundary-regression battery on a normal-sized plan, then
  PR** (~$30).
- Closed negative: X5-A/B, X8-A/B, X1-A/B/C (no escape reduction),
  X1-E/G (mechanism never under load — needs a real-defect-pressure
  fixture), X2-B (needs the review-only instrument).

## 5. Budget

Batteries: composed $31.25, wave-cap $36.73, X8v2 $34.65, X1-edit
$110.98, X5-scaled ~$192.35, X2 $26.01, X6 $54.09 = **$486.06**.
Plus one infra round (~$0 — 8 EACCES setup stubs, quarantined).
Non-battery API spend ≈ $0 (no MICRO/API batteries this campaign).
**~$514 of the $1000 envelope remains for the plan-decomposition
campaign.**

## 6. New queue

1. X9-A escape-hatch tightening ("stop only if every path forward is a
   guess" drives turn-1 bundled stops) — highest-value X9 iteration.
2. X6-A normal-plan boundary-regression check — the pre-PR gate.
3. X10 candidate: mechanical cross-module consistency scan at final
   review (all 45 missed seeds were greppable) vs a reviewer-checklist
   line.
4. Wave-cap arms need a fixture whose final review yields multiple
   REAL defect findings (consistency drift cannot pressure the cap).
5. X2-B review-only micro-battery over the committed deviation tree
   (x1-review-micro API pattern; ~1/20th the cost of full sessions).
6. Aged-session/automation replay harness (unlocks X3-B and the
   localization headline's direct test).
7. Behavioral re-verification treatment (X5's successor): change what
   the session does at the re-verify moment; pair with attention
   routing.
8. Heading-context `- None.` LIST_ITEM_RE false positive (26 corpus
   occurrences, T1 discovery).
9. Evals-repo provenance fix (worktree `.git` pointer unreachable
   in-container).
10. Runner hardening: bash-invoke setup.sh explicitly (exec-bit class);
    never gate arm chains on rep exit codes (both bit this campaign).
11. Vendored plan-conflict-scan drift discipline (touch both copies or
    state why not).
12. Residual grading depth: per-rep review-dynamics narratives for the
    X5/X6/X2 batteries (mechanical layers + controller hand-checks
    carried those verdicts; narrative depth awaits grading capacity).

## 7. Process notes

Review earned its keep everywhere it ran: 10 fix rounds, every one a
real defect (including the extractor parsing 1 of 4 real patch shapes
and the dot-dir fix reintroducing its own bug class via substring
matching). Two launch-infrastructure lessons are queue item 10. The
200-subagent session limit forced controller-performed verification for
the final third of the campaign — disclosed per-entry; raising
CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION (or splitting campaigns across
sessions) is the operational fix. The pinned-deflection standard
(item 15) recorded zero voids across 66 reps — the x9b-rep2 ad-lib
class is closed.
