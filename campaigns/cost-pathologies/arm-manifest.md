# Arm manifest — cost-pathologies campaign

Treatment-arm skill text. Every branch is LOCAL-ONLY in
`/Users/jesse/git/superpowers/superpowers` (never pushed, merged, or PR'd),
cut from `codex-efficiency-fixes` at **329b8f1** and carrying exactly one
commit. Batteries cite the SHA below, not the branch name — branches are
mutable, SHAs are the record.

Controls are the unpatched base (329b8f1): X1-D, X1-F (human-exception),
X2-D, X3-D, X5-C, X6-C, X7-C, X8-C, X9-C. X1-AB is not built; it is gated
on A and B both beating control independently.

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
| X5-A receipts-in-report | `cp/x5a` | d71d307 | sdd/SKILL.md, sdd/implementer-prompt.md | Implementer issues a `LEASE-RECEIPT:` line (command, tree_sha, result) in its report and short status; the controller cites it in a reviewer's or fix-round's dispatch instead of asking for a re-run when the tree_sha is unchanged, marking `LEASE-HONORED:`/`LEASE-INVALIDATED:` into that same dispatch. |
| X5-B machine-checkable receipt file | `cp/x5b` | 644bee6 | sdd/SKILL.md, sdd/implementer-prompt.md | Same receipt grammar, written instead to a dedicated per-task receipts file (`…/task-N-receipts.md`); the controller `cat`/`grep`s the file mechanically before dispatching a reviewer or re-review and appends `LEASE-HONORED:`/`LEASE-INVALIDATED:` to the same file. |
| X6-A batching rule | `cp/x6a` | 2262c91 | sdd/SKILL.md | Several small, independent, same-shape plan tasks are collapsed into one batch dispatch brief and one subagent, instead of one dispatch per task. |
| X6-B inline-when-trivial | `cp/x6b` | f46243f | sdd/SKILL.md | A single mechanical edit needing no new test and no design judgment is made by the controller inline, in its own turn, instead of dispatched; anything touching more than one file, a test, or judgment still gets its own dispatch. |
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
pre-registered exceptions are X9-B, which is X9-A plus surfacing by design,
and X5-A/X5-B, which legitimately share the `LEASE-RECEIPT:`/
`LEASE-HONORED:`/`LEASE-INVALIDATED:` grammar verbatim — that grammar is a
scorer-defined spec both arms must emit, not either arm's own distinctive
phrasing; see Task 11's addendum below) and no measurement vocabulary.
Re-run in full after fix rounds 1 and 2; all 17 pass. X5/X6 (4 more
branches, 21 total) verified the same way in Task 11.

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

---

## Addendum (Task 11, 2026-08-01): X5 and X6 arms — closing the Task 3 gap

Task 6's report flagged that `cp/x5a`, `cp/x5b`, `cp/x6a`, `cp/x6b` were
defined in the design doc but never authored — absent from both this
manifest and Task 3's branch list, "out of [that] task's scope" and left
for whoever owned Task 11's pre-registration. This addendum closes that
gap: the four branches above (rows added to the main table) were authored
the same way as the other 17 — single temporary worktree, cut from
`codex-efficiency-fixes` at 329b8f1, one commit each, local-only.

**The receipt grammar is a spec, not this task's invention.**
`campaigns/cost-pathologies/score_x5_leases.py`'s module docstring (Task 7)
defines the exact three line markers X5-A and X5-B must emit for
`lease_events` to have any signal:

    LEASE-RECEIPT: command=<command_norm> tree_sha=<sha> result=<pass|fail>
    LEASE-HONORED: command=<command_norm> tree_sha=<sha>
    LEASE-INVALIDATED: command=<command_norm> tree_sha=<sha>

case-sensitive, line-anchored (`re.MULTILINE`, `^LEASE-...`). Both arms'
skill text was written to reproduce this grammar verbatim and to say,
every place a line is emitted, that it starts at the very beginning of its
own line with nothing before it — no bullet dash, no backticks — since an
LLM's natural instinct is to wrap a fixed-format token in markdown, which
would break the `^` anchor. Sanity-checked directly against the scorer's
own regex (not just read): constructed sample text shaped like each arm's
instructed output (implementer report, implementer short status, a
controller dispatch citing a receipt, a receipts-file `cat` dump) and
confirmed `_LEASE_LINE_RE` matches all of them with the expected
`command_norm`/`tree_sha`/`result` groups.

**X5-A (`cp/x5a`) — receipts in report/short-status.** The implementer
appends a `LEASE-RECEIPT:` line to its report's Report Format section and
repeats it, on its own trailing line, after its short status list (the
short list's own bullets could not carry it without a leading `- `
prefix breaking the anchor, so the receipt line is pulled out of the list
entirely). The controller cites a matching receipt into the *reviewer's
dispatch* itself (never just the ledger — Task 9's operationalized lesson
is that ledger/progress.md content does not reliably survive capture,
inter-agent dispatch text does) and adds `LEASE-HONORED:`/
`LEASE-INVALIDATED:` to that same dispatch. The fix loop gets its own
paragraph: a fix round moves the tree, so the round's own fresh run is the
only receipt that can cover it — `LEASE-INVALIDATED:` goes into the fix
dispatch itself, and the fix report's fresh `LEASE-RECEIPT:` is what the
re-review dispatch cites.

**X5-B (`cp/x5b`) — machine-checkable receipt file.** Same grammar,
delivered differently: the controller names a per-task receipts file
alongside the report file (`…/task-N-brief.md` → `…/task-N-receipts.md`,
mirroring the existing brief→report naming convention) and the
implementer appends its `LEASE-RECEIPT:` line there instead of the report
or short status. Before composing a reviewer or re-review dispatch, the
controller `cat`s (or `grep LEASE-`s) the file itself — a mechanical read,
not recalled prose — and appends `LEASE-HONORED:`/`LEASE-INVALIDATED:`
back to the file. This is the arm's actual distinguishing mechanism from
X5-A: the same three-line grammar, but the honoring seat's own act of
checking is a tool call over a file (captured as exec-command output in
the scorer's third channel) rather than trusting what it remembers from a
report it already read once.

**X6-A (`cp/x6a`) — batching rule** and **X6-B (`cp/x6b`) —
inline-when-trivial** both land as a single paragraph at the top of "The
Task Loop" (before the existing "Everything you paste into a dispatch
prompt…" paragraph) — the natural gate point before any per-task dispatch
decision fires, mirroring how X1-B/X1-C occupy the same anchor sentence in
different directions. X6-B's boundary ("touches more than one file, needs
a new or updated test, or calls for judgment about approach still gets its
own subagent dispatch — when in doubt, dispatch") is the arm's answer to
the design doc's "explicit boundary so it cannot swallow real tasks."
Neither arm needs the LEASE- grammar; X6 is graded from ordinary dispatch
shape (`score_x6_floor`'s dispatch count/size), not marker lines.

**Verification.** Same automated pass as the other 17 (declared-files-only
diff, one commit, distinctive phrase present, no cross-arm phrase leakage
beyond the disclosed X5-A/X5-B grammar overlap, no measurement
vocabulary) — all 4 pass; see the updated "Verification performed" section
above. Privacy sweep on this addendum and the full manifest diff
(hostnames, emails, API-key patterns, absolute non-repo paths, ticket-ID
shapes): no matches.

## 2026-08-01 rebase — queue campaign base (sim/dev-postmerge)

All 21 arms rebased from 329b8f1 onto `sim/dev-postmerge` (= superpowers
origin/dev @ bb2a34b + no-ff merges of PR heads 7c560e0, e9686d5, 4dc71b1,
3ff8d15 — the "PRs #2059–#2064 landed" assumption; base delta vs 329b8f1
is exactly 433184c's 4 deleted SKILL.md lines). All rebases clean, no
conflicts. `cp/x9a`'s rebased diff retains its original 42ins/19del shape
in `skills/subagent-driven-development/SKILL.md`; per standing rule, its
rebased text is UNGRADED until the X7+X9 composed battery (plan Task 11)
runs. New SHAs (one arm per row, same `| name | \`branch\` | sha |`
column layout as the main table above, so `run-quorum.sh`'s existing
`grep -F`/awk-field-4 arm resolution parses this section too — task 4
of the queue-execution campaign, 2026-08-01, reformatted this table
from a compact 3-arms-per-row layout for exactly this reason; the
runner also prefers this section's rows over the main table's for any
arm present in both, since they physically sort last in the file --
see run-quorum.sh's own comment at the `grep -F` call site):

| arm | branch | sha |
|-----|--------|-----|
| X1-A criterion-backing (rebased) | `cp/x1a` | 89c7684 |
| X1-B rising severity floor (rebased) | `cp/x1b` | b618107 |
| X1-C marginal-value verdict (rebased) | `cp/x1c` | 208dc4d |
| X1-E scoped auto second wave (rebased) | `cp/x1e` | 1c6db05 |
| X1-G hard cap (rebased) | `cp/x1g` | a8df1ff |
| X2-A plan-header contract (rebased) | `cp/x2a` | 03b8f6a |
| X2-B reviewer lens (rebased) | `cp/x2b` | 03a28c5 |
| X2-C implementer empowerment (rebased) | `cp/x2c` | 42ccda2 |
| X3-A reviewer citation rule (rebased) | `cp/x3a` | b25bcd5 |
| X3-B requirements inventory (rebased) | `cp/x3b` | e5654c1 |
| X3-C adjudication default (rebased) | `cp/x3c` | 97ff02b |
| X5-A receipts-in-report (rebased) | `cp/x5a` | 6f0d340 |
| X5-B machine-checkable receipt file (rebased) | `cp/x5b` | 4f456a1 |
| X6-A batching rule (rebased) | `cp/x6a` | d53436b |
| X6-B inline-when-trivial (rebased) | `cp/x6b` | 77f5426 |
| X7-A evidence-bearing preflight (rebased) | `cp/x7a` | ea84cf9 |
| X7-B mechanical consistency check (rebased) | `cp/x7b` | 701a37d |
| X8-A scope-bound approvals (rebased) | `cp/x8a` | a152ce4 |
| X8-B approval-ledger discipline (rebased) | `cp/x8b` | 14c13b1 |
| X9-A rule-log-proceed (rebased) | `cp/x9a` | 61bf701 |
| X9-B rule-log-proceed + async surfacing (rebased) | `cp/x9b` | 85a8c90 |

## 2026-08-01 composed arm — cp/x7x9a (queue campaign Task 11)

The composed arm merges X7-A's evidence-bearing preflight (the scan now
produces a table — one row per task-pair sharing a file/interface, one row
per task's internal self-consistency — written to the ledger before any
ruling) with X9-A's never-stall doctrine (plan conflicts, ambiguities, and
BLOCKED-class findings are ruled on and ledgered rather than escalated to
the human, with only four hard-stop classes — irreversible/destructive
actions, security-sensitive actions, out-of-worktree side effects like
merge/push/publish, and totally-broken plans — left as genuine stop
conditions). The one textual overlap between the two arms (both rewrote
the preflight scan's closing paragraph) was resolved by ordering rather
than rewording: x7a's table-format mandate and ruling sentence bracket
x9a's "rule on everything you find... if clean, proceed without comment"
clause, so the table is established as unconditional (produced while
scanning, before the outcome is known) and x9a's "without comment" reads
as no extra narration needed beyond the ledgered table — not as permission
to skip it. Verification (declared-files-only, phrase presence ×2 per
parent, line-count reconciliation to the union, word-multiset no-stray-
vocabulary, no upstream): task-11-arm-report.md in the campaign workspace.

| Branch | Description | SHA |
|---|---|---|
| `cp/x7x9a` | X7-A preflight + X9-A never-stall composed | 5303307 |

## 2026-08-02 backlog campaign — x9a2 (escape-hatch tightening)

cp/x9a2 = cp/x9a (61bf701) + tightened escape-hatch clause at its three
sites (stop-list paragraph, process-digraph node, adjudication paragraph):
a ruling you can write down is not a guess; confirm-asks on rulings
already made are stalls. +11/−6, one file (SDD SKILL.md).

| Branch | Description | SHA |
|---|---|---|
| `cp/x9a2` | X9-A + escape-hatch tightening | f42d72a |

## 2026-08-03 backlog campaign — x11 (verification dedupe, controller seat)

cp/x11 = sim/dev-postmerge (1fed99d) + "Verification is read, not re-run"
paragraph at the top of SDD's Handle-the-report section (controller and
reviewer never repeat a suite on an unchanged commit; three re-run
exceptions) + one rationalization-table row. +11/−0, one file.
Motivated by T8's X5 narratives: duplicate verification concentrates at
the controller seat (3-14 pytest reruns/rep), reviewers already decline.

| Branch | Description | SHA |
|---|---|---|
| `cp/x11` | verification-dedupe (controller seat) | d6cb918 |

## 2026-08-03 backlog campaign — x10a/x10b (final-review consistency)

cp/x10a = sim/dev-postmerge + one checklist sentence in the Final Review
dispatch guidance (cross-module consistency lens: one name per concept,
single-definition constants, uniform error formats, symmetric shared
value sets). +4/−1 lines, one file.

cp/x10b = sim/dev-postmerge + bundled
skills/subagent-driven-development/scripts/consistency-scan (vendored
from campaigns/cost-pathologies/x10-consistency-scan.py @ 53722a5 with
the header/usage strings sanitized of campaign vocabulary — drift rule:
logic changes must touch both copies or state why not) + Final Review
instruction to run it and hand the output file to the final reviewer as
verification candidates. One file modified, one script added.

| Branch | Description | SHA |
|---|---|---|
| `cp/x10a` | final-review consistency checklist line | 11b1433 |
| `cp/x10b` | final-review mechanical consistency scan | 4447922 |

## 2026-08-03 plan-decomposition campaign — pd-p1 / pd-p2 / pd-p1p2

pd/p1 (alias cp/pd-p1) = sim/dev-postmerge + plan-as-directory:
writing-plans emits `plan.md` (header + task index with Files/Depends
columns) + `tasks/NN-<slug>.md` one per task, one write per file; SDD
consumes task files directly as briefs and holds only plan.md in
controller context. +40/−8 across writing-plans and SDD SKILL.md.

pd/p2 (alias cp/pd-p2) = cp/x7a (evidence-bearing preflight, ea84cf9)
+ coherence extension: preflight table gains one row per shared NAME
pinned by multiple tasks with each task's exact value; rulings applied
as PLAN AMENDMENTS (edit the losing task's text, commit) before Task 1.
+14/−4 in SDD SKILL.md on top of x7a.

pd/p1p2 (alias cp/pd-p1p2) = pd/p2 + pd/p1 cherry-picked + composition
fix: the preflight scan is the controller's ONE pass through task files.

| Branch | Description | SHA |
|---|---|---|
| `cp/pd-p1` | plan-as-directory | ee0c6b0 |
| `cp/pd-p2` | plan-time coherence-amendment gate (incl. x7a) | 292da9c |
| `cp/pd-p1p2` | composed | 1a1a8fd |

## 2026-08-03 plan-decomposition iteration — pd-p1b

pd/p1b (alias cp/pd-p1b) = sim/dev-postmerge + incremental single-file
plan authoring in writing-plans: spine (header + constraints + full
task index) written first, then one task-section append per response
with a spine re-read before each, index↔section reconciliation at the
end. Rationale: the return-window constraint binds per WRITE, not per
FILE — this keeps the monolith's whole-plan view while removing the
single-write ceiling. +15/−0, one file.

| Branch | Description | SHA |
|---|---|---|
| `cp/pd-p1b` | incremental-monolith plan authoring | 831fbfd |

## 2026-08-03 plan-decomposition iteration — pd-p2s (spec-anchored coherence)

pd/p2s (alias cp/pd-p2s) = pd/p2 (292da9c) + spec-anchored value rows:
each shared-name row starts from the SPEC's value when one exists (plan
majority otherwise); spec divergence is a defect regardless of the
task's own argument; specless coherence rulings declared provisional in
ledger + finish report. Direct counter to the ground-truth gap
(P2-on-cp-x10 verdict).

| Branch | Description | SHA |
|---|---|---|
| `cp/pd-p2s` | spec-anchored coherence gate | 1937691 |

## 2026-08-04 plan-decomposition iteration — pd-d1p (tree-identity dedupe)

pd/d1p (alias cp/pd-d1p) = sim/dev-postmerge + interrogation-derived
fix for the X11 null: evidence follows the TREE not the commit ID;
mechanical identity check (`git diff --quiet <tested-commit> HEAD`)
before any re-run; post-merge habit named verbatim in the
rationalization table. Derived from 4/4 convergent elicitations of the
X11 re-runners (Jesse's interrogate-then-fix method).

| Branch | Description | SHA |
|---|---|---|
| `cp/pd-d1p` | tree-identity verification dedupe | f2c425c |

## 2026-08-04 plan-decomposition iteration — pd-x12 (invariant-instance enumeration)

pd/x12 (alias cp/pd-x12) = sim/dev-postmerge + interrogation-derived
fix for the X1-edit reviewer escapes: sdd/task-reviewer-prompt.md's
spec-compliance section gains a mechanical procedure — when a
requirement states an invariant, enumerate every instance of its
anchor (grep the constant/guard/call) and give each instance its own
file:line verdict; one verified instance is not evidence for its
siblings; proximity is not the check; green proves only what tests
encode. Derived from 4/4 convergent elicitations of the X1-edit
reviewers (single-instance generalization). Distinct from the failed
x1a/b/c arms: those were review-POLICY exhortations; this is a
mechanical enumeration procedure in the sessions' own elicited terms —
so the battery doubles as a test of the interrogation method.

| Branch | Description | SHA |
|---|---|---|
| `cp/pd-x12` | invariant-instance enumeration (task-reviewer seat) | ae2b457 |

## 2026-08-04 plan-decomposition iteration — pd-p2g (green-as-waiver counter, p2s')

pd/p2g (alias cp/pd-p2g) = cp/pd-p2s (1937691) + the elicited
green-as-waiver counter, in the dismissing sessions' own terms: a clean
merge and green suite close no coherence rows (no test asserts
cross-module agreement); "intentional"/"inconsequential" are rulings
you WRITE, never impressions a passing suite hands you; diverging rows
stay open until a written ruling resolves them. One scan-block
paragraph + one rationalization row. The method-scope test: three
hand-written texts failed specless (control, P2, p2s) — does the
sessions' own elicited counter do better, or is missing authority
beyond any text's reach?

| Branch | Description | SHA |
|---|---|---|
| `cp/pd-p2g` | green-as-waiver counter (specless coherence) | c5fd8ba |

## 2026-08-04 plan-decomposition iteration — pd-d1s (structural evidence lease) and pd-x13 (illegibility row)

pd/d1s (alias cp/pd-d1s) = sim/dev-postmerge + d1p's successor per its
uptake verdict (2/4): the identity check moves from prose into the
process artifact — scripts/review-package prints a `TEST-EVIDENCE:`
lease (tree sha + the exact `git diff --quiet <head> HEAD -- .`
command) after every package; SKILL.md's DONE step and a
rationalization row point at the lease instead of restating the
doctrine. Files: sdd/scripts/review-package, sdd/SKILL.md.

pd/x13 (alias cp/pd-x13) = sim/dev-postmerge + the 5/5 elicited
counter from the X5 evidence-illegibility class, in
sdd/task-reviewer-prompt.md's Tests block: evidence you cannot see is
not evidence that doesn't exist — re-read at the stated path or report
the gap; re-running to regenerate what you failed to read is not
verification.

| Branch | Description | SHA |
|---|---|---|
| `cp/pd-d1s` | structural evidence lease (review-package emits) | f4af30b |
| `cp/pd-x13` | illegibility is not invalidation (reviewer seat) | 24da35d |

## 2026-08-05 plan-decomposition iteration — pd-k1 (knowledge-forwarding handoff)

pd/k1 (alias cp/pd-k1) = sim/dev-postmerge + append-only
`<workspace>/handoff.md`: SKILL.md's dispatch-contents list gains item
(6) (handoff path, read-before-work / append-at-report, created empty
before Task 1); implementer-prompt.md reads the handoff after the brief
and appends a `## Task N` block (2-5 lines: working test command,
environment quirks, binding decisions) before writing the report. Both
hooks sit at moments implementers already attend to (dispatch text,
report step) — the x13-class placement, not the x12-class.

| Branch | Description | SHA |
|---|---|---|
| `cp/pd-k1` | append-only handoff knowledge-forwarding | 76884ac |

## 2026-08-05 plan-decomposition synthesis — pd-ship (composed ship texts)

pd/ship (alias cp/pd-ship) = sim/dev-postmerge + the campaign's ship
set verbatim: #2086's two texts (writing-plans `**Spec:**` header line;
SDD setup "If the plan names a Spec, read that too… rulings without one
are provisional") + PR #2089's x13 paragraph (task-reviewer
illegibility row). Purpose: battery-run-verbatim status for #2086's
glue text + co-presence regression check.

| Branch | Description | SHA |
|---|---|---|
| `cp/pd-ship` | composed ship texts (#2086 + x13) | 1c95520 |

## 2026-08-05 adjudication battery — NEW BASE sim/dev2 + r1t/rebut/composed

**Base retarget:** `sim/dev2` @ fb518ed = current origin/dev with the
merged 2026-08-04 stack (#2059-2062, #2077, #2078, #2080) + #2090.
Prior baselines (1fed99d era) do NOT transfer — the stack changes SDD
behavior (batching, evidence-bearing preflight, rule-and-continue);
this battery carries its own base2 controls.

pd/r1t (alias cp/r1t) = sim/dev2 + one Calibration sentence in
sdd/task-reviewer-prompt.md: structure-conformance divergences
(behavior preserved) are Minor with file:line, ride the ledger to
final-review cleanup triage, never block the loop alone. From the R1
micro (guard 8/8 under every policy; downgrade 6/8 compliance).

cp/rebut = sim/dev2 + the serf after-action package in sdd/SKILL.md
(REAL-SESSION provenance, ~/after-action-rebut-with-evidence.md):
(a) breaker's contestable-finding bullet — runtime claims are ruled by
RUNS (falsifiability statement first, the finding's own proposed test
preferred, hostile execution on unmodified code, expected-green guard
commit, discriminating observable in the ledger entry, re-flag of an
evidence-parked class = hard stop to human); (b) per-round ledger
class/severity tags + convergence guidance (decay = keep going, flat
3-round repetition = structural-dedupe mandate or early
evidence-adjudication; early adjudication without the run stays
forbidden).

cp/r1t-rebut = both.

| Branch | Description | SHA |
|---|---|---|
| `sim/dev2` | new base (origin/dev fb518ed) | fb518ed |
| `cp/r1t` | structure-conformance triage sentence | 08972e6 |
| `cp/rebut` | evidence-adjudication package | 52df997 |
| `cp/r1t-rebut` | composed | 77ec054 |
