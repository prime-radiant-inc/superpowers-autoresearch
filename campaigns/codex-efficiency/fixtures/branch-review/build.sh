#!/usr/bin/env bash
# Hand-authored review-input fixture for cx-branch-review (E2 FULL, Task 8).
#
# Builds a small git repo in the current working directory: a `main`
# baseline (2 files) and a `feature` branch (checked out at the end, ready
# to review "before we merge") carrying 4 commits across 4 concerns --
# core logic, CLI, tests, docs -- roughly 450 changed lines total. This is
# the review's INPUT (a hand-authored branch), not skill output -- see
# task-8-brief.md Step 1.
#
# Two issues are seeded, each catchable only by actually reading the code
# (not by running the shipped test suite, which passes cleanly against
# both):
#   1. Missing edge-case test -- taskqueue/queue.py's dequeue_batch(n) is
#      correctly implemented for n > len(queue) (it returns whatever is
#      left instead of raising, per its own docstring), but
#      tests/test_queue.py never exercises that path -- no test calls
#      dequeue_batch with n greater than the number of enqueued items, or
#      on an empty queue.
#   2. Docstring/behavior mismatch -- taskqueue/queue.py's peek() docstring
#      (and docs/DESIGN.md) says it "Returns None if the queue is empty",
#      but the implementation indexes the heap directly with no empty
#      check, so it raises IndexError instead. tests/test_queue.py only
#      calls peek() on a non-empty queue, so the shipped suite stays green.
#
# Assumes the caller has already `cd`-ed into the target workdir; this
# script only runs `git`/file-writing commands against the current
# directory, matching the other codex-efficiency scenario setup.sh
# scripts' convention (e.g. writing-plans-no-spec-conversational/setup.sh).
set -euo pipefail

git init -qb main
git config user.email "drill@test.local"
git config user.name "Drill Test"

# --- main: baseline skeleton -------------------------------------------
mkdir -p taskqueue
cat > taskqueue/__init__.py <<'PY'
"""taskqueue: a small priority queue package (skeleton)."""
PY

cat > README.md <<'MD'
# taskqueue

A small priority queue package (skeleton). See `docs/` once the queue
implementation lands.
MD

git add taskqueue/__init__.py README.md
git commit -qm "initial: taskqueue skeleton"

git checkout -qb feature

# --- feature commit 1: core logic ---------------------------------------
cat > taskqueue/validators.py <<'PY'
"""Input validation helpers for the taskqueue package."""


def validate_priority(priority):
    """Validate that priority is a non-negative integer.

    Raises TypeError if priority is not an int, ValueError if negative.
    """
    if not isinstance(priority, int) or isinstance(priority, bool):
        raise TypeError(f"priority must be an int, got {type(priority).__name__}")
    if priority < 0:
        raise ValueError("priority must be non-negative")


def validate_label(label):
    """Validate that label is a non-empty string.

    Raises TypeError if label is not a string, ValueError if empty/blank.
    """
    if not isinstance(label, str):
        raise TypeError(f"label must be a str, got {type(label).__name__}")
    if not label.strip():
        raise ValueError("label must not be empty")
PY

cat > taskqueue/queue.py <<'PY'
"""Priority queue with batch dequeue support."""
import heapq
import itertools

from .validators import validate_label, validate_priority


