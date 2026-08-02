"""Tests for x6_mine_dispatch_floor.py (queue-execution campaign,
2026-08-01, Task 7 / item 3's MINE tier). All fixture data here is
SYNTHETIC, hand-built rollout JSONL -- never derived from, or a sample of,
any real corpus. Privacy is absolute for the real MINE-tier run (see this
task's report for the aggregate distribution table over the real mined
corpus; that output contains numbers only, never committed).

Fixture layout (fixtures/x6-mine-synthetic/):
  - `.hidden-host/session-a/` -- ONE dispatching session with THREE
    resolvable dispatches (root + 3 children), deliberately placed under a
    dot-prefixed directory to exercise `scorer_common.find_files()`'s
    dot-dir-safe walk (a plain `glob.glob(pattern, recursive=True)` would
    silently skip it -- see scorer_common.py's module docstring). Dispatch
    sizes are exact round numbers for easy hand-verification: total_tokens
    1000/2000/3000, final_answer messages 40/80/120 chars ->
    useful_output_tokens 10/20/30 (chars//4) -> floor_ratio 100.0 for all
    three.
  - `session-b/` -- a second dispatching session with ONE resolvable
    dispatch: total_tokens=5000, message 200 chars -> useful_output=50 ->
    floor_ratio 100.0.

Combined: dispatch_counts=[3, 1] (order-independent -- os.walk's traversal
order is not guaranteed, so every assertion below is order-insensitive),
total_tokens=[1000, 2000, 3000, 5000], useful_output=[10, 20, 30, 50],
floor_ratio=[100.0, 100.0, 100.0, 100.0] -- hand-verified stats below.
"""
import json
import os
import unittest

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "x6-mine-synthetic")

FORBIDDEN_SUBSTRINGS = (
    "minea", "mineb", "thread-", "session-a", "session-b", "hidden-host",
    "rollout-", "task_a", "task_b", ".jsonl",
)


class TestPercentiles(unittest.TestCase):
    def test_empty_list_gives_all_none(self):
        import x6_mine_dispatch_floor as x6m
        result = x6m._percentiles([])
        self.assertEqual(result, {"n": 0, "min": None, "p25": None, "median": None,
                                    "p75": None, "max": None, "mean": None})

    def test_single_value_gives_that_value_for_every_percentile(self):
        import x6_mine_dispatch_floor as x6m
        result = x6m._percentiles([42])
        self.assertEqual(result["n"], 1)
        for key in ("min", "p25", "median", "p75", "max", "mean"):
            self.assertEqual(result[key], 42)

    def test_known_four_value_distribution(self):
        import x6_mine_dispatch_floor as x6m
        result = x6m._percentiles([1000, 2000, 3000, 5000])
        self.assertEqual(result["n"], 4)
        self.assertEqual(result["min"], 1000)
        self.assertEqual(result["max"], 5000)
        self.assertEqual(result["median"], 2500.0)
        self.assertAlmostEqual(result["mean"], 2750.0)
        # p25 <= median <= p75 always holds; exact quartile values depend
        # on statistics.quantiles' interpolation method, not asserted here.
        self.assertLessEqual(result["p25"], result["median"])
        self.assertLessEqual(result["median"], result["p75"])


class TestDispatchCountHistogram(unittest.TestCase):
    def test_buckets_single_digit_and_open_ended_ranges(self):
        import x6_mine_dispatch_floor as x6m
        histogram = x6m._dispatch_count_histogram([1, 3])
        self.assertEqual(histogram, {"1": 1, "2": 0, "3": 1, "4-5": 0, "6-10": 0, "11+": 0})

    def test_open_ended_bucket_catches_large_counts(self):
        import x6_mine_dispatch_floor as x6m
        histogram = x6m._dispatch_count_histogram([1, 5, 8, 15, 30])
        self.assertEqual(histogram["1"], 1)
        self.assertEqual(histogram["4-5"], 1)
        self.assertEqual(histogram["6-10"], 1)
        self.assertEqual(histogram["11+"], 2)

    def test_empty_counts_gives_all_zero_buckets(self):
        import x6_mine_dispatch_floor as x6m
        histogram = x6m._dispatch_count_histogram([])
        self.assertEqual(set(histogram.values()), {0})


