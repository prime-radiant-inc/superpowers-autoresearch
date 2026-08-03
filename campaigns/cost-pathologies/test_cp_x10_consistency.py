"""Tests for validate_x10_fixture.py (backlog campaign, 2026-08-02, Task
5): the cp-x10-consistency scenario's fixture -- a six-task plan whose
faithful implementation induces five real cross-module consistency
defects (seeded-truth-ledger.md).

Mirrors test_cp_x1_wavecap.py's structure: pytest over two static,
committed code trees (scenarios/cp-x10-consistency/fixtures/, the
pre-state, and fixtures/cp-x10-consistency-outcomes/complete/, the
post-state), no container spend, no real agent session.

Everything here is synthetic; no real system.
"""
import filecmp
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import validate_x10_fixture as v  # noqa: E402

SCENARIO_FIXTURES = v.SCENARIO_FIXTURES
COMPLETE = v.COMPLETE
DETECTORS = v.DETECTORS

TASK_OUTPUT_FILES = (
    "jobqueue/worker.py",
    "jobqueue/scheduler.py",
    "jobqueue/api.py",
    "jobqueue/notifier.py",
    "jobqueue/reporter.py",
    "jobqueue/archiver.py",
)


class TestSetupMaterializesDeterministicallyAndStartsClean(unittest.TestCase):
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

    def test_materialized_starting_tree_passes_its_own_test_suite(self):
        with tempfile.TemporaryDirectory() as tmp:
            materialized = Path(tmp) / "materialized"
            shutil.copytree(SCENARIO_FIXTURES, materialized)
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-q"],
                cwd=materialized,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_materialized_starting_tree_has_no_task_output_yet(self):
        with tempfile.TemporaryDirectory() as tmp:
            materialized = Path(tmp) / "materialized"
            shutil.copytree(SCENARIO_FIXTURES, materialized)
            for relpath in TASK_OUTPUT_FILES:
                self.assertFalse((materialized / relpath).exists(), f"{relpath} should not exist pre-session")


class TestPostStatePassesItsOwnTestSuite(unittest.TestCase):
    def test_complete_tree_passes_pytest(self):
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=COMPLETE,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_complete_tree_has_all_six_task_output_files(self):
        for relpath in TASK_OUTPUT_FILES:
            self.assertTrue((COMPLETE / relpath).exists(), f"{relpath} missing from complete/")


class TestSeededDefectsPresentInCompleteTree(unittest.TestCase):
    def test_every_defect_is_detected_in_the_complete_tree(self):
        for defect_id, detector in DETECTORS.items():
            with self.subTest(defect=defect_id):
                self.assertIs(detector(COMPLETE), True, f"{defect_id} not detected in complete/")

    def test_at_least_five_defects_detected(self):
        results = [detector(COMPLETE) for detector in DETECTORS.values()]
        self.assertGreaterEqual(sum(1 for r in results if r is True), 5)


class TestSeededDefectsNotFalselyDetectedInPreState(unittest.TestCase):
    def test_no_defect_is_falsely_detected_before_any_task_runs(self):
        for defect_id, detector in DETECTORS.items():
            with self.subTest(defect=defect_id):
                result = detector(SCENARIO_FIXTURES)
                self.assertIsNone(
                    result,
                    f"{defect_id} should be not-yet-checkable in the pre-state (task output files "
                    f"don't exist yet), got {result}",
                )


class TestValidateScriptExitsCleanly(unittest.TestCase):
    def test_main_returns_zero(self):
        self.assertEqual(v.main(["-v"]), 0)


if __name__ == "__main__":
    unittest.main()