class PriorityQueue:
    """A min-heap priority queue of (priority, label) items.

    Lower priority values are dequeued first. Ties are broken by insertion
    order (FIFO among equal priorities).
    """

    def __init__(self):
        self._heap = []
        self._counter = itertools.count()

    def __len__(self):
        return len(self._heap)

    def is_empty(self):
        """Return True if the queue has no items."""
        return len(self._heap) == 0

    def enqueue(self, label, priority):
        """Add an item with the given label and priority.

        Raises TypeError/ValueError (via validators.py) if label or
        priority is invalid.
        """
        validate_label(label)
        validate_priority(priority)
        heapq.heappush(self._heap, (priority, next(self._counter), label))

    def dequeue(self):
        """Remove and return the highest-priority (lowest-value) label.

        Raises IndexError if the queue is empty.
        """
        if not self._heap:
            raise IndexError("dequeue from an empty PriorityQueue")
        _, _, label = heapq.heappop(self._heap)
        return label

    def dequeue_batch(self, n):
        """Remove and return up to n items in priority order (highest
        priority first). If the queue has fewer than n items, returns all
        remaining items without raising.
        """
        if n < 0:
            raise ValueError("n must be non-negative")
        result = []
        for _ in range(n):
            if not self._heap:
                break
            result.append(self.dequeue())
        return result

    def peek(self):
        """Return the highest-priority label without removing it.

        Returns None if the queue is empty.
        """
        return self._heap[0][2]

    def to_list(self):
        """Return all items as (priority, label) tuples, sorted by
        priority. Does not modify the queue."""
        return [(priority, label) for priority, _, label in sorted(self._heap)]
PY

git add taskqueue/validators.py taskqueue/queue.py
git commit -qm "feat: add PriorityQueue core with validation"

# --- feature commit 2: CLI wrapper --------------------------------------
cat > taskqueue/cli.py <<'PY'
"""Command-line wrapper around taskqueue.PriorityQueue, persisted to a JSON
file (list of [priority, label] pairs) between invocations."""
import argparse
import json
import sys
from pathlib import Path

from .queue import PriorityQueue

DEFAULT_STORE = "queue.json"


def _load(store_path):
    q = PriorityQueue()
    path = Path(store_path)
    if path.exists():
        for priority, label in json.loads(path.read_text()):
            q.enqueue(label, priority)
    return q


def _save(q, store_path):
    Path(store_path).write_text(json.dumps(q.to_list()))


def cmd_add(args):
    q = _load(args.store)
    q.enqueue(args.label, args.priority)
    _save(q, args.store)
    print(f"added {args.label!r} at priority {args.priority}")


def cmd_list(args):
    q = _load(args.store)
    if q.is_empty():
        print("(queue is empty)")
        return
    for priority, label in q.to_list():
        print(f"{priority}\t{label}")


def cmd_pop(args):
    q = _load(args.store)
    items = q.dequeue_batch(args.n)
    _save(q, args.store)
    if not items:
        print("(nothing to pop)")
        return
    for label in items:
        print(label)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="taskqueue", description="Priority task queue CLI"
    )
    parser.add_argument(
        "--store", default=DEFAULT_STORE,
        help="JSON store file (default: %(default)s)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="add an item")
    p_add.add_argument("label")
    p_add.add_argument("priority", type=int)
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="list all items, priority order")
    p_list.set_defaults(func=cmd_list)

    p_pop = sub.add_parser("pop", help="pop up to N items, priority order")
    p_pop.add_argument("-n", type=int, default=1)
    p_pop.set_defaults(func=cmd_pop)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
PY

cat > taskqueue/__main__.py <<'PY'
"""Entry point: python -m taskqueue"""
import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
PY

git add taskqueue/cli.py taskqueue/__main__.py
git commit -qm "feat: add CLI wrapper for queue operations"

# --- feature commit 3: tests ---------------------------------------------
mkdir -p tests
cat > tests/test_validators.py <<'PY'
import pytest

from taskqueue.validators import validate_label, validate_priority


def test_validate_priority_accepts_non_negative_int():
    validate_priority(0)
    validate_priority(5)


def test_validate_priority_rejects_negative():
    with pytest.raises(ValueError):
        validate_priority(-1)


def test_validate_priority_rejects_non_int():
    with pytest.raises(TypeError):
        validate_priority("high")


def test_validate_priority_rejects_bool():
    with pytest.raises(TypeError):
        validate_priority(True)


def test_validate_label_accepts_non_empty_string():
    validate_label("ship it")