class TestSessionDispatchCountsAndSizes(unittest.TestCase):
    def test_finds_both_sessions_including_the_dot_directory_one(self):
        import x6_mine_dispatch_floor as x6m
        counts, totals, useful, ratios = x6m.session_dispatch_counts_and_sizes(FIXTURES)
        self.assertEqual(sorted(counts), [1, 3])
        self.assertEqual(sorted(totals), [1000, 2000, 3000, 5000])
        self.assertEqual(sorted(useful), [10, 20, 30, 50])
        self.assertEqual(len(ratios), 4)
        for r in ratios:
            self.assertAlmostEqual(r, 100.0)

    def test_no_rollout_files_gives_empty_lists(self):
        import x6_mine_dispatch_floor as x6m
        with_no_rollouts = os.path.dirname(FIXTURES)  # "fixtures" itself has no rollout-*.jsonl directly under it beyond subdirs already covered; use an empty temp dir instead
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            counts, totals, useful, ratios = x6m.session_dispatch_counts_and_sizes(tmp)
            self.assertEqual((counts, totals, useful, ratios), ([], [], [], []))


class TestAggregate(unittest.TestCase):
    def setUp(self):
        import x6_mine_dispatch_floor as x6m
        self.result = x6m.aggregate(FIXTURES)

    def test_session_and_dispatch_totals(self):
        self.assertEqual(self.result["n_dispatching_sessions"], 2)
        self.assertEqual(self.result["n_dispatches_total"], 4)

    def test_dispatch_count_distribution(self):
        d = self.result["dispatch_count_distribution"]
        self.assertEqual(d["n"], 2)
        self.assertEqual(d["min"], 1)
        self.assertEqual(d["max"], 3)
        self.assertEqual(d["median"], 2.0)
        self.assertAlmostEqual(d["mean"], 2.0)

    def test_dispatch_count_histogram(self):
        self.assertEqual(self.result["dispatch_count_histogram"],
                          {"1": 1, "2": 0, "3": 1, "4-5": 0, "6-10": 0, "11+": 0})

    def test_total_tokens_distribution(self):
        d = self.result["dispatch_total_tokens_distribution"]
        self.assertEqual(d["n"], 4)
        self.assertEqual(d["min"], 1000)
        self.assertEqual(d["max"], 5000)
        self.assertEqual(d["median"], 2500.0)
        self.assertAlmostEqual(d["mean"], 2750.0)

    def test_floor_ratio_distribution_is_uniform(self):
        d = self.result["dispatch_floor_ratio_distribution"]
        self.assertEqual(d["n"], 4)
        for key in ("min", "p25", "median", "p75", "max", "mean"):
            self.assertAlmostEqual(d[key], 100.0)

    def test_output_is_json_serializable_and_carries_no_raw_identifiers(self):
        # Belt-and-suspenders privacy check: the aggregate report must
        # never leak a fixture's own identifying substrings (thread ids,
        # session names, paths) -- only pure numbers should survive into
        # the printed output.
        serialized = json.dumps(self.result)
        for needle in FORBIDDEN_SUBSTRINGS:
            self.assertNotIn(needle, serialized, f"leaked identifier: {needle!r}")


class TestMainCLI(unittest.TestCase):
    def test_requires_exactly_one_argument(self):
        import x6_mine_dispatch_floor as x6m
        import io
        import contextlib
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = x6m.main(["x6_mine_dispatch_floor.py"])
        self.assertEqual(code, 1)
        self.assertIn("usage", stderr.getvalue())

    def test_prints_valid_json_to_stdout(self):
        import x6_mine_dispatch_floor as x6m
        import io
        import contextlib
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = x6m.main(["x6_mine_dispatch_floor.py", FIXTURES])
        self.assertEqual(code, 0)
        parsed = json.loads(stdout.getvalue())
        self.assertEqual(parsed["n_dispatching_sessions"], 2)


if __name__ == "__main__":
    unittest.main()
