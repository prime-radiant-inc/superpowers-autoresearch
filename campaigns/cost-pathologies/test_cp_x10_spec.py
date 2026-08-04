"""Tests for validate_cp_x10_spec.py (plan-decomposition campaign,
2026-08-03, P2-on-cp-x10 iteration): the cp-x10-spec scenario -- the
cp-x10-consistency fixture plus `fixtures/docs/superpowers/specs/
job-queue-spec.md` and `checks.sh`'s new `spec-resolution-N` emit
lines. See `scenarios/cp-x10-spec/seeded-truth-ledger.md`'s "Spec
resolutions" section for the answer key this file checks against.

Mirrors test_cp_x10_consistency.py's / test_pd_overflow_fixture.py's
structure: pytest over static, committed code trees, no container
spend, no real agent session. `TestChecksShSpecResolutionsRunForReal`
follows the T4-correction pattern (validate_pd_pipeline.py's own
module docstring) of exercising checks.sh's REAL bash/awk logic via
`v.run_checks_sh_instruments`, not a Python reimplementation of it.

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
import validate_cp_x10_spec as v  # noqa: E402

SCENARIO_FIXTURES = v.SCENARIO_FIXTURES
UNRESOLVED = v.UNRESOLVED
RESOLVED = v.RESOLVED
SPEC_FILE = v.SPEC_FILE
CHECKS_SH = v.CHECKS_SH
EXPECTED_UNRESOLVED = v.EXPECTED_UNRESOLVED
EXPECTED_RESOLVED = v.EXPECTED_RESOLVED

TASK_OUTPUT_FILES = (
    "jobqueue/worker.py",
    "jobqueue/scheduler.py",
    "jobqueue/api.py",
    "jobqueue/notifier.py",
    "jobqueue/reporter.py",
    "jobqueue/archiver.py",
)


def _parse(lines):
    return v.parse_emit_lines(lines)


class TestSpecFileShipsAndIsBlind(unittest.TestCase):
    def test_spec_file_exists_under_docs_superpowers_specs(self):
        self.assertTrue(SPEC_FILE.exists())
        self.assertEqual(
            SPEC_FILE.relative_to(SCENARIO_FIXTURES).as_posix(),
            "docs/superpowers/specs/job-queue-spec.md",
        )

    def test_spec_file_states_all_five_canonical_values(self):
        # Normalize whitespace so a needle that happens to fall across a
        # markdown line-wrap (prose, not code) still matches -- the
        # wrapping is a rendering detail, not a content difference.
        text = " ".join(SPEC_FILE.read_text().split())
        for needle in (
            "TIMEOUT_SECONDS = 30",
            "RETRY_LIMIT = 4",
            "JobPayloadError",
            "job payload missing field",
            '"retrying"',
            "MIN_PRIORITY = 1",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)

    def test_no_banned_blinding_words_in_spec_file(self):
        self.assertTrue(v.check_blinding(verbose=False))

    def test_blinding_check_catches_an_injected_banned_word(self):
        # Regression guard on the checker itself: prove it actually
        # fires on a real hit, not just silently passing everything.
        with tempfile.TemporaryDirectory() as tmp:
            poisoned = Path(tmp) / "poisoned-spec.md"
            poisoned.write_text("This spec has a seeded conflict in it.\n")
            original = v.SPEC_FILE
            try:
                v.SPEC_FILE = poisoned
                self.assertFalse(v.check_blinding(verbose=False))
            finally:
                v.SPEC_FILE = original

    def test_story_md_opening_message_names_the_spec_without_hinting_conflict(self):
        story_text = (HERE / "scenarios" / "cp-x10-spec" / "story.md").read_text()
        self.assertIn("docs/superpowers/specs/job-queue-spec.md", story_text)
        self.assertIn(
            "The spec is authoritative. Proceed per your workflow.", story_text
        )


class TestPreStateUnchangedFromConsistencyFixturePlusSpec(unittest.TestCase):
    """cp-x10-spec's fixtures/ must be cp-x10-consistency's fixtures/,
    byte-for-byte, with exactly one addition (the spec file) -- proving
    this variant didn't silently drift the shared plan/pre-state that
    validate_x10_fixture.py's own coverage depends on."""

    def _consistency_fixtures(self):
        return HERE / "scenarios" / "cp-x10-consistency" / "fixtures"

    def test_shared_files_are_byte_identical(self):
        consistency_fixtures = self._consistency_fixtures()
        comparison = filecmp.dircmp(
            consistency_fixtures,
            SCENARIO_FIXTURES,
            # docs/ is compared separately below (it gained a sibling
            # `specs/` dir); README.md was deliberately reworded to
            # mention the new spec file (fixtures/README.md).
            ignore=[".gitignore", ".pytest_cache", "__pycache__", "docs", "README.md"],
        )
        self.assertEqual(comparison.diff_files, [])
        self.assertEqual(comparison.funny_files, [])
        # The plan file itself (nested under docs/) must also match.
        plan_relpath = "docs/superpowers/plans/job-queue-plan.md"
        self.assertEqual(
            (consistency_fixtures / plan_relpath).read_text(),
            (SCENARIO_FIXTURES / plan_relpath).read_text(),
        )

    def test_spec_file_is_the_only_new_top_level_addition_under_docs(self):
        consistency_docs = self._consistency_fixtures() / "docs" / "superpowers"
        spec_docs = SCENARIO_FIXTURES / "docs" / "superpowers"
        consistency_subdirs = {p.name for p in consistency_docs.iterdir()}
        spec_subdirs = {p.name for p in spec_docs.iterdir()}
        self.assertEqual(spec_subdirs - consistency_subdirs, {"specs"})

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