def test_validate_label_rejects_non_string():
    with pytest.raises(TypeError):
        validate_label(123)


def test_validate_label_rejects_blank():
    with pytest.raises(ValueError):
        validate_label("   ")
PY

cat > tests/test_queue.py <<'PY'
import pytest

from taskqueue.queue import PriorityQueue


def test_enqueue_dequeue_priority_order():
    q = PriorityQueue()
    q.enqueue("low", 5)
    q.enqueue("high", 1)
    q.enqueue("mid", 3)
    assert q.dequeue() == "high"
    assert q.dequeue() == "mid"
    assert q.dequeue() == "low"


def test_dequeue_ties_broken_fifo():
    q = PriorityQueue()
    q.enqueue("first", 1)
    q.enqueue("second", 1)
    assert q.dequeue() == "first"
    assert q.dequeue() == "second"


def test_dequeue_empty_raises():
    q = PriorityQueue()
    with pytest.raises(IndexError):
        q.dequeue()


def test_is_empty_and_len():
    q = PriorityQueue()
    assert q.is_empty()
    assert len(q) == 0
    q.enqueue("a", 1)
    assert not q.is_empty()
    assert len(q) == 1


def test_dequeue_batch_returns_up_to_n_in_priority_order():
    q = PriorityQueue()
    q.enqueue("c", 3)
    q.enqueue("a", 1)
    q.enqueue("b", 2)
    assert q.dequeue_batch(2) == ["a", "b"]
    assert len(q) == 1


def test_dequeue_batch_negative_n_raises():
    q = PriorityQueue()
    with pytest.raises(ValueError):
        q.dequeue_batch(-1)


def test_peek_returns_highest_priority_without_removing():
    q = PriorityQueue()
    q.enqueue("low", 5)
    q.enqueue("high", 1)
    assert q.peek() == "high"
    assert len(q) == 2  # peek does not remove


def test_to_list_sorted_by_priority():
    q = PriorityQueue()
    q.enqueue("low", 5)
    q.enqueue("high", 1)
    assert q.to_list() == [(1, "high"), (5, "low")]


def test_enqueue_rejects_invalid_priority():
    q = PriorityQueue()
    with pytest.raises(ValueError):
        q.enqueue("x", -1)


def test_enqueue_rejects_invalid_label():
    q = PriorityQueue()
    with pytest.raises(ValueError):
        q.enqueue("", 1)
PY

