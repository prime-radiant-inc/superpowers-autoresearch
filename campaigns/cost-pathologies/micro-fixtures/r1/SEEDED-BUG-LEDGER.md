# R1 mixed fixture — seeded-bug ledger

Not session-visible: this file lives outside `mixed/` and is never read by
`r1-review-micro.py`'s `pack_tree`/`build_user_message` (which glob only
`package.json`, `src/reports/*.js`, `test/report.test.js`, and
`task-report.md` inside the tree directory). It exists purely so the
grading/`REAL_BUG_RE` design and any future hand-rescoring has ground
truth without it leaking into what the reviewer subagent sees.

## The tree

`mixed/` is `../x2b/deviant/` (the structural-deviation tree: three files
instead of the plan's four, `aggregate.js`+`format.js` merged into
`summarize.js`) with one additional, independent defect seeded into
`summarize.js`.

## The seeded bug

`formatSummaryCsv` (`mixed/src/reports/summarize.js`) filters out
zero-amount categories before rendering CSV rows:

```js
export function formatSummaryCsv(totals) {
  return [
    "category,amount",
    ...sortedEntries(totals)
      .filter(([, amount]) => amount !== 0)   // <-- seeded bug
      .map(([category, amount]) => `${category},${amount}`),
  ]
    .join("\n");
}
```

`formatSummary` (the plain-text renderer) has no such filter and includes
every category regardless of total. The plan
(`campaigns/cost-pathologies/micro-fixtures/x2b/plan.md`, Task 2) requires
`formatSummaryCsv` to use "the same category/amount pairs `formatSummary`
uses" — a category whose entries net to zero (e.g. a charge and an equal
refund in the same category) silently disappears from the CSV output
while still appearing in the text summary. This is a real, demonstrable
behavior bug, not a style nit:

```
$ node -e '...formatSummary({travel:150, meals:0})...'
formatSummary:    "meals: 0\ntravel: 150"
formatSummaryCsv: "category,amount\ntravel,150"   # meals silently dropped
```

`mixed/test/report.test.js` is byte-identical to `x2b/deviant`'s test
file and does not exercise a zero-amount category, so `npm test` reports
6/6 passing in the tree as shipped — the bug is real but uncaught by the
existing suite, matching the "failing edge case the plan requires"
framing: the plan's requirement is violated, but no committed test
currently proves it. `mixed/task-report.md` is unchanged from
`x2b/deviant/task-report.md` (same claims, same 6/6): the implementer is
not aware of this defect, so nothing in session-visible content
discloses it. A reviewer can only find it by reading `summarize.js`
against the plan's Task 2 requirement, which is exactly the judgment
this battery measures.

## What this fixture is for

R1 asks whether a review-triage policy (suppress / downgrade / cleanup-
wave) that successfully quiets structure-only noise on `x2b/deviant`
also, as a side effect, buries a REAL defect when one is present in the
same tree. `mixed--<policy>` cells carry both the pre-existing structural
deviation (from `deviant`) and this seeded bug simultaneously. The guard
metric: does `formatSummaryCsv`'s zero-amount bug still land in a
blocking section (Critical/Important) under every policy, or does some
policy's triage machinery catch it in the same net as the structural
finding and downgrade/suppress/reroute it too?

Synthetic fixture; no real system.
