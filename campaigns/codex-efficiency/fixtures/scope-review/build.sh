#!/usr/bin/env bash
# Hand-authored review-input fixture for cx-scope-review (E5, Task 12).
#
# Builds a small git repo in the current working directory: a `main`
# baseline (thread-safe producer/consumer queue) and a `feature` branch
# (checked out at the end, ready to review "before we merge") carrying 3
# commits that add a batch API on top of it. This is the review's INPUT
# (a hand-authored branch), not skill output -- same convention as
# fixtures/branch-review/build.sh (Task 8).
#
# THREE defects are planted, each requiring a DIFFERENT review scope to
# catch -- see out/e5-defect-key.md for exact file:line + detection
# rubric per defect. A fourth (D4) is not planted here; it emerges live,
# from whatever the coding agent's mid-session repair does (see
# scenarios/cx-scope-review/story.md).
#
#   D1 (local/task scope) -- mtqueue/batch.py's DEFAULT_BATCH_SIZE is 1,
#      not the 5 docs/BATCH.md documents. Unit-testable: the shipped
#      suite's own test_batch.py::test_drain_batch_default_pulls_documented_batch_size
#      is RED against this branch (drain_batch() with no explicit size
#      returns 1 item, not 5) -- catchable by running `pytest`/reading
#      just the new batch.py commit, no cross-referencing needed.
#
#   D2 (cross-task/cross-commit scope) -- mtqueue/queue.py's new
#      peek_batch() method (added in the same commit as D1) reads
#      self._items directly, with no `with self._lock:` -- unlike every
#      other SharedQueue method, and unlike the thread-safety CONTRACT
#      docs/DESIGN.md establishes on `main`, BEFORE the feature branch
#      exists. Catching this requires reading the feature branch's new
#      method against a convention established in an earlier
#      commit/task, not just the isolated diff. The shipped test suite
#      exercises peek_batch()/preview() only sequentially (no concurrent
#      thread hits it), so it stays green despite the race -- same
#      "passes cleanly, only a code read catches it" shape as
#      fixtures/branch-review's two seeds.
#
#   D3 (clean-checkout scope) -- mtqueue/batch_codec.py imports msgpack,
#      which is not in pyproject.toml's dependencies. docs/DEV_SETUP.md
#      documents the gap as a TODO the author never did. A clean
#      checkout (this eval container's own Python, which has no msgpack
#      preinstalled) hits a real ModuleNotFoundError the moment anything
#      imports batch_codec or collects tests/test_batch_codec.py -- not
#      a simulated failure, an actual one, verifiable by literally
#      trying to run the suite in this environment.
#
# Assumes the caller has already `cd`-ed into the target workdir; this
# script only runs `git`/file-writing commands against the current
# directory, matching the other codex-efficiency scenario setup.sh
# scripts' convention.
set -euo pipefail

git init -qb main
git config user.email "drill@test.local"
git config user.name "Drill Test"

# --- main: baseline (thread-safe queue + producer/consumer wrappers) ----
mkdir -p mtqueue tests docs

cat > mtqueue/__init__.py <<'PY'
"""mtqueue: a small thread-safe producer/consumer queue (skeleton)."""
PY

cat > mtqueue/queue.py <<'PY'
"""Thread-safe shared queue for a producer/consumer pipeline."""
import collections
import threading


class SharedQueue:
    """A FIFO queue safe for concurrent producer/consumer access.

    Every method that reads or mutates the internal deque acquires
    `self._lock` for the duration of the operation -- this is the
    queue's core thread-safety contract (see docs/DESIGN.md).
    """

    def __init__(self):
        self._items = collections.deque()
        self._lock = threading.Lock()

    def push(self, item):
        """Append item to the queue. Thread-safe."""
        with self._lock:
            self._items.append(item)

    def pop_nowait(self):
        """Remove and return the oldest item, or None if empty. Thread-safe."""
        with self._lock:
            if not self._items:
                return None
            return self._items.popleft()

    def __len__(self):
        with self._lock:
            return len(self._items)
PY

cat > mtqueue/producer.py <<'PY'
"""Producer wrapper around SharedQueue."""


class Producer:
    """Pushes items onto a SharedQueue."""

    def __init__(self, queue):
        self.queue = queue

    def produce(self, item):
        """Push a single item onto the queue."""
        self.queue.push(item)
PY

cat > mtqueue/consumer.py <<'PY'
"""Consumer wrapper around SharedQueue."""


class Consumer:
    """Pops items off a SharedQueue."""

    def __init__(self, queue):
        self.queue = queue

    def consume(self):
        """Pop and return a single item, or None if the queue is empty."""
        return self.queue.pop_nowait()
PY

cat > tests/test_queue.py <<'PY'
import threading

from mtqueue.queue import SharedQueue


def test_push_then_pop_fifo_order():
    q = SharedQueue()
    q.push("a")
    q.push("b")
    assert q.pop_nowait() == "a"
    assert q.pop_nowait() == "b"


