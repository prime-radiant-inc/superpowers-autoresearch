# E5 defect key — `cx-scope-review` / `fixtures/scope-review/` (Task 12)

Answer key for `score_e5.py`'s seeded-defect recall matrix. Every
detection rubric below is a crisp, greppable keyword set, not a subtle
omission — the direct lesson from Task 8's E2-FULL result (the
"coverage-gap" seed, a missing-edge-case-test omission, went 0/4 while
all 4 reviewers converged on real, independently-discovered issues
instead; see `logs/2026-07-28-codex-efficiency.md`'s 2026-07-29
"E2-FULL RESULT" entry). All three fixture-planted defects below are
either a literal RED test, a literal blocking `ModuleNotFoundError`, or
a one-line convention violation checkable against an explicit written
contract — nothing a reviewer has to intuit from an absence.

Line numbers are exact against the fixture as built by
`fixtures/scope-review/build.sh`, `feature` branch, HEAD (commit
"test+docs: batch API tests, BATCH.md, dev-setup msgpack note").
Verified directly by rendering the fixture and reading it back
(`cat -n`), not computed from the heredoc source.

## D1 — local/task-scope bug (wrong default), unit-testable

**File:line:** `mtqueue/batch.py:3`

```
DEFAULT_BATCH_SIZE = 1  # see docs/BATCH.md -- documented default is 5
```

`docs/BATCH.md:6` documents the contract: *"Documented default: 5 items
per call when `max_items` is omitted."* `drain_batch()` (same file,
line 6) uses `DEFAULT_BATCH_SIZE` as its default argument, so calling it
with no explicit size returns 1 item, not 5.

**Directly demonstrable, not just readable:** `tests/test_batch.py`'s own
`test_drain_batch_default_pulls_documented_batch_size` (added in the
same commit) is RED against this branch —
`assert drain_batch(q) == [0, 1, 2, 3, 4]` fails with
`assert [0] == [0, 1, 2, 3, 4]`. A plain `pytest tests/` run in this
fixture (verified: `pyproject.toml`'s `[tool.pytest.ini_options]`
`addopts = "--continue-on-collection-errors"`, set on `main` before D3
exists, keeps this test's result visible even though D3 also fires in
the same run) shows this as `1 failed`, independent of D3's collection
error.

**Detection rubric (any ONE is a hit):**
- The literal test name `test_drain_batch_default_pulls_documented_batch_size`
  or its assertion shape (`[0] == [0, 1, 2, 3, 4]`, "1 item"/"one item"
  vs "5"/"five") appears in a review artifact or relayed message.
- `DEFAULT_BATCH_SIZE` is named alongside "1" and "5" (or "default").
- `drain_batch` is named alongside a wrong-default / off-by-multiple
  framing ("returns 1 instead of 5", "default batch size is wrong",
  etc.) — not merely "batch size" mentioned in passing.

**Scope this measures:** the narrowest, most local review pass (reading
or running just the batch-core commit / its own tests). The Task 1
baseline prediction is that this defect IS caught.

## D2 — cross-commit/cross-task race (unlocked read), NOT unit-testable

**File:line:** `mtqueue/queue.py:31-34`, specifically line 34:

```python
    def peek_batch(self, n):
        """Return up to n oldest items without removing them, oldest
        first. Read-only -- does not mutate the queue."""
        return list(itertools.islice(self._items, n))
```

Every sibling method (`push` line 19-22, `pop_nowait` line 24-29,
`__len__` line 36-38) acquires `self._lock` before touching
`self._items`; `peek_batch` does not. The contract this violates is
written explicitly on `main`, in a commit that predates the whole
`feature` branch — `docs/DESIGN.md:14-17`: *"Any new method added to
`SharedQueue` that reads `self._items`... must acquire `self._lock`
first, exactly like the existing methods, or it reintroduces the exact
race this design exists to prevent."* Catching D2 requires
cross-referencing that main-branch contract (or the sibling methods'
own locking pattern) against the feature branch's new method — a
task/commit-scoped diff review of "the batch core commit" alone,
without pulling in `main`'s established convention, can plausibly miss
it. `docs/BATCH.md:13-17` restates the same expectation from the batch
API's own docs, as a second cross-reference path.

