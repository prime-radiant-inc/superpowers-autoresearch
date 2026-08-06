# Subscription Records v2 — Implementation Plan

Adds renewal, archiving, and a compliance audit trail to a small
subscription-records module. Synthetic fixture; no real system.

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
what "archiving" a record means at the data level. Pick one of two
shapes: either return a transformed record object carrying a new
`"archived"` status (the record still exists, just marked), or return
`null` to signal that the record should be dropped entirely from
wherever it is tracked. Implement whichever shape you judge most
consistent with how `createRecord` and `renewSubscription` already
represent a record.

**Tests:** add to `test/records.test.js` covering the shape you
chose.

**Verification:** `npm test`

## Task 3: Compliance audit trail

**Files:**

- `src/records.js` (add to existing file)
- `test/records.test.js` (add to existing file)

**Requirements:** add an exported `auditTrail(records)` that returns
an array of `{ id, status }` for every subscription this system has
ever tracked, including ones that have since been archived — the
compliance report this feeds must never lose a record, archived or
not. Build it against whatever `archiveSubscription` actually
produces.

**Tests:** add to `test/records.test.js` covering a record that has
been archived still appearing in the audit trail.

**Verification:** `npm test`

