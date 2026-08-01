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
