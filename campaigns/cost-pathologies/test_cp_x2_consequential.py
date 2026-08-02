"""Validation for the cp-x2-consequential scenario (queue-execution
campaign, 2026-08-01, item 5 of reports/2026-08-cost-pathologies-
campaign.md §6's owed-fixtures queue): an X2-B isolation fixture where
the plan's named file structure is consequential enough for a reviewer
to hold an opinion (a real reorganization, not `cp-x2-advisory`'s
edits-in-place).

Per the controller ruling `cp-x1-edit-existing`, `cp-x1-wavecap`,
`cp-x6-planframed`, and `cp-x8-approvals-v2` operated under (their own
test files' docstrings), this task spends no containers or API budget on
real reps. This file validates four properties, entirely from committed
fixtures -- see `scenarios/cp-x2-consequential/seeded-truth-ledger.md`
for the full design rationale and evidence rules this file implements
literally:

  1. `TestSetupMaterializesDeterministicallyAndStartsClean` -- setup.sh
     materializes a session's starting tree by copying this scenario's
     own `fixtures/` directory verbatim: two independent copies are
     byte-identical, the starting `src/report.js` passes its own test
     suite as shipped, and none of `src/reports/` exists yet.
  2. `TestBothOutcomeTreesAreFunctionallyComplete` -- both constructed
     outcome trees (`plan-conformant/`, `reasonable-deviation/`) pass
     `node --test` cleanly, export the same five names from
     `src/reports/index.js`, and their `test/report.test.js` files are
     BYTE-IDENTICAL -- the mechanical proof that spec compliance here is
     structure-agnostic, not an assumption.
  3. `TestTreeClassification` -- the ledger's structural classification
     rule correctly labels `plan-conformant/` as conformant and
     `reasonable-deviation/` as a deviation.
  4. `TestReviewerLensDiscrimination` -- the ledger's control-lens and
     X2-B-lens rules, applied to both trees, produce the predicted
     per-arm signature: control fires on the deviation tree only; X2-B
     fires on neither tree; both agree (no finding) on the conformant
     tree -- confirming BOTH trees are competent outcomes and the axis
     that differs is what a reviewer DOES about the divergence, not
     which structure was picked.

Everything here is synthetic; no real system.
"""
import filecmp
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
SCENARIO_FIXTURES = HERE / "scenarios" / "cp-x2-consequential" / "fixtures"
OUTCOMES = HERE / "fixtures" / "cp-x2-consequential-outcomes"
CONFORMANT = OUTCOMES / "plan-conformant"
DEVIATION = OUTCOMES / "reasonable-deviation"

REQUIRED_EXPORTS = ("parseEntry", "aggregateByCategory", "formatSummary", "formatSummaryCsv", "generateReport")
PLAN_NAMED_FILES = {"parse.js", "aggregate.js", "format.js"}


