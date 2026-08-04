"""Tests for validate_pd_overflow_xl.py (plan-decomposition campaign,
overflow-probe expansion): the pd-overflow-xl scenario's fixture -- the
CERTIFIED return-window overflow probe, a wider authoring+execution
pipeline whose `scenarios/pd-overflow-xl/checks.sh` emits (never
asserts) plan-shape, task-count, settings-micro-edit-disposition,
cross-module-coherence, and simplest-thing observables for the
campaign's P1/P2/P4 instruments, over a wider module list spanning
three subsystems (32 modules) than `pd-overflow` (16, one subsystem).

Mirrors `test_pd_overflow_fixture.py`'s structure, adapted for the
32-module/six-consuming-module/six-settings-constant widening (see
`scenarios/pd-overflow-xl/probe-design-notes.md` for what this tree is
built to prove, and why one tree suffices here, same as `pd-overflow`'s
own). No container spend, no real agent session; everything here is
synthetic.
"""
import filecmp
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import validate_pd_overflow_xl as v  # noqa: E402

SCENARIO_FIXTURES = v.SCENARIO_FIXTURES
DIRECTORY_TASKS = v.DIRECTORY_TASKS

_EMIT_LINE_RE = re.compile(r"^true # ([a-zA-Z0-9_.\-/ ]+?): (.*)$")


def _parse_lines(lines):
    """Parse checks.sh-style 'true # label: value' lines into a dict,
    exactly as a scorer consuming the composer's recorded command text
    would."""
    parsed = {}
    for line in lines:
        match = _EMIT_LINE_RE.match(line)
        assert match, f"line does not match the emit-line format: {line!r}"
        label, value = match.groups()
        parsed.setdefault(label, []).append(value)
    return parsed


def _run_pytest(tree_root):
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=tree_root,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0, result.stdout + result.stderr


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
            ok, output = _run_pytest(materialized)
            self.assertTrue(ok, output)

    def test_materialized_starting_tree_has_no_module_output_yet(self):
        with tempfile.TemporaryDirectory() as tmp:
            materialized = Path(tmp) / "materialized"
            shutil.copytree(SCENARIO_FIXTURES, materialized)
            for relpath in v.MODULE_FILES:
                self.assertFalse((materialized / relpath).exists(), f"{relpath} should not exist pre-session")

    def test_materialized_starting_tree_has_no_plan_yet(self):
        with tempfile.TemporaryDirectory() as tmp:
            materialized = Path(tmp) / "materialized"
            shutil.copytree(SCENARIO_FIXTURES, materialized)
            self.assertEqual(v.pd_pipeline.plan_files(materialized), [])


class TestOutcomeTreePassesItsOwnTestSuite(unittest.TestCase):
    def test_directory_tasks_passes_pytest(self):
        ok, output = _run_pytest(DIRECTORY_TASKS)
        self.assertTrue(ok, output)

    def test_all_thirty_two_module_files_present(self):
        self.assertEqual(len(v.MODULE_FILES), 32)
        for relpath in v.MODULE_FILES:
            self.assertTrue((DIRECTORY_TASKS / relpath).exists(), f"{relpath} missing from {DIRECTORY_TASKS}")


class TestPlanShapeObservablesFireCorrectly(unittest.TestCase):
    def test_directory_tasks_is_multiple_files(self):
        observables = v.compute_observables(DIRECTORY_TASKS)
        self.assertEqual(observables["plan_shape"], "directory")
        # 32 module tasks + 3 dedicated settings tasks + constraints.md + plan.yaml
        self.assertEqual(observables["plan_file_count"], 37)

    def test_task_count_is_thirty_five(self):
        observables = v.compute_observables(DIRECTORY_TASKS)
        self.assertEqual(observables["plan_task_count"], 35)


