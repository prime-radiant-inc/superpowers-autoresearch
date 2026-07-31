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
| X1-B rising severity floor | `cp/x1b` | 47d0df7 | sdd/SKILL.md | Rounds 1–2 accept Critical/Important; rounds 3+ accept Critical only, Important findings drop to the ledger. |
| X1-C marginal-value verdict | `cp/x1c` | 970f5b0 | sdd/SKILL.md, sdd/task-reviewer-prompt.md, sdd/re-review-prompt.md | Every review and re-review ends with "another round worth it: yes/no + what is at stake"; the loop stops on no, whatever the open count. |
| X1-E scoped auto second wave | `cp/x1e` | b26cda2 | sdd/SKILL.md | A second final fix wave is authorized only by a regression full verification finds, scoped to the failing command and ledgered. |
| X1-G hard cap | `cp/x1g` | 6a0eedf | sdd/SKILL.md | No second fix wave and no exception to ask for; every residual is ledgered and routed to the finishing gates. |
| X2-A plan-header contract | `cp/x2a` | 5364c34 | writing-plans/SKILL.md, sdd/SKILL.md | Plan header declares requirements binding and pictured details advisory; the dispatch carries the same contract to the implementer. |
| X2-B reviewer lens | `cp/x2b` | dcdb3fb | sdd/task-reviewer-prompt.md | Reviewer judges what the brief required, never how it illustrated the work; the plan's file list stops being a requirement. |
| X2-C implementer empowerment | `cp/x2c` | 184edfd | sdd/implementer-prompt.md | Implementer owns the deviation call over the brief's advisory details — not a blocker, not a question — and records it in the report. |
| X3-A reviewer citation rule | `cp/x3a` | b5c931f | sdd/task-reviewer-prompt.md | Every requirement a finding invokes is quoted to its source line; an unquotable requirement is filed Minor as the reviewer's own. |
| X3-B requirements inventory | `cp/x3b` | 29f1878 | sdd/implementer-prompt.md, sdd/SKILL.md | Implementer's report traces every implemented requirement to its source and marks unsourced work; controller clears unsourced entries before review. |
| X3-C adjudication default | `cp/x3c` | f478a24 | sdd/SKILL.md | A finding invoking an uncited requirement gets no fix round — it is ledgered as a suggestion for the final review. |
| X7-A evidence-bearing preflight | `cp/x7a` | e1cd285 | sdd/SKILL.md | Preflight emits its pairwise checks as a ledger table ("clean" without rows is not a scan) and rules on what it surfaces instead of batching a question. |
| X7-B mechanical consistency check | `cp/x7b` | 66a37fa | sdd/SKILL.md, sdd/scripts/plan-conflict-scan (new) | A script over the plan's Files:/Interfaces: blocks reports delete-vs-use, create-order, and produce/consume mismatches at setup; prose scan covers only what it cannot see; conflicts get rulings. |
| X8-A scope-bound approvals | `cp/x8a` | 83a7ef8 | sdd/SKILL.md | An approval covers the decision it answered; new substantive decisions get a recorded ruling, with four named classes still waiting for an approval that names them. |
| X8-B approval-ledger discipline | `cp/x8b` | cd9eb5d | sdd/SKILL.md | Approvals are ledgered with their scope; dispatches name the covering entry, and uncovered decisions become logged rulings. |
| X9-A rule-log-proceed | `cp/x9a` | 6ae5c12 | sdd/SKILL.md | Controller rules on every non-catastrophic conflict with the spec as binding authority, ledgers each ruling, stops only for the four catastrophic classes, and reports all rulings at session end. |
| X9-B rule-log-proceed + async surfacing | `cp/x9b` | acb60e9 | sdd/SKILL.md | X9-A plus one-line surfacing of each ruling as it is made, so the human can override in flight but is never waited on. |

`sdd/` = `skills/subagent-driven-development/`.

## Verification performed

Per arm, before its row was written: `git diff codex-efficiency-fixes..cp/<arm>
--stat` touches only the declared files; the branch carries exactly one
commit; the arm's distinctive phrase greps in the patched file on that
branch; and the added lines contain no other arm's distinctive phrase (the
single pre-registered exception is X9-B, which is X9-A plus surfacing by
design) and no measurement vocabulary. `plan-conflict-scan` (X7-B) was run
against two seeded fixtures and three real plans: it surfaces all three
seeded conflicts and reports zero findings on the real plans.

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

**Authoring worktree.** Arms were written in a single temporary worktree
(`/tmp/cp-arm-author`), reused serially and removed afterward. The
`.worktrees/codex-efficiency-fixes` worktree holding the base branch was
not touched.
