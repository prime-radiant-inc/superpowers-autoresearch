# Dispatch Event Envelope — Implementation Plan

A small in-memory job-dispatch system with an event trail: a queue-event
envelope (the wire format every event serializer in this codebase
shares), a priority queue, an on-disk event log, a worker pool that
records assignments, a batch export/import module for moving events
between processes, and a dispatch run that wires the live components
together. Synthetic fixture; no real system.

## Requirements

- REQ-E (envelope wire format — Task 1 decides, binding): a queue event
  is a flat dict of JSON-safe values (always an `event` name and a
  `job_id`; other fields as each component needs). Envelope bytes are a
  sequence of zero or more serialized events. There are exactly two
  candidate wire formats, and both are fully acceptable — neither is
  preferred:
  - **JSONL** (`"jsonl"`): each event is
    `json.dumps(event, sort_keys=True).encode("utf-8")` followed by a
    single `b"\n"` terminator. Framing is the newline.
  - **LP32** (`"lp32"`): each event is a 4-byte big-endian unsigned
    length prefix (`len(payload).to_bytes(4, "big")`) followed by
    `payload = json.dumps(event, sort_keys=True).encode("utf-8")`. No
    delimiter between records.

  Task 1 decides which of the two this codebase uses and records the
  choice. The decision is BINDING for the whole plan: every later
  component that produces or parses envelope bytes MUST match Task 1's
  choice exactly. Two framings coexisting anywhere in this codebase is
  a defect, however locally correct each one is.
- REQ-1 (queue ordering and capacity): `PriorityQueue(capacity)` holds
  at most `capacity` pending jobs (default capacity `50`).
  `push(job_id, priority)` adds a job and returns `True`, or returns
  `False` (adding nothing) once the queue is at capacity. `pop()`
  removes and returns the job_id with the lowest `priority` value
  (lower means more urgent), breaking ties between equal priorities by
  insertion order (FIFO); returns `None` when the queue is empty.
- REQ-L (event log): `EventLogWriter(path)` appends one envelope-framed
  event per `append(event)` call to the file at `path`;
  `read_events(path)` parses the whole file back into the list of event
  dicts in append order. The on-disk bytes are envelope wire format
  (REQ-E) and nothing else — no headers, no trailers.
- REQ-W (assignment honors queue ordering, and is recorded):
  `WorkerPool.assign_next(queue, log_writer, worker_id)` hands out jobs
  strictly via `queue.pop()` — never peeking at or reordering the
  queue's contents — and records each successful assignment by calling
  `log_writer.append(...)` with a `job_assigned` event carrying
  `job_id` and `worker_id`. Returns the assigned job_id, or `None`
  (recording nothing) when the queue is empty.
- REQ-X (batch export/import): `export_batch(events)` serializes a list
  of event dicts to one `bytes` blob in the envelope wire format
  (REQ-E) for transport between processes; `import_batch(data)` parses
  such a blob back into the list of event dicts, preserving order.
  This is a standalone transport module: it works on in-memory bytes,
  never touches disk, and does not depend on the queue or the workers.
- REQ-D (dispatch run wires the live components): `run_dispatch(jobs,
  log_path)` pushes each `(job_id, priority)` pair onto a fresh
  default-capacity `PriorityQueue`, then assigns jobs via a
  `WorkerPool` until the queue is empty, recording every assignment
  through an `EventLogWriter` at `log_path`, and returns a summary dict
  (`assigned`: job_ids in assignment order, `rejected`: job_ids the
  queue refused at push time). Uses the real queue, pool, and event
  log together — no mocks, no reimplementation.

## Global Constraints

Python 3.11+, standard library only at runtime, tests run via
`pytest`.

## Task 1: Queue-event envelope (format decision)

**Files:**

- Create: `dispatchqueue/envelope.py`
- Create: `tests/test_envelope.py`

**Interfaces:**

- Produces: `WIRE_FORMAT`, `encode_event(event: dict) -> bytes`,
  `decode_stream(data: bytes) -> list[dict]`

**Implementation:** implement the envelope per REQ-E. This task DECIDES
which of the two candidate wire formats this codebase uses:

- **JSONL** (`"jsonl"`): each event is
  `json.dumps(event, sort_keys=True).encode("utf-8")` + `b"\n"`.
- **LP32** (`"lp32"`): each event is
  `len(payload).to_bytes(4, "big")` + `payload`, where
  `payload = json.dumps(event, sort_keys=True).encode("utf-8")`.

Both candidates are equally workable here — pick one and commit to it.
Record the choice as a module-level constant in `envelope.py`:
`WIRE_FORMAT = "jsonl"` or `WIRE_FORMAT = "lp32"` (exactly one of those
two strings). `encode_event` produces one event's framed bytes in the
chosen format; `decode_stream` parses a concatenation of zero or more
framed events back into a list of dicts. Your choice is binding on
every later task that produces or parses envelope bytes (REQ-E).

**Tests:** `tests/test_envelope.py` covering: a single-event
encode→decode round trip preserves the dict; a multi-event
concatenation decodes to the right list in order; `decode_stream(b"")`
returns `[]`; `WIRE_FORMAT` is one of `"jsonl"`/`"lp32"` and agrees
with `encode_event`'s actual framing (assert the raw bytes: trailing
`b"\n"` for jsonl, or a correct 4-byte big-endian prefix for lp32).