class TestSettingsMicroEditDispositionFiresCorrectly(unittest.TestCase):
    def test_mixed_disposition_three_merged_three_dedicated(self):
        observables = v.compute_observables(DIRECTORY_TASKS)
        self.assertEqual(observables["settings_touching_tasks"], 6)
        self.assertEqual(observables["settings_dedicated_tasks"], 3)
        self.assertEqual(observables["settings_merged_tasks"], 3)

    def test_a_prose_mention_of_settings_py_without_an_edit_is_not_miscounted(self):
        # Regression guard (same class as pd-overflow's own): task-14
        # archiving.md's prose mentions the archive grace period *setting*
        # (added by a different, dedicated task) without touching
        # orders/settings.py itself -- it must not be picked up as a
        # seventh settings-touching task.
        text = (DIRECTORY_TASKS / "docs/superpowers/plans/2026-08-03-order-fulfillment-ops-reconciliation/task-14-archiving.md").read_text()
        self.assertNotIn("orders/settings.py", text)
        observables = v.compute_observables(DIRECTORY_TASKS)
        self.assertEqual(observables["settings_touching_tasks"], 6)

    def test_cross_subsystem_warehouse_prose_mentions_are_not_miscounted(self):
        # Same guard, for the new subsystems: shift_coverage.py,
        # reconciliation.py, and carrier_manifest.py's tasks all mention
        # `orders.settings.WAREHOUSES` (dotted attribute reference) in
        # prose, never the literal `orders/settings.py` path -- none of
        # the three should count as settings-touching.
        base = DIRECTORY_TASKS / "docs/superpowers/plans/2026-08-03-order-fulfillment-ops-reconciliation"
        for filename in ("task-22-shift-coverage.md", "task-27-reconciliation.md", "task-29-carrier-manifest.md"):
            text = (base / filename).read_text()
            self.assertNotIn("orders/settings.py", text, f"{filename} should not literally touch orders/settings.py")


class TestCoherenceObservableFiresCorrectly(unittest.TestCase):
    def test_coherent_at_twelve_across_all_six_modules(self):
        observables = v.compute_observables(DIRECTORY_TASKS)
        self.assertTrue(observables["max_line_items_coherent"])
        self.assertEqual(
            observables["max_line_items"],
            {
                "orders/validation.py": 12,
                "orders/pricing.py": 12,
                "orders/fulfillment.py": 12,
                "orders/allocation.py": 12,
                "orders/manual_override.py": 12,
                "orders/csv_import.py": 12,
            },
        )


class TestSettingsConstantsPresence(unittest.TestCase):
    def test_all_six_constants_present(self):
        presence = v.settings_constants_present(DIRECTORY_TASKS)
        self.assertTrue(all(presence.values()), presence)
        self.assertEqual(set(presence), set(v.SETTINGS_CONSTANT_NAMES))
        self.assertEqual(len(v.SETTINGS_CONSTANT_NAMES), 6)


class TestSimplestThingSignalFiresCorrectly(unittest.TestCase):
    def test_pricing_is_simple(self):
        observables = v.compute_observables(DIRECTORY_TASKS)
        self.assertEqual(observables["pricing_simplest_thing_signal"], "simple")
        self.assertEqual(observables["pricing_overbuild_hits"], 0)


class TestEmitLinesParseInTheFormatAScorerWouldConsume(unittest.TestCase):
    def test_lines_parse_and_match_observables(self):
        observables = v.compute_observables(DIRECTORY_TASKS)
        lines = v.format_lines(observables)
        parsed = _parse_lines(lines)
        self.assertEqual(parsed["plan-shape"], ["directory (37 file(s))"])
        self.assertEqual(parsed["plan-task-count"], ["35"])
        self.assertEqual(parsed["settings-micro-edits-dedicated-tasks"], ["3"])
        self.assertEqual(parsed["settings-micro-edits-merged-tasks"], ["3"])
        self.assertEqual(parsed["max-line-items-coherent"], ["yes (12 across all six modules)"])
        self.assertEqual(parsed["pricing-simplest-thing-signal"], ["simple (0 markers)"])
        self.assertEqual(parsed["settings-return-window-days"], ["present"])
        self.assertEqual(parsed["settings-audit-log-retention-days"], ["present"])
        self.assertEqual(parsed["settings-reconciliation-tolerance-cents"], ["present"])

    def test_every_plan_file_gets_its_own_emit_line(self):
        observables = v.compute_observables(DIRECTORY_TASKS)
        lines = v.format_lines(observables)
        plan_file_lines = [line for line in lines if line.startswith("true # plan-file:")]
        self.assertEqual(len(plan_file_lines), 37)


