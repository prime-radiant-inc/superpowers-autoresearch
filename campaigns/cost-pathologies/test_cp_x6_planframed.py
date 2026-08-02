"""Validation for the cp-x6-planframed scenario (queue-execution campaign,
2026-08-01, Task 7 / item 3 of reports/2026-08-cost-pathologies-campaign.md
§6's queue): the X6 plan-framed fixture -- the same dozen-small-edits work
`cp-x6-smalledits` uses, re-framed as an explicit SDD plan/task list so a
real session reliably engages subagent-driven-development (see this
scenario's own seeded-truth-ledger.md for the disclosed trade-off: this
fixture tests "does X6 help once SDD is engaged," never "does X6 change
whether SDD gets reached for").

Per the same controller ruling `cp-x1-edit-existing` and `cp-x1-wavecap`
operated under (their own test files' docstrings), this task spends no
containers or API budget on real reps. This file validates three
properties, entirely from committed fixtures:

  1. `TestSetupMaterializesDeterministicallyAndReproducibleStartingState`
     -- setup.sh (`setup-helpers run init_repo_from_fixtures ...`)
     materializes a session's starting tree by copying this scenario's own
     `fixtures/` directory verbatim. That property is validated directly:
     two independent copies of `fixtures/` are byte-identical, AND running
     the materialized starting tree's test suite twice independently
     produces the identical, reproducible result both times. "Green" here
     means the harness runs cleanly to a reproducible result, not that the
     tests pass -- they are seeded to fail (matching
     `cp-x6-smalledits/seeded-truth-ledger.md`'s documented baseline for
     this identical fixture content, reused byte-for-byte here: 14 failing
     / 1 passing out of 15 total assertions) until the plan's twelve fixes
     land.
  2. `TestPlanTaskStructureAndSmallness` -- the plan
     (`fixtures/docs/superpowers/plans/util-bugfix-plan.md`) parses into
     exactly twelve `## Task N:` blocks, each naming exactly one file in
     its `Files:` section as a `Modify:` entry (never a `Create:`, never
     more than one file) -- the mechanical smallness criterion that keeps
     the batching-vs-per-task-dispatch decision X6-A/X6-B govern live in
     every task (see the ledger's "Mechanical smallness criterion"
     section). The twelve files are also pairwise distinct.
  3. `TestScoreX6FloorDiscriminatesDispatchShapes` -- `score_x6_floor.py`
     (Task 2, corpus-validated, unmodified) correctly discriminates a
     batched-dispatch synthetic transcript (ONE `spawn_agent` dispatch
     covering all twelve tasks) from a per-task-dispatch synthetic
     transcript (TWELVE separate dispatches, one per task) on rollout data
     shaped like this scenario's own twelve tasks -- confirming the
     INSTRUMENT can tell the predicted arm shapes apart, not that a real
     session produces either one. Fixtures under
     `fixtures/cp-x6-planframed-dispatch-shapes/{batched,per-task}/`,
     built with the same synthetic-rollout-JSONL conventions
     `fixtures/x6/` (score_x6_floor's own corpus-validated test fixture)
     already uses.

Everything here is synthetic; no real system.
"""
import glob
import filecmp
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
SCENARIO_FIXTURES = HERE / "scenarios" / "cp-x6-planframed" / "fixtures"
PLAN_PATH = SCENARIO_FIXTURES / "docs" / "superpowers" / "plans" / "util-bugfix-plan.md"
DISPATCH_SHAPES = HERE / "fixtures" / "cp-x6-planframed-dispatch-shapes"

sys.path.insert(0, str(HERE))


# ---------------------------------------------------------------------------
# Property 1: setup.sh materializes deterministically; the starting tree's
# own test run is a reproducible, known result.
# ---------------------------------------------------------------------------


def _run_tap_test(tree_root):
    """Runs `node --test --test-reporter=tap` in TREE_ROOT and parses the
    TAP summary's `# tests` / `# pass` / `# fail` counters -- more stable
    across node versions than scraping the default spec reporter's output,
    which does not always print a machine-parseable summary line."""
    result = subprocess.run(
        ["node", "--test", "--test-reporter=tap"],
        cwd=tree_root,
        capture_output=True,
        text=True,
    )
    counts = {}
    for key in ("tests", "pass", "fail"):
        m = re.search(rf"^# {key} (\d+)$", result.stdout, re.M)
        counts[key] = int(m.group(1)) if m else None
    return counts, result.stdout + result.stderr


class TestSetupMaterializesDeterministicallyAndReproducibleStartingState(unittest.TestCase):
    def _assert_no_diff(self, comparison):
        self.assertEqual(comparison.left_only, [], f"only in copy A: {comparison.left_only}")
        self.assertEqual(comparison.right_only, [], f"only in copy B: {comparison.right_only}")
        self.assertEqual(comparison.diff_files, [], f"differing files: {comparison.diff_files}")
        for sub in comparison.subdirs.values():
            self._assert_no_diff(sub)

    def test_two_independent_copies_of_fixtures_are_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy_a = Path(tmp) / "a"
            copy_b = Path(tmp) / "b"
            shutil.copytree(SCENARIO_FIXTURES, copy_a)
            shutil.copytree(SCENARIO_FIXTURES, copy_b)
            self._assert_no_diff(filecmp.dircmp(copy_a, copy_b))

    def test_starting_tree_test_run_is_deterministic_and_matches_seeded_failure_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_1 = Path(tmp) / "run-1"
            run_2 = Path(tmp) / "run-2"
            shutil.copytree(SCENARIO_FIXTURES, run_1)
            shutil.copytree(SCENARIO_FIXTURES, run_2)
            counts_1, out_1 = _run_tap_test(run_1)
            counts_2, out_2 = _run_tap_test(run_2)
            expected = {"tests": 15, "pass": 1, "fail": 14}
            self.assertEqual(counts_1, expected, out_1)
            self.assertEqual(counts_2, expected, out_2)
            self.assertEqual(counts_1, counts_2, "two independent runs disagreed")