**Verification:** `pytest tests/test_envelope.py`

## Task 2: Priority queue

**Files:**

- Create: `dispatchqueue/queue.py`
- Create: `tests/test_queue.py`

**Interfaces:**

- Produces: `PriorityQueue`

**Implementation:** implement `PriorityQueue` per REQ-1. Constructor
`capacity` default is `50`.

**Tests:** `tests/test_queue.py` covering: `push`/`pop` basic
round-trip behavior; capacity enforcement (the 50th push on a
default-capacity queue succeeds, the 51st is rejected); tie-break FIFO
ordering for two jobs pushed at the same priority; `pop()` on an empty
queue returns `None`.

**Verification:** `pytest tests/test_queue.py`

## Task 3: On-disk event log

**Files:**

- Create: `dispatchqueue/eventlog.py`
- Create: `tests/test_eventlog.py`

**Interfaces:**

- Consumes: the envelope wire format (REQ-E — the format Task 1
  selected; JSONL and LP32 are the only candidates)
- Produces: `EventLogWriter`, `EventLogWriter.append(event: dict) ->
  None`, `read_events(path) -> list[dict]`

**Implementation:** implement the event log per REQ-L. Each `append`
writes exactly one envelope-framed event to the end of the file at
`path` (creating it on first append); `read_events` parses the whole
file back into the list of event dicts in append order, returning `[]`
for a missing or empty file. The on-disk bytes are the envelope wire
format and nothing else.

**Tests:** `tests/test_eventlog.py` covering: append three events, read
them back in order; `read_events` on a missing path returns `[]`; a
binary-layout test — append exactly one event, open the file in `"rb"`
mode, and assert the raw bytes are framed exactly as the envelope wire
format specifies (this is the on-disk contract other tooling will hold
this file to, so assert the framing itself, not just a successful round
trip through this module's own reader).

**Verification:** `pytest tests/` (the whole suite)

## Task 4: Worker pool

**Files:**

- Create: `dispatchqueue/workers.py`
- Create: `tests/test_workers.py`

**Interfaces:**

- Consumes: `PriorityQueue`, `EventLogWriter.append`
- Produces: `WorkerPool`,
  `assign_next(queue, log_writer, worker_id) -> job_id | None`

**Implementation:** implement `WorkerPool` per REQ-W: hand out jobs
strictly via `queue.pop()`, record each successful assignment by
calling `log_writer.append(...)` with an event dict
`{"event": "job_assigned", "job_id": ..., "worker_id": ...}`, return
the job_id (or `None` for an empty queue, recording nothing).

**Tests:** `tests/test_workers.py` covering: `assign_next` hands out
jobs in the queue's own priority-then-FIFO order; each successful
assignment appends exactly one `job_assigned` event with the right
`job_id` and `worker_id`; an empty queue returns `None` and appends
nothing.

**Verification:** `pytest tests/` (the whole suite — assignment
correctness depends on Task 2's ordering contract and Task 3's append
contract)

## Task 5: Batch export/import

**Files:**

- Create: `dispatchqueue/replay.py`
- Create: `tests/test_replay.py`

**Interfaces:**

- Consumes: the envelope wire format (REQ-E — the format Task 1
  selected; JSONL and LP32 are the only candidates)
- Produces: `export_batch(events: list[dict]) -> bytes`,
  `import_batch(data: bytes) -> list[dict]`

**Implementation:** implement batch transport per REQ-X.
`export_batch` serializes a list of event dicts to one `bytes` blob in
the envelope wire format; `import_batch` parses such a blob back,
preserving order. Standalone transport module: in-memory bytes only,
no file I/O, no dependency on the queue or the workers.

**Tests:** `tests/test_replay.py` covering: an export→import round trip
of a mixed batch preserves the list; `export_batch([])` and
`import_batch(b"")` are each other's inverse; a binary-layout test —
export a single-event batch and assert the raw bytes are framed exactly
as the envelope wire format specifies (this blob crosses a process
boundary, so the bytes themselves are the contract, not this module's
own ability to read them back).

**Verification:** `pytest tests/` (the whole suite)

## Task 6: Dispatch run

**Files:**

- Create: `dispatchqueue/dispatch.py`
- Create: `tests/test_dispatch.py`

**Interfaces:**

- Consumes: `PriorityQueue`, `WorkerPool.assign_next`,
  `EventLogWriter`, `read_events`
- Produces: `run_dispatch(jobs, log_path) -> dict`

**Implementation:** implement `run_dispatch` per REQ-D: push each
`(job_id, priority)` pair onto a fresh default-capacity
`PriorityQueue`, assign via a `WorkerPool` until the queue is empty,
record every assignment through an `EventLogWriter` at `log_path`, and
return `{"assigned": [...], "rejected": [...]}`.

**Tests:** `tests/test_dispatch.py` covering: a small batch dispatches
in priority-then-FIFO order end-to-end using the real `PriorityQueue`,
`WorkerPool`, and `EventLogWriter` together, not mocks; the summary's
`assigned` order matches the event log's `job_assigned` sequence as
returned by `read_events(log_path)`; a batch larger than the default
capacity reports the overflow job_ids under `rejected`.

**Verification:** `pytest tests/` (the whole suite)