def test_pop_empty_returns_none():
    q = SharedQueue()
    assert q.pop_nowait() is None


def test_len_reflects_pending_items():
    q = SharedQueue()
    assert len(q) == 0
    q.push("x")
    assert len(q) == 1


def test_concurrent_push_pop_preserves_all_items():
    """Smoke test for the queue's core thread-safety contract
    (docs/DESIGN.md): N producer threads each push M items; after they
    finish, exactly N*M items are poppable, none lost or duplicated."""
    q = SharedQueue()
    n_threads, n_items = 8, 50

    def produce(offset):
        for i in range(n_items):
            q.push((offset, i))

    threads = [threading.Thread(target=produce, args=(t,)) for t in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    seen = []
    while len(q):
        seen.append(q.pop_nowait())
    assert len(seen) == n_threads * n_items
    assert len(set(seen)) == n_threads * n_items
PY

cat > docs/DESIGN.md <<'MD'
# mtqueue -- design notes

## Thread-safety contract

`SharedQueue` wraps a `collections.deque` guarded by a single
`threading.Lock` (`self._lock`). **Every method that reads or mutates
the internal deque must acquire `self._lock` for the duration of the
operation** -- this is the queue's only thread-safety guarantee, and the
whole point of the class: a `deque` is not safe for concurrent
iteration/mutation across threads without external locking (mutating it
from one thread while another iterates it can raise `RuntimeError:
deque mutated during iteration`, or silently produce a torn read).

Any new method added to `SharedQueue` that reads `self._items` (whether
or not it also mutates it) must acquire `self._lock` first, exactly like
the existing methods, or it reintroduces the exact race this design
exists to prevent.
MD

cat > pyproject.toml <<'TOML'
[project]
name = "mtqueue"
version = "0.1.0"
description = "A small thread-safe producer/consumer queue (skeleton)."
requires-python = ">=3.9"
dependencies = []

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[tool.pytest.ini_options]
# One test module failing to IMPORT must not hide every other test
# module's results -- established here, on main, before the feature
# branch (with its own import-time break, D3) exists.
addopts = "--continue-on-collection-errors"
TOML

cat > README.md <<'MD'
# mtqueue

A small thread-safe producer/consumer queue library.

## Development

```bash
pip install -e .
pytest tests/
```

See [docs/DESIGN.md](docs/DESIGN.md) for the thread-safety contract.
MD

git add mtqueue README.md pyproject.toml docs/DESIGN.md tests/test_queue.py
git commit -qm "initial: mtqueue thread-safe queue + producer/consumer skeleton"

git checkout -qb feature

# --- feature commit 1: batch core (D1 + D2) -----------------------------
cat > mtqueue/queue.py <<'PY'
"""Thread-safe shared queue for a producer/consumer pipeline."""
import collections
import itertools
import threading


class SharedQueue:
    """A FIFO queue safe for concurrent producer/consumer access.

    Every method that reads or mutates the internal deque acquires
    `self._lock` for the duration of the operation -- this is the
    queue's core thread-safety contract (see docs/DESIGN.md).
    """

    def __init__(self):
        self._items = collections.deque()
        self._lock = threading.Lock()

    def push(self, item):
        """Append item to the queue. Thread-safe."""
        with self._lock:
            self._items.append(item)

    def pop_nowait(self):
        """Remove and return the oldest item, or None if empty. Thread-safe."""
        with self._lock:
            if not self._items:
                return None
            return self._items.popleft()

    def peek_batch(self, n):
        """Return up to n oldest items without removing them, oldest
        first. Read-only -- does not mutate the queue."""
        return list(itertools.islice(self._items, n))

    def __len__(self):
        with self._lock:
            return len(self._items)
PY

cat > mtqueue/batch.py <<'PY'
"""Batch draining helpers layered on top of SharedQueue."""

DEFAULT_BATCH_SIZE = 1  # see docs/BATCH.md -- documented default is 5


def drain_batch(queue, max_items=DEFAULT_BATCH_SIZE):
    """Pop up to max_items from queue in one call, oldest first, stopping
    early if the queue empties. Defaults to DEFAULT_BATCH_SIZE items per
    docs/BATCH.md.
    """
    items = []
    for _ in range(max_items):
        item = queue.pop_nowait()
        if item is None:
            break
        items.append(item)
    return items
PY

git add mtqueue/queue.py mtqueue/batch.py
git commit -qm "feat: add batch draining core (drain_batch, SharedQueue.peek_batch)"

# --- feature commit 2: batch codec + producer/consumer integration -----
cat > mtqueue/batch_codec.py <<'PY'
"""Wire encoding for batches of queue items, for the network transport
layer (see docs/DEV_SETUP.md for the msgpack dependency note)."""
import msgpack


def encode_batch(items):
    """Serialize a list of items to bytes for network transport."""
    return msgpack.packb(items, use_bin_type=True)


def decode_batch(data):
    """Deserialize bytes produced by encode_batch back into a list."""
    return msgpack.unpackb(data, raw=False)
PY

cat > mtqueue/producer.py <<'PY'
"""Producer wrapper around SharedQueue."""


class Producer:
    """Pushes items onto a SharedQueue."""

    def __init__(self, queue):
        self.queue = queue

    def produce(self, item):
        """Push a single item onto the queue."""
        self.queue.push(item)


class BatchProducer(Producer):
    """Producer with a bulk-push convenience method."""

    def push_many(self, items):
        """Push every item in items onto the queue, one at a time (each
        push is independently thread-safe via SharedQueue.push)."""
        for item in items:
            self.produce(item)
PY

cat > mtqueue/consumer.py <<'PY'
"""Consumer wrapper around SharedQueue."""


class Consumer:
    """Pops items off a SharedQueue."""

    def __init__(self, queue):
        self.queue = queue

    def consume(self):
        """Pop and return a single item, or None if the queue is empty."""
        return self.queue.pop_nowait()


class BatchConsumer(Consumer):
    """Consumer with a batch-preview convenience method."""

    def preview(self, n):
        """Return up to n pending items without removing them, for a
        caller that wants to inspect what's next before consuming it."""
        return self.queue.peek_batch(n)
PY

git add mtqueue/batch_codec.py mtqueue/producer.py mtqueue/consumer.py
git commit -qm "feat: add batch wire codec and producer/consumer batch wrappers"

# --- feature commit 3: tests + docs -------------------------------------
cat > tests/test_batch.py <<'PY'
from mtqueue.batch import drain_batch
from mtqueue.queue import SharedQueue


def test_drain_batch_pops_up_to_max_items():
    q = SharedQueue()
    for i in range(5):
        q.push(i)
    assert drain_batch(q, max_items=3) == [0, 1, 2]
    assert len(q) == 2


def test_drain_batch_stops_early_on_empty_queue():
    q = SharedQueue()
    q.push("only")
    assert drain_batch(q, max_items=5) == ["only"]


def test_drain_batch_default_pulls_documented_batch_size():
    """docs/BATCH.md documents drain_batch's default as 5 items per call
    when max_items is omitted."""
    q = SharedQueue()
    for i in range(8):
        q.push(i)
    assert drain_batch(q) == [0, 1, 2, 3, 4]
PY

cat > tests/test_batch_codec.py <<'PY'
from mtqueue.batch_codec import decode_batch, encode_batch


def test_roundtrip_preserves_items():
    items = [{"id": 1, "label": "a"}, {"id": 2, "label": "b"}]
    assert decode_batch(encode_batch(items)) == items
PY

cat > tests/test_producer_consumer_batch.py <<'PY'
from mtqueue.consumer import BatchConsumer
from mtqueue.producer import BatchProducer
from mtqueue.queue import SharedQueue


def test_push_many_enqueues_all_items():
    q = SharedQueue()
    BatchProducer(q).push_many([1, 2, 3])
    assert len(q) == 3


def test_preview_does_not_remove_items():
    q = SharedQueue()
    for i in range(3):
        q.push(i)
    consumer = BatchConsumer(q)
    assert consumer.preview(2) == [0, 1]
    assert len(q) == 3  # preview must not consume
PY

cat > docs/BATCH.md <<'MD'
# mtqueue -- batch API

## `drain_batch(queue, max_items=DEFAULT_BATCH_SIZE)`

Pops up to `max_items` items from the queue in one call, oldest first,
stopping early if the queue runs out. **Documented default: 5 items per
call** when `max_items` is omitted -- callers doing bulk draining
without an explicit batch size should get a reasonably-sized batch, not
a single item at a time (that would defeat the point of a "batch" API).

## `SharedQueue.peek_batch(n)` / `BatchConsumer.preview(n)`

Returns up to `n` pending items without removing them. Like every other
`SharedQueue` method, this must honor the queue's thread-safety contract
(docs/DESIGN.md): read-only access to the internal deque still needs
`self._lock`, since a concurrent `push()`/`pop_nowait()` from another
thread can mutate the deque mid-iteration otherwise.
MD

cat > docs/DEV_SETUP.md <<'MD'
# mtqueue -- dev environment notes

This repo's shared dev sandbox already has a few convenience packages
preinstalled from other projects on the same box, so local test runs may
pass even for a dependency this project hasn't formally declared yet.

- `msgpack` -- `batch_codec.py`'s wire encoding uses it. **TODO before
  merge: add `msgpack` to `pyproject.toml`'s `[project.dependencies]`**
  -- right now it only imports successfully here because of the
  preinstalled shared venv, not because the project declares it. A
  clean checkout (fresh venv, `pip install -e .`, nothing preinstalled)
  will hit `ModuleNotFoundError: No module named 'msgpack'` the moment
  anything imports `batch_codec`.
MD

git add tests/test_batch.py tests/test_batch_codec.py tests/test_producer_consumer_batch.py docs/BATCH.md docs/DEV_SETUP.md
git commit -qm "test+docs: batch API tests, BATCH.md, dev-setup msgpack note"
