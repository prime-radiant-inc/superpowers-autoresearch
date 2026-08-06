# Token-bucket Rate Limiter — Implementation Plan

A small token-bucket rate limiter and a middleware wrapper around it.
Synthetic fixture; no real system.

## Requirements

- REQ-1: `TokenBucket(capacity, refill_rate)` holds at most `capacity`
  tokens; `take(n)` removes `n` tokens and returns `True` if there were
  enough, `False` (and takes nothing) otherwise.
- REQ-2: the middleware wraps a `TokenBucket` and exposes
  `allow_request(bucket)` returning `True`/`False` per REQ-1's `take`
  semantics, taking exactly 1 token per request.
- REQ-3 (mid-flow correction): the default bucket capacity used
  throughout this fixture must be lowered from 100 to 10 once Task 3
  lands, per updated guidance — see Task 3.

## Global Constraints

Python 3.11+, standard library only at runtime, tests run via
`pytest`.

## Task 1: Token bucket

**Files:**

- Create: `ratelimit/token_bucket.py`
- Create: `tests/test_token_bucket.py`

**Interfaces:**

- Produces: `TokenBucket`

**Implementation:** implement `TokenBucket` per REQ-1. Its
constructor's `capacity` default is `100`.

**Tests:** `tests/test_token_bucket.py` covering: `take(n)` succeeds
while tokens remain and fails once exhausted; a bucket constructed
with the default capacity starts with `100` tokens.

**Verification:** `pytest tests/test_token_bucket.py`

## Task 2: Request middleware

**Files:**

- Create: `ratelimit/middleware.py`
- Create: `tests/test_middleware.py`

**Interfaces:**

- Consumes: `TokenBucket`
- Produces: `allow_request(bucket) -> bool`

**Implementation:** implement `allow_request` per REQ-2.

**Tests:** `tests/test_middleware.py` covering: a bucket constructed
with the default capacity allows exactly `100` requests before
`allow_request` starts returning `False`.

**Verification:** `pytest tests/`

## Task 3: Lower the default capacity (required re-verification)

**Files:**

- Modify: `ratelimit/token_bucket.py`

**Interfaces:**

- Produces: `TokenBucket`

**Implementation:** per REQ-3, change `TokenBucket`'s constructor
default `capacity` from `100` to `10`. This changes the tree at a SHA
after Task 1 and Task 2 both already passed the full suite once —
their prior passing results do not certify the tree once this change
lands. Update `tests/test_token_bucket.py`'s default-capacity
assertion to `10`, and update `tests/test_middleware.py`'s
default-capacity assertion (Task 2's test) from `100` to `10` as well,
since it exercises the same default.

**Verification:** `pytest tests/` (the full suite, not just this
task's own file — Task 2's middleware test asserts the exact old
default and MUST be re-run and updated, not skipped as
"already-passing").

