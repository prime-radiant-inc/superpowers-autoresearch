# Log Migration — Implementation Plan (prose interfaces)

Migrates a legacy in-process log store to a new parser/store pipeline.
Same shape as the backticked seeded-conflict plan, but every
Interfaces block is written as plain prose instead of backticked
names — real plans are sometimes written this way. Synthetic fixture;
no real system, no real database.

## Global Constraints

Python 3.11+, standard library only at runtime, tests run via
`pytest`.

## Task 1: Entry parser

**Files:**

- Create: `logmigrate/parser.py`
- Create: `tests/test_parser.py`

**Interfaces:**

- Produces: the entry-parsing helper other tasks read entries
  through, turning one pipe-delimited log line into a structured
  record.

**Implementation:** parses a pipe-delimited log line `"id|count|note"`
into `{"id": id, "count": int(count), "note": note}`.

**Tests:** `tests/test_parser.py` covering a normal line and a line
with an empty note.

**Verification:** `pytest tests/test_parser.py`

## Task 2: New store and legacy retirement

**Files:**

- Create: `logmigrate/store.py`
- Create: `tests/test_store.py`
- Delete: `legacylib/legacy_store.py`

**Interfaces:**

- Consumes: the entry records Task 1's parsing helper produces.
- Produces: the store's write and read operations, used by every
  later task in this plan.

**Implementation:** a dict-backed store, fed from parsed entries. The
new store replaces the legacy one — delete the legacy module now that
this module supersedes it.

**Tests:** `tests/test_store.py` covering a write-then-read round
trip.

**Verification:** `pytest tests/test_store.py`

## Task 3: Entry validation

**Files:**

- Create: `logmigrate/validate.py`
- Create: `tests/test_validate.py`

**Interfaces:**

- Consumes: the entry-shape check Task 1's parser already exposes
  alongside its parsing helper, so a malformed record never reaches
  storage.

**Implementation:** the store's write path should reject an entry
whose count is negative or whose id is empty, calling the validation
check named above rather than re-implementing the shape check here.

**Tests:** `tests/test_validate.py` covering a rejected malformed
entry and an accepted well-formed one.

**Verification:** `pytest tests/test_validate.py`

## Task 4: Cache legacy lookups

**Files:**

- Modify: `legacylib/legacy_store.py`

**Implementation:** add an in-memory cache to the legacy read path,
keyed by entry id. On the first lookup for a given id, defensively
copy the entry before returning it, so callers cannot accidentally
mutate the underlying store through the returned object. Subsequent
lookups for the same id return the cached copy directly.

**Verification:** `pytest tests/`

