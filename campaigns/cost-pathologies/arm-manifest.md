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
| X1-B rising severity floor | `cp/x1b` | 151b2e1 | sdd/SKILL.md | Rounds 1–2 accept Critical/Important; rounds 3+ accept Critical only, Important findings drop to the ledger. |
| X1-C marginal-value verdict | `cp/x1c` | 69fd769 | sdd/SKILL.md, sdd/task-reviewer-prompt.md, sdd/re-review-prompt.md | Every review and re-review ends with "another round worth it: yes/no + what is at stake"; the loop stops on no, whatever the open count. |
| X1-E scoped auto second wave | `cp/x1e` | b26cda2 | sdd/SKILL.md | A second final fix wave is authorized only by a regression full verification finds, scoped to the failing command and ledgered. |
| X1-G hard cap | `cp/x1g` | 6a0eedf | sdd/SKILL.md | No second fix wave and no exception to ask for; every residual is ledgered and routed to the finishing gates. (Its rewrite drops the base clause "stop on load-bearing ones" in place — "load-bearing ones included" overrides the breaker reference that survives in the same sentence.) |
| X2-A plan-header contract | `cp/x2a` | 5364c34 | writing-plans/SKILL.md, sdd/SKILL.md | Plan header declares requirements binding and pictured details advisory; the dispatch carries the same contract to the implementer. |
| X2-B reviewer lens | `cp/x2b` | dcdb3fb | sdd/task-reviewer-prompt.md | Reviewer judges what the brief required, never how it illustrated the work; the plan's file list stops being a requirement. |
| X2-C implementer empowerment | `cp/x2c` | 4b2abd9 | sdd/implementer-prompt.md | Implementer owns the deviation call over the brief's advisory details — not a blocker, not a question — and records it in the report. |
| X3-A reviewer citation rule | `cp/x3a` | b5c931f | sdd/task-reviewer-prompt.md | Every requirement a finding invokes is quoted to its source line; an unquotable requirement is filed Minor as the reviewer's own. |
| X3-B requirements inventory | `cp/x3b` | b670a91 | sdd/implementer-prompt.md, sdd/SKILL.md | Implementer's report traces every implemented requirement to its source and marks unsourced work; controller flags unsourced entries, ledgers them, and names them in the reviewer's dispatch (no bounce-back). |
| X3-C adjudication default | `cp/x3c` | f478a24 | sdd/SKILL.md | A finding invoking an uncited requirement gets no fix round — it is ledgered as a suggestion for the final review. |
| X7-A evidence-bearing preflight | `cp/x7a` | e1cd285 | sdd/SKILL.md | Preflight emits its pairwise checks as a ledger table ("clean" without rows is not a scan) and rules on what it surfaces instead of batching a question. |
| X7-B mechanical consistency check | `cp/x7b` | edd9bcd | sdd/SKILL.md, sdd/scripts/plan-conflict-scan (new) | A script over the plan's Files:/Interfaces: blocks and task code reports delete-vs-still-listed, modify-before-create, consumed-callable-with-no-producer, and in-task call/definition arity mismatches at setup; prose scan covers only what it cannot see; conflicts get rulings. |
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
design) and no measurement vocabulary. Re-run in full after fix rounds 1
and 2; all 17 pass.

**`plan-conflict-scan` (X7-B) validation — measured, from the committed
blob** (`git show cp/x7b:…/plan-conflict-scan`, never the working tree:
round 1's first attempt passed in the working tree while the committed blob
was syntactically broken, an apostrophe having closed the awk program's
quoting).

What the script checks after two fix rounds: delete-vs-still-listed,
modify-before-create, an interface consumed with no producing task (or
produced only later), and a call whose argument count contradicts a
definition in the same task. The `produces X but never writes it` check is
gone. Interfaces register in both real conventions — `name(args) -> type`
and a bare backticked `name` — with dotted forms deduped on their last
segment. Prose cannot register as a call (a paren must touch the name), and
a consumed name is ignored when it is a language builtin, an ALL_CAPS
env-shaped token, a path or `filename.ext`, or a single character.

Every row below carries what the scan actually parsed, so a zero that means
"nothing to check" is visible as such:

