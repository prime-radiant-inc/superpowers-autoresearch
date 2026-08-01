# Seeded-truth ledger — cp-x6-smalledits

Answer key for X6's arms (Task 11). NEVER surfaced to the Coding-Agent
or the Gauntlet-Agent. Everything here is synthetic.

Per the design doc: "Problem: dispatching an agent costs a context
floor regardless of task size. FULL (fixture with a dozen small edits,
cost per completed edit per arm; quality guard: all edits reviewed and
correct)."

## The twelve seeds

Twelve independent files under `util/`, each with exactly one small,
mechanical bug (an off-by-one, a swapped return value, a missing line,
a wrong constant), documented in-line with a `// BUG: ...` comment and
listed in `BUGS.md`. Verified: with the fixture as committed, `npm
test` reports 14 failing / 1 passing out of 15 total assertions (one
file, `isPalindrome.js`, has two tests; only one demonstrates its bug —
the other passes both before and after the fix, which is expected and
not itself a signal). Every one of the twelve files has at least one
failing test tied to its seeded bug, confirmed by running the suite
against the fixture as committed (not inferred).

**Why independent matters:** no file imports another under `util/`,
and no test imports more than one `util/` module — fixing any one bug
cannot break or interact with any other. This is deliberate: the
pathology under study is dispatch/context overhead per unit of work,
not any cross-file coordination cost, so the fixture must not
introduce a coordination cost that would confound the measurement.

## What is NOT measured here (checks.sh stays behavior-neutral)

`checks.sh` asserts only that `npm test` passes at the end (the
quality guard: "all edits reviewed and correct") and does not assert
anything about HOW the work got done — no assertion on subagent
dispatch count, on `Agent`/`Task` tool-call count, on inline-edit
count, or on any batching shape. That is exactly what Task 11's
scorer and the arms (X6-A batching rule, X6-B inline-when-trivial,
X6-C control) are for: whether the controller dispatches one subagent
per file (twelve dispatches, twelve context floors), batches all
twelve into one subagent brief, or does some/all of the work inline
without dispatching at all.

## Guard

"quality guard: all edits reviewed and correct" — an arm that
"wins" on dispatch cost by leaving any of the twelve tests failing, or
by breaking a DIFFERENT file while fixing one (there should be no way
to do this given the files are independent, per above), fails
regardless of its cost number.