**NOT unit-testable in the shipped suite:** `tests/test_producer_consumer_batch.py::test_preview_does_not_remove_items`
exercises `BatchConsumer.preview()` (which calls `peek_batch`)
sequentially, single-threaded — it passes cleanly. No shipped test runs
a producer thread and a consumer thread concurrently against
`peek_batch`, so `pytest tests/` alone never surfaces this defect; only
reading the code (or writing a NEW concurrent test) does.

**Detection rubric (any ONE is a hit):**
- `peek_batch` named alongside "lock"/"race"/"thread-safe"/"unsynchronized"
  /"without acquiring" (in either direction: flagging the missing lock,
  or explicitly clearing it as fine).
- `self._items` (or "the deque"/"the internal queue") described as read
  "without the lock" / "outside the lock" / "unlocked".
- A reference to `docs/DESIGN.md`'s thread-safety contract in the same
  finding as `peek_batch`/`preview`.

**Scope this measures:** cross-commit/cross-task review — does the
review pass cross-reference the branch's new code against an
established, pre-existing convention, not just the isolated new-commit
diff.

## D3 — clean-checkout break (undeclared dependency)

**Files:lines:**
- `mtqueue/batch_codec.py:3` — `import msgpack`
- `pyproject.toml:6` — `dependencies = []` (msgpack absent)
- `docs/DEV_SETUP.md:7-12` — the author's own TODO note, never acted on:
  *"`msgpack` -- `batch_codec.py`'s wire encoding uses it. **TODO before
  merge: add `msgpack` to `pyproject.toml`'s `[project.dependencies]`**
  -- right now it only imports successfully here because of the
  preinstalled shared venv, not because the project declares it. A
  clean checkout... will hit `ModuleNotFoundError: No module named
  'msgpack'` the moment anything imports `batch_codec`."*

**Directly demonstrable, not hypothetical:** the eval container's own
Python has no `msgpack` preinstalled — verified (`pip show msgpack`
finds nothing, both in this key's own validation run and expected in
the quorum coding-agent container). `pytest tests/` in this fixture
produces a REAL `ERROR collecting tests/test_batch_codec.py` /
`ModuleNotFoundError: No module named 'msgpack'`, not a scenario
simulating one — any reviewer who actually runs the suite sees it
directly, no clean-room re-checkout needed to reproduce it.

**Detection rubric (any ONE is a hit):**
- `msgpack` named alongside "pyproject"/"dependency"/"dependencies"/
  "requirements"/"missing"/"undeclared".
- The literal string `ModuleNotFoundError` (or "No module named") in a
  review artifact or relayed message.
- `batch_codec` named alongside "clean checkout"/"clean install"/"fresh
  venv"/"missing package".

**Scope this measures:** clean-checkout awareness — does the review
pass actually run the suite (or otherwise validate declared deps
against actual imports) rather than trusting that "tests pass" in the
author's own already-provisioned environment.

## D4 — emerges live (not fixture content)

Not planted in `fixtures/scope-review/`. Per `scenarios/cx-scope-review/story.md`,
after the agent's first completion claim the Gauntlet reports D1's own
symptom ("drain_batch without an explicit size only gives me 1 item,
not 5") and asks for a fix. D4 is whatever the agent's repair actually
does — there is no keyword rubric for it (its content isn't known until
the battery runs). `score_e5.py` measures D4 structurally instead: does
the post-repair re-review (if any) examine only the repair's own diff,
or does it re-scope to the whole branch — recorded as
`fix_review_scope` per session (`"repair_diff_only"` |
`"full_branch"` | `"no_re_review"`), derived from
`rollout_parser.patch_applies()`'s changed-path sets compared against
which files a post-repair review pass's own exec/read activity touches.

## Manual-verification discipline

Every rubric match `score_e5.py` reports is verified by printing the
actual matching context line(s) from that run's OWN session artifacts
(final-answer text, relayed review findings) — this is our own
scenario's output, not external corpus content, so quoting it in
`out/e5-report.md` is permitted per this campaign's standing rule
(distinguish "our own fixture/scenario/battery output" from "a real
private corpus," per `score_e3.py`'s module docstring and the Drew/
07-29-corpus privacy rules elsewhere in this log).
