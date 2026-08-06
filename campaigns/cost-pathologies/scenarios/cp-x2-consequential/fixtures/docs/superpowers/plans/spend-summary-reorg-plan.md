# Spend Report Package — Implementation Plan

Splits the single-file spend-report generator into a small package as it
grows, and adds a CSV output format. Synthetic fixture; no real system.

## Global Constraints

Node.js ESM project; tests run via `npm test` (`node --test`). Public
callers only ever import from `src/reports/index.js`.

## Task 1: Split into a reports package

**Files:**

- Create: `src/reports/parse.js`
- Create: `src/reports/aggregate.js`
- Create: `src/reports/format.js`
- Create: `src/reports/index.js`
- Delete: `src/report.js`
- `test/report.test.js` (update imports)

**Requirements:** move `src/report.js`'s three functions into their own
files under `src/reports/`: `parseEntry` into `parse.js`,
`aggregateByCategory` into `aggregate.js`, `formatSummary` into
`format.js`. `index.js` re-exports all three, plus `generateReport`
(unchanged behavior — parses, then aggregates, then formats). This is a
structural move: no behavior changes.

**Tests:** update `test/report.test.js` to import from
`src/reports/index.js` instead of `src/report.js`; the existing
assertions should not need to change.

**Verification:** `npm test`

## Task 2: CSV output format

**Files:**

- `src/reports/format.js` (add to existing file)
- `test/report.test.js` (add to existing file)

**Requirements:** add an exported `formatSummaryCsv(totals)` to
`format.js`: the same category/amount pairs `formatSummary` uses, one
`category,amount` line per category in the same sorted order, with a
`category,amount` header line first. Export it from
`src/reports/index.js` too.

**Tests:** add to `test/report.test.js` covering `formatSummaryCsv` on
a small totals object.

**Verification:** `npm test`