# ---------------------------------------------------------------------------
# Property 2: the plan's task structure parses, and every task is genuinely
# small (exactly one file, always a Modify, never a Create).
# ---------------------------------------------------------------------------

TASK_HEADER_RE = re.compile(r"^## Task (\d+):", re.M)
FILE_LINE_RE = re.compile(r"^- (Modify|Create): `([^`]+)`\s*$", re.M)


def _parse_plan_tasks(text):
    """Every `## Task N:` block's (n, [(kind, path), ...]) pair, where
    `kind` is "Modify" or "Create" and `path` is the file it names, read
    from that task's own `**Files:**` section."""
    headers = list(TASK_HEADER_RE.finditer(text))
    tasks = []
    for i, m in enumerate(headers):
        start = m.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        block = text[start:end]
        files_match = re.search(
            r"\*\*Files:\*\*(.*?)(?:\*\*Implementation|\*\*Verification)", block, re.S
        )
        files_block = files_match.group(1) if files_match else ""
        files = FILE_LINE_RE.findall(files_block)
        tasks.append({"n": int(m.group(1)), "files": files})
    return tasks


class TestPlanTaskStructureAndSmallness(unittest.TestCase):
    def setUp(self):
        self.text = PLAN_PATH.read_text()
        self.tasks = _parse_plan_tasks(self.text)

    def test_exactly_twelve_tasks(self):
        self.assertEqual(len(self.tasks), 12)
        self.assertEqual([t["n"] for t in self.tasks], list(range(1, 13)))

    def test_every_task_names_exactly_one_file(self):
        for task in self.tasks:
            with self.subTest(task=task["n"]):
                self.assertEqual(
                    len(task["files"]), 1,
                    f"Task {task['n']} names {len(task['files'])} files, expected exactly 1"
                )

    def test_every_task_files_entry_is_modify_not_create(self):
        for task in self.tasks:
            with self.subTest(task=task["n"]):
                kind, _path = task["files"][0]
                self.assertEqual(kind, "Modify", f"Task {task['n']} is a {kind}, expected Modify")

    def test_the_twelve_files_are_pairwise_distinct(self):
        files = [task["files"][0][1] for task in self.tasks]
        self.assertEqual(len(files), len(set(files)), f"duplicate file across tasks: {files}")

    def test_every_named_file_is_a_util_js_file(self):
        for task in self.tasks:
            with self.subTest(task=task["n"]):
                _kind, path = task["files"][0]
                self.assertTrue(path.startswith("util/"), path)
                self.assertTrue(path.endswith(".js"), path)


# ---------------------------------------------------------------------------
# Property 3: score_x6_floor.dispatch_floor() discriminates a
# batched-dispatch transcript from a per-task-dispatch transcript on
# rollout data shaped like this scenario's own twelve tasks.
# ---------------------------------------------------------------------------


class TestScoreX6FloorDiscriminatesDispatchShapes(unittest.TestCase):
    def _paths(self, shape):
        return sorted(glob.glob(str(DISPATCH_SHAPES / shape / "*.jsonl")))

    def test_batched_shape_is_one_dispatch(self):
        import score_x6_floor as sx6
        result = sx6.dispatch_floor(self._paths("batched"))
        self.assertEqual(len(result["dispatches"]), 1)

    def test_per_task_shape_is_twelve_dispatches(self):
        import score_x6_floor as sx6
        result = sx6.dispatch_floor(self._paths("per-task"))
        self.assertEqual(len(result["dispatches"]), 12)

    def test_per_task_task_names_are_all_distinct(self):
        import score_x6_floor as sx6
        result = sx6.dispatch_floor(self._paths("per-task"))
        names = [d["task_name"] for d in result["dispatches"]]
        self.assertEqual(len(names), len(set(names)), names)

    def test_batched_dispatch_costs_less_total_tokens_than_the_sum_of_per_task_dispatches(self):
        # The floor-tax story this fixture is built to let a future battery
        # observe: one batch dispatch's own floor cost vs. twelve separate
        # floor costs stacked on top of each other.
        import score_x6_floor as sx6
        batched = sx6.dispatch_floor(self._paths("batched"))
        per_task = sx6.dispatch_floor(self._paths("per-task"))
        batched_total = sum(d["total_tokens"] for d in batched["dispatches"])
        per_task_total = sum(d["total_tokens"] for d in per_task["dispatches"])
        self.assertLess(batched_total, per_task_total)


if __name__ == "__main__":
    unittest.main()