cat > tests/test_cli.py <<'PY'
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def run_cli(tmp_path, *args):
    store = tmp_path / "queue.json"
    result = subprocess.run(
        [sys.executable, "-m", "taskqueue", "--store", str(store), *args],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    return result, store


def test_add_then_list(tmp_path):
    result, _ = run_cli(tmp_path, "add", "write-report", "2")
    assert result.returncode == 0
    assert "added 'write-report'" in result.stdout
    result2, _ = run_cli(tmp_path, "list")
    assert "write-report" in result2.stdout


def test_list_empty_queue(tmp_path):
    result, _ = run_cli(tmp_path, "list")
    assert result.returncode == 0
    assert "(queue is empty)" in result.stdout


def test_pop_returns_highest_priority_first(tmp_path):
    run_cli(tmp_path, "add", "low", "5")
    run_cli(tmp_path, "add", "high", "1")
    result, _ = run_cli(tmp_path, "pop")
    assert result.returncode == 0
    assert result.stdout.strip() == "high"


def test_pop_n_returns_multiple(tmp_path):
    run_cli(tmp_path, "add", "a", "3")
    run_cli(tmp_path, "add", "b", "1")
    run_cli(tmp_path, "add", "c", "2")
    result, _ = run_cli(tmp_path, "pop", "-n", "2")
    assert result.returncode == 0
    assert result.stdout.splitlines() == ["b", "c"]


def test_add_rejects_negative_priority(tmp_path):
    result, _ = run_cli(tmp_path, "add", "x", "-1")
    assert result.returncode != 0
PY

git add tests/test_validators.py tests/test_queue.py tests/test_cli.py
git commit -qm "test: add test suite for queue, validators, and CLI"

# --- feature commit 4: docs -----------------------------------------------
mkdir -p docs
cat > docs/USAGE.md <<'MD'
# taskqueue -- usage

`taskqueue` is a small priority queue library with a CLI wrapper. Lower
priority numbers are dequeued first (priority 0 is the most urgent).

## Library

```python
from taskqueue.queue import PriorityQueue

q = PriorityQueue()
q.enqueue("write report", priority=2)
q.enqueue("fix outage", priority=0)
q.dequeue()          # -> "fix outage"
q.peek()             # -> "write report" (does not remove)
q.dequeue_batch(5)   # -> ["write report"] (fewer than 5 items: returns all)
```

## CLI

Items persist between invocations in a JSON store file (default
`queue.json` in the current directory; override with `--store`).

```bash
python -m taskqueue add "write report" 2
python -m taskqueue add "fix outage" 0
python -m taskqueue list
# 0     fix outage
# 2     write report
python -m taskqueue pop
# fix outage
python -m taskqueue pop -n 5
# write report
```

## Commands

| Command | Arguments | Behavior |
|---|---|---|
| `add` | `<label> <priority>` | Enqueue an item. |
| `list` | -- | Print all items, priority order. |
| `pop` | `[-n N]` | Remove and print up to N items (default 1), priority order. |
MD

cat > docs/DESIGN.md <<'MD'
# taskqueue -- design notes

## Data structure

`PriorityQueue` wraps a binary min-heap (`heapq`) of `(priority, sequence,
label)` tuples. `sequence` is a monotonically increasing counter from
`itertools.count()`, used only to break ties between equal priorities in
FIFO order -- `heapq` compares tuples element-by-element, and two items
enqueued at the same priority would otherwise compare on `label` (or
raise, if labels aren't orderable).

## Contracts

- `enqueue(label, priority)` -- validates both arguments (`validators.py`)
  before pushing; raises `TypeError`/`ValueError` on bad input, never
  silently coerces.
- `dequeue()` -- raises `IndexError` on an empty queue (mirrors the
  standard library's own `list.pop()`/`heapq.heappop()` convention for
  "remove from empty container").
- `dequeue_batch(n)` -- the batch counterpart. Never raises for a short
  queue: if fewer than `n` items remain, it returns whatever is left
  instead of raising. This differs deliberately from `dequeue()` -- a
  batch caller is usually asking for "as many as you have, up to n", not
  asserting the queue holds at least `n`.
- `peek()` -- read-only lookup of the next item to be dequeued. Returns
  `None` on an empty queue rather than raising, since peeking is commonly
  used as a non-destructive "is there anything urgent?" check that
  shouldn't need a try/except at every call site.
- `to_list()` -- read-only snapshot of all items, priority order. Used by
  the CLI's `list` command and by the persistence layer (`cli.py`); does
  not mutate the queue.

## Persistence (CLI only)

The CLI has no database -- it round-trips the full queue through a JSON
file (list of `[priority, label]` pairs) on every invocation. Fine for a
small number of items; not intended for concurrent access.
MD

cat > README.md <<'MD'
# taskqueue

A small priority queue library with a CLI wrapper.

## Install

```bash
pip install -e .
```

(Package layout only -- no `setup.py`/`pyproject.toml` is included in
this skeleton; treat `-e .` as illustrative, not a working command yet.)

## Quick start

See [docs/USAGE.md](docs/USAGE.md) for the library and CLI walkthrough,
and [docs/DESIGN.md](docs/DESIGN.md) for the data structure and API
contracts.

## Development

```bash
pytest tests/
```
MD

git add docs/USAGE.md docs/DESIGN.md README.md
git commit -qm "docs: add usage guide and design notes"
