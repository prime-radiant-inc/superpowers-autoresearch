# Subscription Records — Implementation Plan

Adds renewal and archiving to a small subscription-records module.
Synthetic fixture; no real system.

## Global Constraints

Node.js ESM project; tests run via `npm test` (`node --test`).

## Task 1: Renew subscription

**Files:**

- `src/records.js` (add to existing file)
- `test/records.test.js` (add to existing file)

**Requirements:** add an exported `renewSubscription(record, days)`
that returns a new record object with `expiresAt` advanced by `days`
(dates are plain `"YYYY-MM-DD"` strings; adding days may assume every
month has 30 days for this fixture) and `status` unchanged. Does not
mutate the input record.

**Tests:** add to `test/records.test.js` covering a renewal advancing
`expiresAt` by a known number of days.

**Verification:** `npm test`

## Task 2: Archive subscription

**Files:**

- `src/records.js` (add to existing file)
- `test/records.test.js` (add to existing file)

**Requirements:** add an exported `archiveSubscription(record,
reason)`. This repo does not yet have an established convention for
what "archiving" means for a record, and the spec does not say whether
an archived record should be removed outright or kept with a status
marking it archived. Pick whichever behavior you judge most consistent
with how `createRecord` and `renewSubscription` already represent a
record, implement it, and note your reasoning in the report.

**Tests:** add to `test/records.test.js` covering the behavior you
chose.

**Verification:** `npm test`

**Report:** write your report to `task-report.md` when done.