class TestBashChecksShAgreesWithThePythonPort(unittest.TestCase):
    """checks.sh itself is bash+awk (matching every sibling scenario's
    convention), never invoked directly by the harness outside a real
    quorum run. This test sources it and calls its own helper functions
    directly against the outcome tree, proving the ACTUAL bash/awk
    logic -- not just this file's Python reimplementation -- produces
    the same task-count and settings-disposition numbers."""

    CHECKS_SH = HERE / "scenarios" / "pd-overflow-xl" / "checks.sh"

    def _run_helpers(self, tree_root):
        script = f"""
set -euo pipefail
cd {tree_root}
source {self.CHECKS_SH}
files=()
while IFS= read -r f; do
    [ -n "$f" ] && files+=("$f")
done < <(_pd_plan_files)
echo "FILE_COUNT ${{#files[@]}}"
echo "TASK_COUNT $(_pd_task_count "${{files[@]}}")"
echo "DISPOSITION $(_pd_settings_disposition "${{files[@]}}")"
"""
        result = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        values = {}
        for line in result.stdout.splitlines():
            key, _, rest = line.partition(" ")
            values[key] = rest
        return values

    def test_directory_tasks_bash_matches_python(self):
        bash_values = self._run_helpers(DIRECTORY_TASKS)
        observables = v.compute_observables(DIRECTORY_TASKS)
        self.assertEqual(int(bash_values["FILE_COUNT"]), observables["plan_file_count"])
        self.assertEqual(int(bash_values["TASK_COUNT"]), observables["plan_task_count"])
        total, dedicated = (int(x) for x in bash_values["DISPOSITION"].split())
        self.assertEqual(total, observables["settings_touching_tasks"])
        self.assertEqual(dedicated, observables["settings_dedicated_tasks"])


class TestChecksShInstrumentsRunForReal(unittest.TestCase):
    """Runs checks.sh's OWN `_pd_emit_plan_instruments` (via
    `v.run_checks_sh_instruments`) against the materialized tree and
    asserts on the REAL emitted lines -- not a Python reimplementation,
    not a hand-formatted string. Same rationale as
    test_pd_overflow_fixture.py's equivalent class -- see this project's
    2026-08-03 T4 correction fix round."""

    def test_directory_tasks_real_emitted_lines(self):
        lines = v.run_checks_sh_instruments(DIRECTORY_TASKS)
        parsed = _parse_lines(lines)
        self.assertEqual(parsed["plan-shape"], ["directory (37 file(s))"])
        self.assertEqual(parsed["plan-task-count"], ["35"])
        self.assertEqual(parsed["max-line-items-validation"], ["12"])
        self.assertEqual(parsed["max-line-items-pricing"], ["12"])
        self.assertEqual(parsed["max-line-items-fulfillment"], ["12"])
        self.assertEqual(parsed["max-line-items-allocation"], ["12"])
        self.assertEqual(parsed["max-line-items-manual_override"], ["12"])
        self.assertEqual(parsed["max-line-items-csv_import"], ["12"])
        self.assertEqual(parsed["max-line-items-coherent"], ["yes (12 across all six modules)"])
        self.assertEqual(parsed["settings-return-window-days"], ["present"])
        self.assertEqual(parsed["settings-audit-log-retention-days"], ["present"])
        self.assertEqual(parsed["settings-reconciliation-tolerance-cents"], ["present"])


