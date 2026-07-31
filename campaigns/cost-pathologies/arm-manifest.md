# Arm manifest — cost-pathologies campaign

Treatment-arm skill text. Every branch is LOCAL-ONLY in
`/Users/jesse/git/superpowers/superpowers` (never pushed, merged, or PR'd),
cut from `codex-efficiency-fixes` at **329b8f1** and carrying exactly one
commit. Batteries cite the SHA below, not the branch name — branches are
mutable, SHAs are the record.

Controls are the unpatched base (329b8f1): X1-D, X1-F (human-exception),
X2-D, X3-D, X7-C, X8-C, X9-C. X1-AB is not built; it is gated on A and B
both beating control independently.

Mechanism definitions live in
`docs/2026-07-31-cost-pathologies-campaign-design.md` (base + Amendments
1–2). This table records what was written, not what it is expected to do.

| arm | branch | sha | files touched | mechanism |
|-----|--------|-----|---------------|-----------|
| X1-A criterion-backing | `cp/x1a` | 1851307 | sdd/task-reviewer-prompt.md, sdd/re-review-prompt.md | A finding is Critical/Important only if it names the requirement line it violates or a concrete reachable failure path; otherwise Minor. |
| X1-B rising severity floor | `cp/x1b` | bc83650 | sdd/SKILL.md | Rounds 1–2 accept Critical/Important; rounds 3+ accept Critical only, Important findings drop to the ledger. |
| X1-C marginal-value verdict | `cp/x1c` | c5b24af | sdd/SKILL.md, sdd/task-reviewer-prompt.md, sdd/re-review-prompt.md | Every review and re-review ends with "another round worth it: yes/no + what is at stake"; the loop stops on no, whatever the open count. |
| X1-E scoped auto second wave | `cp/x1e` | b26cda2 | sdd/SKILL.md | A second final fix wave is authorized only by a regression full verification finds, scoped to the failing command and ledgered. |
| X1-G hard cap | `cp/x1g` | 6a0eedf | sdd/SKILL.md | No second fix wave and no exception to ask for; every residual is ledgered and routed to the finishing gates. (Its rewrite drops the base clause "stop on load-bearing ones" in place — "load-bearing ones included" overrides the breaker reference that survives in the same sentence.) |
| X2-A plan-header contract | `cp/x2a` | 5364c34 | writing-plans/SKILL.md, sdd/SKILL.md | Plan header declares requirements binding and pictured details advisory; the dispatch carries the same contract to the implementer. |
| X2-B reviewer lens | `cp/x2b` | dcdb3fb | sdd/task-reviewer-prompt.md | Reviewer judges what the brief required, never how it illustrated the work; the plan's file list stops being a requirement. |
| X2-C implementer empowerment | `cp/x2c` | 4b2abd9 | sdd/implementer-prompt.md | Implementer owns the deviation call over the brief's advisory details — not a blocker, not a question — and records it in the report. |
| X3-A reviewer citation rule | `cp/x3a` | b5c931f | sdd/task-reviewer-prompt.md | Every requirement a finding invokes is quoted to its source line; an unquotable requirement is filed Minor as the reviewer's own. |
| X3-B requirements inventory | `cp/x3b` | b670a91 | sdd/implementer-prompt.md, sdd/SKILL.md | Implementer's report traces every implemented requirement to its source and marks unsourced work; controller flags unsourced entries, ledgers them, and names them in the reviewer's dispatch (no bounce-back). |
| X3-C adjudication default | `cp/x3c` | f478a24 | sdd/SKILL.md | A finding invoking an uncited requirement gets no fix round — it is ledgered as a suggestion for the final review. |
| X7-A evidence-bearing preflight | `cp/x7a` | e1cd285 | sdd/SKILL.md | Preflight emits its pairwise checks as a ledger table ("clean" without rows is not a scan) and rules on what it surfaces instead of batching a question. |
| X7-B mechanical consistency check | `cp/x7b` | fd5dc74 | sdd/SKILL.md, sdd/scripts/plan-conflict-scan (new) | A script over the plan's Files:/Interfaces: blocks and task code reports delete-vs-still-listed, modify-before-create, consumed-callable-with-no-producer, and in-task call/definition arity mismatches at setup; prose scan covers only what it cannot see; conflicts get rulings. |
| X8-A scope-bound approvals | `cp/x8a` | 83a7ef8 | sdd/SKILL.md | An approval covers the decision it answered; new substantive decisions get a recorded ruling, with four named classes still waiting for an approval that names them. |
| X8-B approval-ledger discipline | `cp/x8b` | a279eaf | sdd/SKILL.md | Approvals are ledgered with their scope; dispatches name the covering entry, and uncovered decisions become logged rulings. |
| X9-A rule-log-proceed | `cp/x9a` | 76cb06a | sdd/SKILL.md | Controller rules on every non-catastrophic conflict with the spec as binding authority, ledgers each ruling, stops only for the four catastrophic classes, and reports all rulings at session end. |
| X9-B rule-log-proceed + async surfacing | `cp/x9b` | c9d0c87 | sdd/SKILL.md | X9-A plus one-line surfacing of each ruling as it is made, so the human can override in flight but is never waited on. |

`sdd/` = `skills/subagent-driven-development/`.

## Verification performed

Per arm, before its row was written: `git diff codex-efficiency-fixes..cp/<arm>
--stat` touches only the declared files; the branch carries exactly one
commit; the arm's distinctive phrase greps in the patched file on that
branch; and the added lines contain no other arm's distinctive phrase (the
single pre-registered exception is X9-B, which is X9-A plus surfacing by
design) and no measurement vocabulary. Re-run in full after fix round 1;
all 17 pass.