class TestResolvedOutcomePassesItsOwnTestSuite(unittest.TestCase):
    def test_resolved_tree_passes_pytest(self):
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=RESOLVED,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_resolved_tree_has_all_six_task_output_files(self):
        for relpath in TASK_OUTPUT_FILES:
            self.assertTrue((RESOLVED / relpath).exists(), f"{relpath} missing from resolved/")


class TestChecksShSpecResolutionsRunForReal(unittest.TestCase):
    """Runs checks.sh's OWN `_x10_emit_defect_instruments` (via
    `v.run_checks_sh_instruments`) against the two materialized trees
    and asserts on the REAL emitted lines -- not a Python
    reimplementation, not a hand-formatted string."""

    def test_unresolved_tree_matches_expected_disposition(self):
        parsed = _parse(v.run_checks_sh_instruments(UNRESOLVED))
        for key, want in EXPECTED_UNRESOLVED.items():
            with self.subTest(key=key):
                self.assertEqual(parsed[key][0].split(" ", 1)[0], want)

    def test_resolved_tree_matches_expected_disposition(self):
        parsed = _parse(v.run_checks_sh_instruments(RESOLVED))
        for key, want in EXPECTED_RESOLVED.items():
            with self.subTest(key=key):
                self.assertEqual(parsed[key][0].split(" ", 1)[0], want)

    def test_seeded_defect_presence_lines_still_emit_unchanged_recipes(self):
        # spec-resolution-N is new; seeded-defect-N (the pre-existing
        # cp-x10-consistency recipes, format unchanged) must still emit.
        # Unlike spec-resolution-N, these lines' descriptive text lives
        # in the LABEL half (before the colon, in parens) -- the exact
        # cp-x10-consistency shape -- so they're checked as raw
        # substrings over v.run_checks_sh_instruments' own returned
        # lines rather than via parse_emit_lines (which only recognizes
        # a bare label before the colon).
        unresolved_lines = v.run_checks_sh_instruments(UNRESOLVED)
        for n in range(1, 6):
            prefix = f"true # seeded-defect-{n} ("
            with self.subTest(defect=n):
                matches = [line for line in unresolved_lines if line.startswith(prefix)]
                self.assertEqual(len(matches), 1, unresolved_lines)
                self.assertTrue(matches[0].rsplit(": ", 1)[1] == "present", matches[0])

        resolved_lines = v.run_checks_sh_instruments(RESOLVED)
        for n in range(1, 6):
            prefix = f"true # seeded-defect-{n} ("
            with self.subTest(defect=n):
                matches = [line for line in resolved_lines if line.startswith(prefix)]
                self.assertEqual(len(matches), 1, resolved_lines)
                self.assertTrue(matches[0].rsplit(": ", 1)[1] == "resolved-or-absent", matches[0])

    def test_checks_sh_itself_still_parses_with_bash(self):
        result = subprocess.run(["bash", "-n", str(CHECKS_SH)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


class TestSpecResolutionPartialCreditBranches(unittest.TestCase):
    """Regression coverage for the `partial` branch of each
    spec-resolution recipe -- constructed synthetic trees that are
    part-way amended, proving `checks.sh` distinguishes "moved toward
    the spec" from both "fully resolved" and "untouched"."""

    def _tree_with(self, module_texts):
        tmp = tempfile.mkdtemp()
        tree = Path(tmp) / "tree"
        shutil.copytree(UNRESOLVED, tree)
        for relpath, text in module_texts.items():
            (tree / relpath).write_text(text)
        return tree

    def test_resolution_1_partial_when_only_one_side_moved_to_spec_value(self):
        # notifier already 30 (spec value); reporter still 90 -- half-resolved.
        tree = self._tree_with({})
        parsed = _parse(v.run_checks_sh_instruments(tree))
        self.assertEqual(parsed["spec-resolution-1"][0].split(" ", 1)[0], "partial")

    def test_resolution_1_partial_when_unified_to_a_non_spec_value(self):
        tree = self._tree_with({
            "jobqueue/notifier.py": "TIMEOUT_SECONDS = 60\n",
            "jobqueue/reporter.py": "TIMEOUT_SECONDS = 60\n",
        })
        parsed = _parse(v.run_checks_sh_instruments(tree))
        self.assertEqual(parsed["spec-resolution-1"][0].split(" ", 1)[0], "partial")

    def test_resolution_2_partial_when_alias_kept_alongside_old_name(self):
        tree = self._tree_with({
            "jobqueue/scheduler.py": "RETRY_LIMIT = 4\nMAX_RETRY_ATTEMPTS = 4\n",
        })
        parsed = _parse(v.run_checks_sh_instruments(tree))
        self.assertEqual(parsed["spec-resolution-2"][0].split(" ", 1)[0], "partial")

    def test_resolution_2_yes_when_cleanly_renamed(self):
        tree = self._tree_with({"jobqueue/scheduler.py": "RETRY_LIMIT = 4\n"})
        parsed = _parse(v.run_checks_sh_instruments(tree))
        self.assertEqual(parsed["spec-resolution-2"][0].split(" ", 1)[0], "yes")

    def test_resolution_3_partial_when_only_class_renamed(self):
        tree = self._tree_with({
            "jobqueue/api.py": (
                "MIN_PRIORITY = 2\n\n\nclass JobPayloadError(Exception):\n    pass\n\n\n"
                "def parse_submission(payload):\n"
                "    raise JobPayloadError('submission rejected: field x is required')\n"
            ),
        })
        parsed = _parse(v.run_checks_sh_instruments(tree))
        self.assertEqual(parsed["spec-resolution-3"][0].split(" ", 1)[0], "partial")

    def test_resolution_4_partial_when_only_notifier_handles_retrying(self):
        tree = self._tree_with({
            "jobqueue/notifier.py": 'TIMEOUT_SECONDS = 30\n_MESSAGES = {"retrying": "job retrying"}\n',
        })
        parsed = _parse(v.run_checks_sh_instruments(tree))
        self.assertEqual(parsed["spec-resolution-4"][0].split(" ", 1)[0], "partial")

    def test_resolution_4_no_when_neither_handles_retrying(self):
        tree = self._tree_with({})
        parsed = _parse(v.run_checks_sh_instruments(tree))
        self.assertEqual(parsed["spec-resolution-4"][0].split(" ", 1)[0], "no")

    def test_resolution_5_yes_when_api_moves_to_spec_value(self):
        # worker.py is already MIN_PRIORITY = 1 (the spec value) in the
        # unresolved tree -- amending api.py to 1 as well is the FULL
        # resolution (both sides now agree with the spec), not partial.
        tree = self._tree_with({"jobqueue/api.py": "MIN_PRIORITY = 1\n"})
        parsed = _parse(v.run_checks_sh_instruments(tree))
        self.assertEqual(parsed["spec-resolution-5"][0].split(" ", 1)[0], "yes")

    def test_resolution_5_partial_when_api_moves_to_a_non_spec_value(self):
        # api.py changed away from its original 2, but to a third value
        # that still isn't the spec's 1 -- worker's own 1 is the only
        # side matching the spec, so this is partial credit, not yes.
        tree = self._tree_with({"jobqueue/api.py": "MIN_PRIORITY = 5\n"})
        parsed = _parse(v.run_checks_sh_instruments(tree))
        self.assertEqual(parsed["spec-resolution-5"][0].split(" ", 1)[0], "partial")


if __name__ == "__main__":
    unittest.main()
