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
