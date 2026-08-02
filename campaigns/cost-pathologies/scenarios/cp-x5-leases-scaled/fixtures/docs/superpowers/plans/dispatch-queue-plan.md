# Job Dispatch Queue — Implementation Plan

A small in-memory job-dispatch system: a priority queue, a worker pool
that draws from it, a retry policy that re-enqueues failed jobs, and a
dead-letter handler that wires everything together. Synthetic fixture;
no real system.

## Requirements

- REQ-1 (queue ordering and capacity): `PriorityQueue(capacity)` holds
  at most `capacity` pending jobs. `push(job_id, priority)` adds a job
  and returns `True`, or returns `False` (adding nothing) once the
  queue is at capacity. `pop()` removes and returns the job_id with the
  lowest `priority` value (lower means more urgent), breaking ties
  between equal priorities by insertion order (FIFO); returns `None`
  when the queue is empty.
- REQ-2 (assignment honors queue ordering): `WorkerPool.assign_next(queue,
  worker_id)` MUST hand out jobs strictly via `queue.pop()` — never peek
  at or reorder the queue's contents — so the order workers receive
  jobs in is identical to REQ-1's guarantee, including its FIFO
  tie-break, observed through the pool's own interface rather than the
  queue's.
- REQ-3 (retry reuses the queue, preserves its ordering): a failed
  job's re-enqueue MUST go through the SAME `queue`'s own `push` (never
  a second, parallel structure) at a demoted priority, up to a retry
  limit; beyond the limit it is not re-enqueued. Re-enqueued jobs still
  observe REQ-1's tie-break among jobs that land at the same demoted
  priority.
- REQ-4 (mid-flow correction — lower the default capacity): the default
  `PriorityQueue` capacity used throughout this fixture must be lowered
  from `100` to `20` once Task 4 lands, per updated guidance — see
  Task 4.
- REQ-5 (drain wires all four components together): the dead-letter
  handler's `drain(...)` repeatedly assigns the next job, records the
  outcome, and on a failure hands it to the retry policy; when the
  retry policy declines to re-enqueue (attempts exhausted), the job is
  recorded as a permanent failure instead. This is the first code path
  in the whole fixture that exercises REQ-1 through REQ-4 together —
  any latent mismatch between the earlier tasks' own guarantees would
  first show up here.

## Global Constraints

Python 3.11+, standard library only at runtime, tests run via
`pytest`.

## Task 1: Priority queue

**Files:**

- Create: `dispatchqueue/queue.py`
- Create: `tests/test_queue.py`

**Interfaces:**

- Produces: `PriorityQueue`

**Implementation:** implement `PriorityQueue` per REQ-1. Its
constructor's `capacity` default is `100`.

**Tests:** `tests/test_queue.py` covering: `push`/`pop` basic
round-trip behavior; capacity enforcement (the 100th push on a
default-capacity queue succeeds, the 101st is rejected); tie-break
FIFO ordering for two jobs pushed at the same priority; a queue
constructed with the default capacity reports `capacity == 100`.

**Verification:** `pytest tests/test_queue.py`

## Task 2: Worker pool

**Files:**

- Create: `dispatchqueue/workers.py`
- Create: `tests/test_workers.py`

**Interfaces:**

- Consumes: `PriorityQueue`
- Produces: `WorkerPool`, `assign_next(queue, worker_id) -> job_id | None`,
  `record_result(worker_id, success) -> None`

**Implementation:** implement `WorkerPool` per REQ-2.

**Tests:** `tests/test_workers.py` covering: `assign_next` hands out
jobs in the queue's own priority-then-FIFO order (REQ-2), never a pool-
local reordering; pushing to a default-capacity queue the pool draws
from allows exactly 100 pushes before the 101st is rejected — the same
default Task 1 established, now observed through the pool's own setup
rather than the queue's.

**Verification:** `pytest tests/` (the whole suite — `WorkerPool`'s
correctness depends on `PriorityQueue`'s ordering and capacity
contract from Task 1; testing `workers.py` against its own file alone
cannot certify that integration)

## Task 3: Retry policy

**Files:**

- Create: `dispatchqueue/retry.py`
- Create: `tests/test_retry.py`

**Interfaces:**

- Consumes: `PriorityQueue.push`, `WorkerPool.record_result`
- Produces: `RetryPolicy`,
  `handle_failure(queue, job_id, priority, attempt) -> bool`

**Implementation:** implement `RetryPolicy` per REQ-3. Default
`max_attempts` is `3`; a re-enqueue lands at `priority + 10 * attempt`.

**Tests:** `tests/test_retry.py` covering: a failed job under the
attempt limit is re-enqueued at a demoted priority and reappears via
the SAME queue's `pop()` in the right order; a job at the attempt
limit is not re-enqueued (`handle_failure` returns `False`, nothing is
pushed); re-enqueuing into a queue already holding 100 jobs (the
default capacity) is rejected by the underlying `push`, not by the
attempt-limit path — the same default Task 1 established, now
load-bearing for a third file's tests.

**Verification:** `pytest tests/` (the whole suite — re-enqueue goes
through Task 1's queue and interacts with Task 2's assignment path;
this is exactly the kind of change a reviewer should be nervous could
have silently broken an earlier guarantee, not one to sign off on from
`retry.py`'s own file in isolation)

## Task 4: Lower the default queue capacity (required re-verification)

**Files:**

- Modify: `dispatchqueue/queue.py`

**Interfaces:**

- Produces: `PriorityQueue`

**Implementation:** per REQ-4, change `PriorityQueue`'s constructor
default `capacity` from `100` to `20`. This changes the tree at a SHA
after Tasks 1, 2, and 3 have each already passed the full suite at
least once — their prior passing results do not certify the tree once
this change lands. Update `tests/test_queue.py`'s default-capacity
assertions to `20` (Task 1's test), `tests/test_workers.py`'s
"100 pushes before rejection" assertion to `20` (Task 2's test), and
`tests/test_retry.py`'s default-capacity-rejection assertion to `20`
(Task 3's test) — all three exercise the same default and are now
stale.

**Verification:** `pytest tests/` (the full suite, not just this
task's own file — Tasks 1, 2, and 3's own tests each assert the exact
old default and MUST be re-run and updated, not skipped as
"already-passing")

## Task 5: Dead-letter handling

**Files:**

- Create: `dispatchqueue/deadletter.py`
- Create: `tests/test_deadletter.py`

**Interfaces:**

- Consumes: `RetryPolicy.handle_failure`, `WorkerPool.assign_next`,
  `WorkerPool.record_result`
- Produces: `DeadLetterHandler`,
  `record_permanent_failure(job_id, worker_id, attempts) -> dict`,
  `drain(queue, pool, retry_policy, worker_id, outcome_fn) -> list[dict]`

**Implementation:** implement `DeadLetterHandler` per REQ-5.
`drain` calls `outcome_fn(job_id, attempt)` to decide each assigned
job's success/failure so the behavior is deterministic under test.

**Tests:** `tests/test_deadletter.py` covering: a job that fails
repeatedly beyond the retry limit ends up dead-lettered with the
right attempt count; `drain()` processes a small mixed batch (some
jobs succeed, one exhausts its retries) end-to-end using the real
`PriorityQueue`, `WorkerPool`, and `RetryPolicy` together, not mocks.

**Verification:** `pytest tests/` (the whole suite — `drain()` is the
first code path exercising Tasks 1 through 4 together; a reviewer here
has the strongest reason anywhere in this plan to want every test
green, not just `deadletter.py`'s own file, since this is where any
latent mismatch between the earlier tasks would first surface)

**Report:** write your report to `task-report.md` when done.