| plan | findings | FPs | tasks / file entries / consumed / produced / in-task defs |
|------|----------|-----|-----------------------------------------------------------|
| seeded fixture (5 seeded conflicts) | 5 | 0 | 5 / 9 / 3 / 4 / 6 |
| bare-name fixture (2 seeded, both bare-name) | 2 | 0 | 2 / 3 / 3 / 2 / 2 |
| clean fixture | 0 | 0 | 2 / 4 / 1 / 2 / 2 |
| `superpowers-autoresearch/docs/plans/2026-07-31-cost-pathologies-evals.md` | 0 | 0 | 13 / 16 / 0 / 3 / 0 |
| `superpowers-autoresearch/docs/plans/2026-07-28-codex-efficiency-evals.md` | 5 | 5 | 13 / 33 / 15 / 25 / 10 |
| `_tmp/drew-sdd-head-to-head-2026-07-27/sdd-testing-fresh/awesome-fractals-fcu-opus-5/docs/superpowers/plans/2026-07-14-go-fractals-cli.md` (local corpus, never committed) | 0 | 0 | 7 / 43 / 0 / 4 / 0 |

Seeded true positives all fire: delete-vs-still-listed, modify-before-create,
consumed-produced-later, consumed-with-no-producer, `summarize(rows)` defined
vs `summarize(rows, fmt)` called inside one task, and both bare-name
consumed-with-no-producer conflicts.

**The five false positives on the codex-efficiency plan are three distinct
mechanisms, stated plainly** (verified against the plan text, not inferred):

- `compactions` and `patch_applies` (2 findings) ARE declared inside Task 3's
  `Produces:` block — `docs/plans/2026-07-28-codex-efficiency-evals.md:210-216`
  — as one multi-name field list in a single pair of backticks
  (`` `lines, oversized_lines, compactions, …, patch_applies` ``), which the
  scan's per-identifier tokenizer doesn't decompose. The producer line is read;
  the span inside it is not. Single-name spans in the same block
  (`exec_commands(path) -> list[ExecCmd]`, `parse_session(path)`) register
  fine.
- `patch_apply_end` (2 findings, Tasks 10 and 11) appears only in step text
  and in Consumes lines, never in any task's `Produces:` block — the
  producer-recognition scope question.
- `mutation_events` (1 finding) is the round-1 blind spot: Task 10 consumes a
  helper it implements itself.

Producer recognition is confined to `Produces:` lines by design — widening it
to all backticked names anywhere in a task's body would zero the second and
third out but would also silence real consumed-with-no-producer conflicts
whenever any task merely mentions the name. Decomposing multi-name backtick
spans would zero the first out, at the cost of tokenizing prose that happens
to sit between backticks. Both trades belong in the X7 pre-registration, not
in an unreviewed script change.

**Two plans parsed zero consumed interfaces**, so their zero findings on that
axis prove nothing: the cost-pathologies plan names its inputs in prose plus
one backticked path, and go-fractals names them as unbackticked prose
("Consumes: parsePositive, parseNonNegative, … from Task 1"). Their file-entry
checks (16 and 43 entries) did run. Matching unbackticked prose identifiers
is exactly what produced round 1's noise and is deliberately not attempted.

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

**Owed to the X7 pre-registration — three parser-scope questions.** Each one
decides findings before any run happens, so each needs a stated answer and a
fixture written to match:

1. **Producer recognition.** `Produces:` lines only (today), or every
   backticked name in a task's body? Widening zeroes the `patch_apply_end`
   class of false positive and silences real conflicts whenever a task
   mentions a name in passing.
2. **Prose Consumes lines.** Two of three real plans name their inputs in
   unbackticked prose, which parses to zero consumed interfaces. On plans
   written that way X7-B degrades to a file-collision checker while X7-A
   still does interface work — the fixture's writing convention decides the
   A-vs-B comparison before it runs.
3. **Multi-name backtick spans.** A single pair of backticks holding a
   comma-separated field list (`` `lines, compactions, …, patch_applies` ``)
   registers as nothing, because the tokenizer takes a span whole. Real plans
   declare interfaces this way. Decomposing spans fixes it and starts
   tokenizing whatever prose sits between backticks.

**Shared doctrine text across X8 and X9.** X8-B now carries the full
four-class catastrophic clause verbatim alongside X8-A, X9-A, and X9-B —
the same boundary sentence appears in four arms across two experiments,
because Amendment 2 binds all of them to it. It is doctrine, not any arm's
mechanism, and it sharpens the X8-vs-X9 discriminability problem: an X8 arm
and an X9 arm can both be credited for behavior the shared clause produced.
The battery pre-registration has to say which behaviors it will attribute to
the shared clause and which to the arm-specific text, or the X8/X9 verdicts
cannot be told apart.

**Fix round 2 (re-review).** Three branches amended: X7-B restored bare
backticked identifier matching (the paren-touching rule from round 1 had
made the consume check inert on real plans — the reviewer's two-task
bare-name plan caught zero) behind targeted shape suppressors, and reworded
SKILL.md to match; X1-B and X1-C each amended the Complete-the-task opener,
whose "parked with a ruling at the cap" was the same contradiction class as
round 1's I3. Validation table above rebuilt with counts-checked on every
row.

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