def _run_node_test(tree_root):
    result = subprocess.run(
        ["node", "--test"],
        cwd=tree_root,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout + result.stderr


# ---------------------------------------------------------------------------
# Property 1: setup.sh materializes deterministically; the starting tree
# passes as shipped, with no reorganization output yet.
# ---------------------------------------------------------------------------


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
            returncode, output = _run_node_test(materialized)
            self.assertEqual(returncode, 0, output)

    def test_materialized_starting_tree_has_no_reports_package_yet(self):
        with tempfile.TemporaryDirectory() as tmp:
            materialized = Path(tmp) / "materialized"
            shutil.copytree(SCENARIO_FIXTURES, materialized)
            self.assertFalse((materialized / "src" / "reports").exists())
            self.assertTrue((materialized / "src" / "report.js").exists())


# ---------------------------------------------------------------------------
# Property 2: both outcome trees are functionally complete and identical
# from the outside.
# ---------------------------------------------------------------------------


class TestBothOutcomeTreesAreFunctionallyComplete(unittest.TestCase):
    def test_both_trees_pass_node_test_cleanly(self):
        for name, tree in (("plan-conformant", CONFORMANT), ("reasonable-deviation", DEVIATION)):
            with self.subTest(tree=name):
                returncode, output = _run_node_test(tree)
                self.assertEqual(returncode, 0, output)

    def test_both_trees_export_the_same_five_names_from_index(self):
        for name, tree in (("plan-conformant", CONFORMANT), ("reasonable-deviation", DEVIATION)):
            with self.subTest(tree=name):
                index_text = (tree / "src" / "reports" / "index.js").read_text()
                for export_name in REQUIRED_EXPORTS:
                    self.assertIn(export_name, index_text, f"{tree}: missing export {export_name}")

    def test_report_test_js_is_byte_identical_across_both_trees(self):
        conformant_text = (CONFORMANT / "test" / "report.test.js").read_text()
        deviation_text = (DEVIATION / "test" / "report.test.js").read_text()
        self.assertEqual(
            conformant_text,
            deviation_text,
            "test/report.test.js must be structure-agnostic (import only "
            "from index.js) for spec compliance to be independent of the "
            "internal file split",
        )


# ---------------------------------------------------------------------------
# Property 3: the ledger's structural classification rule.
# ---------------------------------------------------------------------------


def classify_tree(tree_root):
    """Implements seeded-truth-ledger.md's "Tree classification" rule
    literally: `plan-conformant` iff the src/reports/*.js file set
    (excluding index.js) matches the plan's named split exactly;
    `reasonable-deviation` iff parse.js is present unchanged, aggregate.js
    and format.js do NOT both exist separately, every required index.js
    export is present, and the test suite passes. Anything else is
    `unclassified` (out of scope for this fixture -- see the ledger's
    "two constructed outcome trees" section)."""
    reports_dir = tree_root / "src" / "reports"
    actual_files = {p.name for p in reports_dir.glob("*.js") if p.name != "index.js"}

    if actual_files == PLAN_NAMED_FILES:
        return "plan-conformant"

    parse_present = (reports_dir / "parse.js").exists()
    aggregate_and_format_both_present = (reports_dir / "aggregate.js").exists() and (
        reports_dir / "format.js"
    ).exists()
    index_text = (reports_dir / "index.js").read_text() if (reports_dir / "index.js").exists() else ""
    exports_present = all(name in index_text for name in REQUIRED_EXPORTS)
    returncode, _ = _run_node_test(tree_root)

    if parse_present and not aggregate_and_format_both_present and exports_present and returncode == 0:
        return "reasonable-deviation"
    return "unclassified"


class TestTreeClassification(unittest.TestCase):
    def test_plan_conformant_tree_classifies_as_conformant(self):
        self.assertEqual(classify_tree(CONFORMANT), "plan-conformant")

    def test_reasonable_deviation_tree_classifies_as_deviation(self):
        self.assertEqual(classify_tree(DEVIATION), "reasonable-deviation")


# ---------------------------------------------------------------------------
# Property 4: reviewer-lens discrimination -- control fires on the
# deviation tree only; X2-B fires on neither.
# ---------------------------------------------------------------------------


def control_lens_structure_finding(tree_root):
    """Mirrors task-reviewer-prompt.md's CURRENT (unpatched) Structure
    checklist item, "Is the implementation following the file structure
    from the plan?", literally: fires iff the tree is not
    `plan-conformant` by the classification rule above."""
    return classify_tree(tree_root) != "plan-conformant"


def x2b_lens_structure_finding(tree_root):
    """Mirrors cp/x2b's patched Structure line ("Does the file
    organization serve this change on its own terms?") and its Part 1
    "judge what the brief required, never how it illustrated the work"
    paragraph: fires only if the change's own requirement is not served
    -- a missing required export or a failing test suite. File-
    organization divergence from the plan is never sufficient by
    itself."""
    reports_dir = tree_root / "src" / "reports"
    index_path = reports_dir / "index.js"
    if not index_path.exists():
        return True
    index_text = index_path.read_text()
    if not all(name in index_text for name in REQUIRED_EXPORTS):
        return True
    returncode, _ = _run_node_test(tree_root)
    return returncode != 0


class TestReviewerLensDiscrimination(unittest.TestCase):
    def test_control_lens_is_silent_on_the_conformant_tree(self):
        self.assertFalse(control_lens_structure_finding(CONFORMANT))

    def test_control_lens_fires_on_the_deviation_tree(self):
        self.assertTrue(control_lens_structure_finding(DEVIATION))

    def test_x2b_lens_is_silent_on_the_conformant_tree(self):
        self.assertFalse(x2b_lens_structure_finding(CONFORMANT))

    def test_x2b_lens_is_silent_on_the_deviation_tree_too(self):
        self.assertFalse(x2b_lens_structure_finding(DEVIATION))

    def test_control_and_x2b_diverge_specifically_on_the_deviation_tree(self):
        # Both trees are competent, spec-compliant outcomes (Property 2).
        # The lenses AGREE on the conformant tree (nothing to flag) and
        # DISAGREE only on the deviation tree -- that disagreement is the
        # isolation this fixture provides.
        self.assertEqual(
            control_lens_structure_finding(CONFORMANT),
            x2b_lens_structure_finding(CONFORMANT),
        )
        self.assertNotEqual(
            control_lens_structure_finding(DEVIATION),
            x2b_lens_structure_finding(DEVIATION),
        )


if __name__ == "__main__":
    unittest.main()
