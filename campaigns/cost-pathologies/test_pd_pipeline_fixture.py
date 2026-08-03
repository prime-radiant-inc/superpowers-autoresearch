"""Tests for validate_pd_pipeline.py (plan-decomposition campaign, Task
1): the pd-pipeline scenario's fixture -- an authoring+execution pipeline
whose `scenarios/pd-pipeline/checks.sh` emits (never asserts) plan-shape,
task-count, settings-micro-edit-disposition, cross-module-coherence, and
simplest-thing observables for the campaign's P1/P2/P4 instruments.

Mirrors test_cp_x10_consistency.py's structure, adapted for two
constructed post-states instead of one (there is no single pre-written
plan here -- the session authors its own -- see
scenarios/pd-pipeline/probe-design-notes.md for what each tree is built
to prove). No container spend, no real agent session; everything here is
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
import validate_pd_pipeline as v  # noqa: E402

SCENARIO_FIXTURES = v.SCENARIO_FIXTURES
MONOLITHIC_LAYERED = v.MONOLITHIC_LAYERED
DIRECTORY_SKELETON = v.DIRECTORY_SKELETON

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
            self.assertEqual(v.plan_files(materialized), [])


class TestBothOutcomeTreesPassTheirOwnTestSuite(unittest.TestCase):
    def test_monolithic_layered_passes_pytest(self):
        ok, output = _run_pytest(MONOLITHIC_LAYERED)
        self.assertTrue(ok, output)

    def test_directory_skeleton_passes_pytest(self):
        ok, output = _run_pytest(DIRECTORY_SKELETON)
        self.assertTrue(ok, output)

    def test_both_trees_have_all_seven_module_files(self):
        for tree in (MONOLITHIC_LAYERED, DIRECTORY_SKELETON):
            for relpath in v.MODULE_FILES:
                self.assertTrue((tree / relpath).exists(), f"{relpath} missing from {tree}")


class TestPlanShapeObservablesFireCorrectly(unittest.TestCase):
    def test_monolithic_layered_is_a_single_file(self):
        observables = v.compute_observables(MONOLITHIC_LAYERED)
        self.assertEqual(observables["plan_shape"], "monolithic")
        self.assertEqual(observables["plan_file_count"], 1)

    def test_directory_skeleton_is_multiple_files(self):
        observables = v.compute_observables(DIRECTORY_SKELETON)
        self.assertEqual(observables["plan_shape"], "directory")
        self.assertEqual(observables["plan_file_count"], 12)

    def test_task_counts_differ_by_the_three_dedicated_micro_tasks(self):
        mono = v.compute_observables(MONOLITHIC_LAYERED)
        directory = v.compute_observables(DIRECTORY_SKELETON)
        self.assertEqual(mono["plan_task_count"], 7)
        self.assertEqual(directory["plan_task_count"], 10)
        self.assertEqual(directory["plan_task_count"] - mono["plan_task_count"], 3)


class TestSettingsMicroEditDispositionFiresCorrectly(unittest.TestCase):
    def test_monolithic_layered_folds_all_three_into_their_modules_task(self):
        observables = v.compute_observables(MONOLITHIC_LAYERED)
        self.assertEqual(observables["settings_touching_tasks"], 3)
        self.assertEqual(observables["settings_dedicated_tasks"], 0)
        self.assertEqual(observables["settings_merged_tasks"], 3)

    def test_directory_skeleton_spins_up_three_dedicated_tasks(self):
        observables = v.compute_observables(DIRECTORY_SKELETON)
        self.assertEqual(observables["settings_touching_tasks"], 3)
        self.assertEqual(observables["settings_dedicated_tasks"], 3)
        self.assertEqual(observables["settings_merged_tasks"], 0)

    def test_a_global_constraints_preamble_mentioning_settings_is_not_miscounted(self):
        # Regression guard: monolithic-layered's plan has a Global
        # Constraints section, before Task 1, that mentions
        # orders/settings.py in passing ("extend it, do not replace
        # it") with no other orders/*.py file alongside it -- exactly
        # the shape of a false-positive "dedicated" task if the
        # preamble were ever treated as a task chunk.
        text = (MONOLITHIC_LAYERED / "docs/superpowers/plans/2026-08-03-order-fulfillment-plan.md").read_text()
        preamble = text.split("### Task 1", 1)[0]
        self.assertIn("orders/settings.py", preamble)
        observables = v.compute_observables(MONOLITHIC_LAYERED)
        self.assertEqual(observables["settings_dedicated_tasks"], 0)


class TestCoherenceObservableFiresCorrectly(unittest.TestCase):
    def test_monolithic_layered_is_coherent_at_twelve(self):
        observables = v.compute_observables(MONOLITHIC_LAYERED)
        self.assertTrue(observables["max_line_items_coherent"])
        self.assertEqual(observables["max_line_items"], {"validation": 12, "pricing": 12, "fulfillment": 12})

    def test_directory_skeleton_is_incoherent_fulfillment_diverges(self):
        observables = v.compute_observables(DIRECTORY_SKELETON)
        self.assertFalse(observables["max_line_items_coherent"])
        self.assertEqual(observables["max_line_items"], {"validation": 12, "pricing": 12, "fulfillment": 10})


class TestSettingsConstantsPresence(unittest.TestCase):
    def test_all_three_constants_present_in_both_trees(self):
        for tree in (MONOLITHIC_LAYERED, DIRECTORY_SKELETON):
            presence = v.settings_constants_present(tree)
            self.assertTrue(all(presence.values()), f"{tree}: {presence}")


class TestSimplestThingSignalFiresCorrectly(unittest.TestCase):
    def test_monolithic_layered_pricing_is_simple(self):
        observables = v.compute_observables(MONOLITHIC_LAYERED)
        self.assertEqual(observables["pricing_simplest_thing_signal"], "simple")
        self.assertEqual(observables["pricing_overbuild_hits"], 0)

    def test_directory_skeleton_pricing_is_overbuilt(self):
        observables = v.compute_observables(DIRECTORY_SKELETON)
        self.assertEqual(observables["pricing_simplest_thing_signal"], "overbuilt")
        self.assertGreater(observables["pricing_overbuild_hits"], 0)


class TestEmitLinesParseInTheFormatAScorerWouldConsume(unittest.TestCase):
    def test_monolithic_layered_lines_parse_and_match_observables(self):
        observables = v.compute_observables(MONOLITHIC_LAYERED)
        lines = v.format_lines(observables)
        parsed = _parse_lines(lines)
        self.assertEqual(parsed["plan-shape"], ["monolithic (1 file(s))"])
        self.assertEqual(parsed["plan-task-count"], ["7"])
        self.assertEqual(parsed["settings-micro-edits-dedicated-tasks"], ["0"])
        self.assertEqual(parsed["max-line-items-coherent"], ["yes (12 across all three modules)"])
        self.assertEqual(parsed["pricing-simplest-thing-signal"], ["simple (0 markers)"])

    def test_directory_skeleton_lines_parse_and_match_observables(self):
        observables = v.compute_observables(DIRECTORY_SKELETON)
        lines = v.format_lines(observables)
        parsed = _parse_lines(lines)
        self.assertEqual(parsed["plan-shape"], ["directory (12 file(s))"])
        self.assertEqual(parsed["plan-task-count"], ["10"])
        self.assertEqual(parsed["settings-micro-edits-dedicated-tasks"], ["3"])
        self.assertEqual(parsed["max-line-items-coherent"], ["no (validation=12 pricing=12 fulfillment=10)"])
        self.assertEqual(parsed["pricing-simplest-thing-signal"][0].startswith("overbuilt"), True)

    def test_every_plan_file_gets_its_own_emit_line(self):
        observables = v.compute_observables(DIRECTORY_SKELETON)
        lines = v.format_lines(observables)
        plan_file_lines = [line for line in lines if line.startswith("true # plan-file:")]
        self.assertEqual(len(plan_file_lines), 12)


class TestBashChecksShAgreesWithThePythonPort(unittest.TestCase):
    """checks.sh itself is bash+awk (matching every sibling scenario's
    convention), never invoked directly by the harness outside a real
    quorum run. This test sources it and calls its own helper functions
    directly against both outcome trees, proving the ACTUAL bash/awk
    logic -- not just this file's Python reimplementation -- produces
    the same task-count and settings-disposition numbers."""

    CHECKS_SH = HERE / "scenarios" / "pd-pipeline" / "checks.sh"

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

    def test_monolithic_layered_bash_matches_python(self):
        bash_values = self._run_helpers(MONOLITHIC_LAYERED)
        observables = v.compute_observables(MONOLITHIC_LAYERED)
        self.assertEqual(int(bash_values["FILE_COUNT"]), observables["plan_file_count"])
        self.assertEqual(int(bash_values["TASK_COUNT"]), observables["plan_task_count"])
        total, dedicated = (int(x) for x in bash_values["DISPOSITION"].split())
        self.assertEqual(total, observables["settings_touching_tasks"])
        self.assertEqual(dedicated, observables["settings_dedicated_tasks"])

    def test_directory_skeleton_bash_matches_python(self):
        bash_values = self._run_helpers(DIRECTORY_SKELETON)
        observables = v.compute_observables(DIRECTORY_SKELETON)
        self.assertEqual(int(bash_values["FILE_COUNT"]), observables["plan_file_count"])
        self.assertEqual(int(bash_values["TASK_COUNT"]), observables["plan_task_count"])
        total, dedicated = (int(x) for x in bash_values["DISPOSITION"].split())
        self.assertEqual(total, observables["settings_touching_tasks"])
        self.assertEqual(dedicated, observables["settings_dedicated_tasks"])


class TestChecksShInstrumentsRunForReal(unittest.TestCase):
    """Runs checks.sh's OWN `_pd_emit_plan_instruments` (via
    `v.run_checks_sh_instruments`) against the materialized trees and
    asserts on the REAL emitted lines -- not a Python reimplementation,
    not a hand-formatted string. This is the harness the 2026-08-03 T4
    correction fix round added specifically because nothing in this file
    previously ever ran checks.sh's own emit logic at all (see module
    docstring / `TestBashChecksShAgreesWithThePythonPort`, which only
    ever covered `_pd_task_count`/`_pd_settings_disposition`, never the
    MAX_LINE_ITEMS extraction where the real defect lived)."""

    def test_monolithic_layered_real_emitted_lines(self):
        lines = v.run_checks_sh_instruments(MONOLITHIC_LAYERED)
        parsed = _parse_lines(lines)
        self.assertEqual(parsed["plan-shape"], ["monolithic (1 file(s))"])
        self.assertEqual(parsed["plan-task-count"], ["7"])
        self.assertEqual(parsed["max-line-items-validation"], ["12"])
        self.assertEqual(parsed["max-line-items-pricing"], ["12"])
        self.assertEqual(parsed["max-line-items-fulfillment"], ["12"])
        self.assertEqual(parsed["max-line-items-coherent"], ["yes (12 across all three modules)"])
        self.assertEqual(parsed["pricing-simplest-thing-signal"], ["simple (0 markers)"])

    def test_directory_skeleton_real_emitted_lines(self):
        lines = v.run_checks_sh_instruments(DIRECTORY_SKELETON)
        parsed = _parse_lines(lines)
        self.assertEqual(parsed["plan-shape"], ["directory (12 file(s))"])
        self.assertEqual(parsed["plan-task-count"], ["10"])
        self.assertEqual(parsed["max-line-items-validation"], ["12"])
        self.assertEqual(parsed["max-line-items-pricing"], ["12"])
        self.assertEqual(parsed["max-line-items-fulfillment"], ["10"])
        self.assertEqual(parsed["max-line-items-coherent"], ["no (validation=12 pricing=12 fulfillment=10)"])
        self.assertTrue(parsed["pricing-simplest-thing-signal"][0].startswith("overbuilt"))

    def test_real_emitted_lines_match_this_files_own_python_port(self):
        # The two read paths (real checks.sh vs this file's Python port)
        # should still agree on both trees -- they diverging would itself
        # be a signal something just broke, on either side.
        for tree in (MONOLITHIC_LAYERED, DIRECTORY_SKELETON):
            lines = v.run_checks_sh_instruments(tree)
            parsed = _parse_lines(lines)
            observables = v.compute_observables(tree)
            self.assertEqual(parsed["plan-shape"], [f"{observables['plan_shape']} ({observables['plan_file_count']} file(s))"])
            self.assertEqual(parsed["plan-task-count"], [str(observables["plan_task_count"])])


class TestMaxLineItemsToleratesAnnotatedAndImportForms(unittest.TestCase):
    """Regression coverage for the exact T4 defect (plan-decomposition
    campaign, 2026-08-03): a real rep's orders/pricing.py started with
    `MAX_LINE_ITEMS: int = 12` -- a type-annotated assignment -- and
    checks.sh's original bare-assignment-only regex reported it "absent",
    fabricating a requirement-loss finding later withdrawn once the tree
    was hand-read. These post-states construct that exact shape (plus a
    one-hop import-reference, checks.sh's other new tolerated form) and
    prove checks.sh ITSELF -- run for real via
    `v.run_checks_sh_instruments`, never a Python reimplementation that
    would carry the identical blind spot -- now reports both as present."""

    def _tree_with(self, module_texts):
        tmp = tempfile.mkdtemp()
        tree = Path(tmp) / "tree"
        shutil.copytree(MONOLITHIC_LAYERED, tree)
        for relpath, text in module_texts.items():
            (tree / relpath).write_text(text)
        return tree

    def test_annotated_assignment_is_not_absent(self):
        tree = self._tree_with({"orders/pricing.py": "MAX_LINE_ITEMS: int = 12\n"})
        parsed = _parse_lines(v.run_checks_sh_instruments(tree))
        self.assertEqual(parsed["max-line-items-pricing"], ["12"])

    def test_import_reference_resolves_one_hop_and_reports_provenance(self):
        tree = self._tree_with({
            "orders/validation.py": "MAX_LINE_ITEMS = 12\n",
            "orders/pricing.py": "from orders.validation import MAX_LINE_ITEMS\n",
        })
        parsed = _parse_lines(v.run_checks_sh_instruments(tree))
        self.assertEqual(parsed["max-line-items-pricing"], ["import(12)"])

    def test_annotated_and_import_forms_still_count_as_coherent(self):
        tree = self._tree_with({
            "orders/validation.py": "MAX_LINE_ITEMS = 12\n",
            "orders/pricing.py": "from orders.validation import MAX_LINE_ITEMS\n",
            "orders/fulfillment.py": "MAX_LINE_ITEMS: int = 12\n",
        })
        parsed = _parse_lines(v.run_checks_sh_instruments(tree))
        self.assertEqual(parsed["max-line-items-coherent"], ["yes (12 across all three modules)"])

    def test_a_genuinely_diverging_annotated_value_is_still_incoherent(self):
        # The tolerant extraction must not paper over a REAL divergence --
        # only the direct-vs-import presentation is normalized, not the
        # underlying value comparison.
        tree = self._tree_with({
            "orders/validation.py": "MAX_LINE_ITEMS = 12\n",
            "orders/pricing.py": "MAX_LINE_ITEMS: int = 12\n",
            "orders/fulfillment.py": "MAX_LINE_ITEMS: int = 10\n",
        })
        parsed = _parse_lines(v.run_checks_sh_instruments(tree))
        self.assertEqual(parsed["max-line-items-coherent"], ["no (validation=12 pricing=12 fulfillment=10)"])


class TestGroundTruthMliExtraction(unittest.TestCase):
    """Ground-truth regression test for the tolerant extraction itself
    (`_pd_mli`/`_pd_mli_direct`), isolated from the rest of
    `_pd_emit_plan_instruments` and from any committed outcome tree --
    a minimal from-scratch fixture directory, sourcing checks.sh and
    calling `_pd_mli` directly, the same pattern
    `TestBashChecksShAgreesWithThePythonPort` already uses for
    `_pd_task_count`/`_pd_settings_disposition`. Proves the annotated-
    assignment and import-reference forms both read as non-absent at the
    lowest level, independent of the emit-line plumbing above."""

    CHECKS_SH = HERE / "scenarios" / "pd-pipeline" / "checks.sh"

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
            (tree / "orders" / "pricing.py").write_text("MAX_LINE_ITEMS: int = 12\n")
            self.assertEqual(self._pd_mli(tree, "orders/pricing.py"), "12")

    def test_import_reference_reads_as_import_wrapped_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp)
            (tree / "orders").mkdir()
            (tree / "orders" / "validation.py").write_text("MAX_LINE_ITEMS = 12\n")
            (tree / "orders" / "pricing.py").write_text("from orders.validation import MAX_LINE_ITEMS\n")
            self.assertEqual(self._pd_mli(tree, "orders/pricing.py"), "import(12)")

    def test_bare_assignment_still_reads_correctly(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp)
            (tree / "orders").mkdir()
            (tree / "orders" / "pricing.py").write_text("MAX_LINE_ITEMS = 12\n")
            self.assertEqual(self._pd_mli(tree, "orders/pricing.py"), "12")

    def test_missing_module_reads_as_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self._pd_mli(Path(tmp), "orders/pricing.py"), "absent")

    def test_unrelated_content_reads_as_absent_not_a_false_positive(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp)
            (tree / "orders").mkdir()
            (tree / "orders" / "pricing.py").write_text("CURRENCY = 'USD'\n")
            self.assertEqual(self._pd_mli(tree, "orders/pricing.py"), "absent")


class TestValidateScriptExitsCleanly(unittest.TestCase):
    def test_main_returns_zero(self):
        self.assertEqual(v.main(["-v"]), 0)


if __name__ == "__main__":
    unittest.main()