**`plan-conflict-scan` (X7-B) validation — measured, from the committed
blob.** Fix round 1 rebuilt this script: the `produces X but never writes
it` check is gone, a consumed interface now counts only where a paren
touches the name, dotted and bare forms dedupe on their last segment, and
an in-task call/definition arity check was added.

True positives, seeded fixture (5 seeded, 5 surfaced): delete-vs-still-
listed, modify-before-create, consumed-produced-later, consumed-with-no-
producer, and `summarize(rows)` defined vs `summarize(rows, fmt)` called
inside one task.

False positives on real plans, before → after:

| plan | before | after |
|------|--------|-------|
| `docs/plans/2026-07-31-cost-pathologies-evals.md` | 6 | **0** |
| `docs/plans/2026-07-28-codex-efficiency-evals.md` | 10 | **1** |
| `docs/superpowers/plans/2026-07-14-go-fractals-cli.md` (Interfaces-bearing) | 0 | 0 |
| clean fixture | 0 | 0 |

The one remaining false positive is real and stated plainly: Task 10 of the
codex-efficiency plan lists `mutation_events(path) -> list[timestamp]` under
Consumes and then implements it in its own Step 1 ("add with a unit test").
The scan sees a callable consumed with no producing task and cannot see that
the consuming task produces it itself. Known blind spot, documented in the
script header; not fixed by heuristic, because guessing which prose means
"this task writes it" is how the first version reached 6 and 10 FPs.

Both counts come from `git show cp/x7b:…/plan-conflict-scan`, not the
working tree — the first fix attempt passed in the working tree while the
committed blob was syntactically broken (an apostrophe closed the awk
program's quoting), which is why validation now runs the committed blob.

## Notes

**Base SHA.** Every branch is cut from `codex-efficiency-fixes` = 329b8f1
("docs(spec): soften the spinout-stack sources note per Jesse"). Control
arms run this SHA unpatched; there is no control branch.

**Runner integration gap (owed by Task 8+).**
`campaigns/codex-efficiency/run-quorum.sh` selects the mounted
`SUPERPOWERS_ROOT` from a hardcoded `case "$ARM"` with four names
(`dev|spinout|v611|fix` → `/tmp/sp-arm-{dev,spinout,v611,fix}`), and aborts
when the named worktree is missing. None of the `cp/*` branches is
reachable through it today. Before the first battery runs, either (a) add a
case per arm mapping `cp/<arm>` to its own checkout at `/tmp/cp-arm-<arm>`,
or (b) generalize the selector to take a branch and materialize
`/tmp/cp-arm-<arm>` on demand — (b) is the smaller total change across 17
arms. Each arm needs its own directory: the runner mounts one
`SUPERPOWERS_ROOT` per run, so arms cannot share a worktree that is
checkout-switched between reps, and parallel `JOBS` would race on it.
Whichever route, the battery must record the arm SHA it actually mounted
(`git -C <root> rev-parse HEAD`) and reconcile it against this manifest —
a battery that cannot name its arm's SHA is ungraded.

**Fix round 1 (task review).** Eight branches were amended in place (single
commit per branch preserved; SHAs above are post-fix): X7-B rebuilt for
false positives and given the intra-brief arity check; X9-A/X9-B closed an
eighth stall site in Final Review; X1-B and X1-C amended the three and one
surviving contradictions their mechanisms create elsewhere in SKILL.md;
X2-C amended the two hooks in implementer-prompt.md that contradicted its
grant; X3-B narrowed to the design's verb (flag + ledger, not bounce-back)
per controller ruling; X8-B gained the fourth catastrophic class so it
matches X8-A. X1-G unchanged.

**Authoring worktree.** Arms were written in a single temporary worktree
(`/tmp/cp-arm-author`), reused serially and removed afterward. The
`.worktrees/codex-efficiency-fixes` worktree holding the base branch was
not touched.
