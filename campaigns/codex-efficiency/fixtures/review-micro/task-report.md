# Task 3 Report

**Status:** DONE

**Commits:** a39791b "feat: add moving_average, cumulative_sums, normalize utilities"

**Tests:** 6/6 passing (`pytest tests/test_rolling.py -v`) — pristine output, no warnings.

**Concerns:** none.

Implemented `moving_average`, `cumulative_sums`, and `normalize` in
`src/rolling.py` per the brief. `moving_average` validates the window
bound and raises `ValueError` outside `[1, len(values)]`. `normalize`
special-cases an all-zero input to avoid division by zero. All three
are pure functions with no I/O, matching the Global Constraints.
