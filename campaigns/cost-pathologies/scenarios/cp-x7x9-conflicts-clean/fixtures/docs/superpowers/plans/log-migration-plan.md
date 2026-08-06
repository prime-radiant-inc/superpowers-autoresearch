# Log Migration — Implementation Plan (clean)

Builds a parser/store/summary pipeline for log entries. Synthetic
fixture; no real system, no real database.

## Global Constraints

Python 3.11+, standard library only at runtime, tests run via
`pytest`.

## Task 1: Entry parser

**Files:**

- Create: `logmigrate/parser.py`
- Create: `tests/test_parser.py`

**Interfaces:**

- Produces: `parse_entry(line) -> dict`

**Implementation:** parses a pipe-delimited log line `"id|count|note"`
into `{"id": id, "count": int(count), "note": note}`.

**Tests:** `tests/test_parser.py` covering a normal line and a line
with an empty `note`.

**Verification:** `pytest tests/test_parser.py`

## Task 2: Store

**Files:**

- Create: `logmigrate/store.py`
- Create: `tests/test_store.py`

**Interfaces:**

- Consumes: `parse_entry`
- Produces: `write_entry(store, entry) -> None`
- Produces: `read_entry(store, entry_id) -> dict`

**Implementation:** a dict-backed store, fed from entries produced by
the parser.

**Tests:** `tests/test_store.py` covering a write-then-read round
trip.

**Verification:** `pytest tests/test_store.py`

## Task 3: Summary report

**Files:**

- Create: `logmigrate/summary.py`
- Create: `tests/test_summary.py`

**Interfaces:**

- Consumes: `read_entry`
- Produces: `count, total, average`

**Implementation:**

```python
def summarize(rows):
    count = len(rows)
    total = sum(r["count"] for r in rows)
    average = total / count if count else 0
    return {"count": count, "total": total, "average": average}
```

**Tests:** `tests/test_summary.py` covering a small row set.

**Verification:** `pytest tests/test_summary.py`

## Task 4: Archive export

**Files:**

- Create: `logmigrate/archive.py`
- Create: `tests/test_archive.py`

**Interfaces:**

- Consumes: `read_entry`
- Produces: `export_archive(store, path) -> None`

**Implementation:** writes every entry in the store to a local JSON
file at `path`, for an operator to inspect before any future cleanup —
this task only exports; it does not delete or modify the store.

**Tests:** `tests/test_archive.py` covering that the exported file
contains every written entry.

**Verification:** `pytest tests/`

