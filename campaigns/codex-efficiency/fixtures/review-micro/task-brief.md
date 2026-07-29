# Task 3 Brief: Rolling-window aggregation utilities

**Files:**

- Create: `src/rolling.py`
- Create: `tests/test_rolling.py`

**Interfaces:**

- Consumes: a list of numbers `values`, and (for `moving_average`) an integer `window`.
- Produces: `moving_average(values, window) -> list[float]`, `cumulative_sums(values) -> list`, and `normalize(values) -> list[float]`, all pure functions with no I/O, exported from `src/rolling.py`.

**Requirements:**

- `moving_average(values, window)` returns the average of every contiguous `window`-sized slice, sliding by one position at a time. For an input of length `n` and window `w`, the result MUST contain exactly `n - w + 1` averages — one for every valid starting index `0` through `n - w` inclusive. Raise `ValueError` if `window` is not between `1` and `len(values)`.
- `cumulative_sums(values)` returns the running total after each element.
- `normalize(values)` scales `values` so they sum to `1.0`; an all-zero input returns a same-length list of `0.0` rather than dividing by zero.
- Follow TDD: write a focused failing test before each function's minimal implementation.

**Report:** write your report to `.superpowers/sdd/review-micro/task-3-report.md` when done.