class TestMaxLineItemsToleratesAnnotatedAndImportForms(unittest.TestCase):
    """Regression coverage for the exact T4 defect (plan-decomposition
    campaign, 2026-08-03), widened to this scenario's six-module
    coherence check -- see test_pd_pipeline_fixture.py's equivalent class
    for the full defect history. Proven by running checks.sh ITSELF (via
    `v.run_checks_sh_instruments`), never a Python reimplementation that
    would carry the identical blind spot."""

    def _tree_with(self, module_texts):
        tmp = tempfile.mkdtemp()
        tree = Path(tmp) / "tree"
        shutil.copytree(DIRECTORY_TASKS, tree)
        for relpath, text in module_texts.items():
            (tree / relpath).write_text(text)
        return tree

    def test_annotated_assignment_is_not_absent(self):
        tree = self._tree_with({"orders/manual_override.py": "MAX_LINE_ITEMS: int = 12\n"})
        parsed = _parse_lines(v.run_checks_sh_instruments(tree))
        self.assertEqual(parsed["max-line-items-manual_override"], ["12"])

    def test_import_reference_resolves_one_hop(self):
        tree = self._tree_with({
            "orders/validation.py": "MAX_LINE_ITEMS = 12\n",
            "orders/csv_import.py": "from orders.validation import MAX_LINE_ITEMS\n",
        })
        parsed = _parse_lines(v.run_checks_sh_instruments(tree))
        self.assertEqual(parsed["max-line-items-csv_import"], ["import(12)"])

    def test_annotated_and_import_forms_still_count_as_coherent_across_all_six(self):
        tree = self._tree_with({
            "orders/validation.py": "MAX_LINE_ITEMS = 12\n",
            "orders/pricing.py": "MAX_LINE_ITEMS: int = 12\n",
            "orders/fulfillment.py": "from orders.validation import MAX_LINE_ITEMS\n",
            "orders/allocation.py": "MAX_LINE_ITEMS: int = 12\n",
            "orders/manual_override.py": "MAX_LINE_ITEMS: int = 12\n",
            "orders/csv_import.py": "from orders.validation import MAX_LINE_ITEMS\n",
        })
        parsed = _parse_lines(v.run_checks_sh_instruments(tree))
        self.assertEqual(parsed["max-line-items-coherent"], ["yes (12 across all six modules)"])

    def test_one_absent_module_breaks_coherence_across_the_wider_family(self):
        # Regression guard specific to the widened family: a module
        # missing the constant entirely (not just disagreeing on its
        # value) must still break coherence now that six modules, not
        # four, participate.
        tree = self._tree_with({"orders/manual_override.py": "# no MAX_LINE_ITEMS here\n"})
        parsed = _parse_lines(v.run_checks_sh_instruments(tree))
        self.assertEqual(parsed["max-line-items-manual_override"], ["absent"])
        self.assertEqual(
            parsed["max-line-items-coherent"][0].split(" ", 1)[0],
            "no",
        )


class TestGroundTruthMliExtraction(unittest.TestCase):
    """Ground-truth regression test for the tolerant extraction itself
    (`_pd_mli`/`_pd_mli_direct`), isolated from the rest of
    `_pd_emit_plan_instruments` and from any committed outcome tree.
    Same rationale as test_pd_overflow_fixture.py's equivalent class."""

    CHECKS_SH = HERE / "scenarios" / "pd-overflow-xl" / "checks.sh"

    def _pd_mli(self, tree_root, relpath):
        script = f"""
set -euo pipefail
cd {shlex.quote(str(tree_root))}
source {shlex.quote(str(self.CHECKS_SH))}
_pd_mli {shlex.quote(relpath)}
"""
        result = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.strip()

    def test_annotated_assignment_reads_as_the_bare_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp)
            (tree / "orders").mkdir()
            (tree / "orders" / "csv_import.py").write_text("MAX_LINE_ITEMS: int = 12\n")
            self.assertEqual(self._pd_mli(tree, "orders/csv_import.py"), "12")

    def test_import_reference_reads_as_import_wrapped_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp)
            (tree / "orders").mkdir()
            (tree / "orders" / "validation.py").write_text("MAX_LINE_ITEMS = 12\n")
            (tree / "orders" / "csv_import.py").write_text("from orders.validation import MAX_LINE_ITEMS\n")
            self.assertEqual(self._pd_mli(tree, "orders/csv_import.py"), "import(12)")

    def test_missing_module_reads_as_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self._pd_mli(Path(tmp), "orders/csv_import.py"), "absent")


class TestValidateScriptExitsCleanly(unittest.TestCase):
    def test_main_returns_zero(self):
        self.assertEqual(v.main(["-v"]), 0)


if __name__ == "__main__":
    unittest.main()
