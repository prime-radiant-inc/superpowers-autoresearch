"""Tests for score_pd_coherence.py (plan-decomposition campaign, Task 2c).

Tree mode is a thin wrapper around the already-validated
x10-consistency-scan.py (>=5/5 seeded defects / <=5 false positives --
test_x10_consistency_scan.py); this file only proves the wiring calls
through correctly, using the same fixtures that module's own tests
already trust, plus the real pd-pipeline fixture trees.

Plan-text mode's constant-divergence detector is exercised against the
real, committed pd-pipeline fixture (monolithic-layered / directory-
skeleton), whose own plan text is coherent by construction (only the
FINAL CODE diverges in directory-skeleton, per its own design -- see
probe-design-notes.md), so the true-negative case is real corpus data,
not invented; the true-positive (an actual injected divergence) is a
small constructed fixture, since no real plan text with a stated
divergence exists yet.

Everything here is synthetic or reuses already-committed synthetic
fixtures; no real system.
"""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import validate_pd_pipeline as v  # noqa: E402

MONOLITHIC_LAYERED = v.MONOLITHIC_LAYERED
DIRECTORY_SKELETON = v.DIRECTORY_SKELETON


class TestTreeCoherenceReportWiring(unittest.TestCase):
    def test_wraps_x10_scan_repo_directly(self):
        import score_pd_coherence as c
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.py").write_text("MAX_RETRIES = 3\n")
            (root / "b.py").write_text("MAX_RETRIES = 5\n")
            wired = c.tree_coherence_report(tmp)
            direct = c.x10.scan_repo(tmp)
            self.assertEqual(
                [(f.category, f.description) for f in wired["findings"]],
                [(f.category, f.description) for f in direct["findings"]],
            )
            self.assertTrue(any(f.category == "constant-divergence" for f in wired["findings"]))

    def test_clean_tree_has_no_findings(self):
        import score_pd_coherence as c
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "a.py").write_text("MAX_RETRIES = 3\n")
            result = c.tree_coherence_report(tmp)
            self.assertEqual(result["findings"], [])


class TestPlanConstants(unittest.TestCase):
    def test_extracts_equals_style_assignment(self):
        import score_pd_coherence as c
        self.assertEqual(c.plan_constants("`MAX_LINE_ITEMS = 12`"), [("MAX_LINE_ITEMS", "12", 1)])

    def test_extracts_colon_style_assignment(self):
        import score_pd_coherence as c
        self.assertEqual(c.plan_constants("- MAX_LINE_ITEMS: 25"), [("MAX_LINE_ITEMS", "25", 1)])

    def test_extracts_quoted_string_value(self):
        import score_pd_coherence as c
        self.assertEqual(c.plan_constants('CURRENCY = "USD"'), [("CURRENCY", "USD", 1)])

    def test_ordinary_capitalized_prose_word_does_not_qualify(self):
        # "Task" and "SPEC" are not ALL_CAPS (lowercase letters in the
        # middle) -- must never be mistaken for a constant name.
        import score_pd_coherence as c
        self.assertEqual(c.plan_constants("### Task 1: reads SPEC.md for details"), [])

    def test_line_numbers_are_one_indexed_and_correct(self):
        import score_pd_coherence as c
        text = "line one\nline two\nMAX_RETRIES = 3\n"
        self.assertEqual(c.plan_constants(text), [("MAX_RETRIES", "3", 3)])


class TestPlanSections(unittest.TestCase):
    def test_monolithic_file_splits_by_task_header_with_preamble(self):
        import score_pd_coherence as c
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plan.md"
            path.write_text(
                "# Plan\n\n## Global Constraints\n\nMAX_LINE_ITEMS = 12\n\n"
                "### Task 1: Validation\n\nUse MAX_LINE_ITEMS = 12 here.\n\n"
                "### Task 2: Pricing\n\nUse MAX_LINE_ITEMS = 12 here too.\n"
            )
            sections = c.plan_sections([path])
            labels = [label for label, _ in sections]
            self.assertEqual(labels, ["preamble", "Task 1: Validation", "Task 2: Pricing"])

    def test_no_task_headers_yields_one_whole_file_section(self):
        import score_pd_coherence as c
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plan.md"
            path.write_text("Just some notes, no task headers at all.\n")
            sections = c.plan_sections([path])
            self.assertEqual([label for label, _ in sections], ["<whole-file>"])

    def test_directory_of_files_uses_filename_as_section_label(self):
        import score_pd_coherence as c
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "task-01.md"
            a.write_text("MAX_LINE_ITEMS = 12\n")
            b = Path(tmp) / "task-02.md"
            b.write_text("MAX_LINE_ITEMS = 10\n")
            sections = c.plan_sections([a, b])
            self.assertEqual([label for label, _ in sections], ["task-01.md", "task-02.md"])

    def test_real_pd_pipeline_directory_skeleton_sections(self):
        # Real fixture data -- confirms the section splitter handles the
        # actual committed plan directory, not just a synthetic stand-in.
        import score_pd_coherence as c
        files = sorted((DIRECTORY_SKELETON / "docs" / "superpowers" / "plans").rglob("*.md"))
        sections = c.plan_sections(files)
        self.assertEqual(len(sections), len(files))


class TestPlanConstantDivergence(unittest.TestCase):
    def test_same_value_across_sections_is_not_divergence(self):
        import score_pd_coherence as c
        sections = [("Task 1", "MAX_LINE_ITEMS = 12"), ("Task 2", "MAX_LINE_ITEMS = 12")]
        self.assertEqual(c.plan_constant_divergence(sections), [])

    def test_different_value_across_sections_is_flagged(self):
        import score_pd_coherence as c
        sections = [("Task 1", "MAX_LINE_ITEMS = 12"), ("Task 2", "MAX_LINE_ITEMS = 25")]
        findings = c.plan_constant_divergence(sections)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].category, "plan-constant-divergence")
        self.assertIn("MAX_LINE_ITEMS", findings[0].description)

    def test_same_section_restating_the_same_value_is_not_divergence(self):
        import score_pd_coherence as c
        sections = [("Task 1", "MAX_LINE_ITEMS = 12\n...\nVerification uses MAX_LINE_ITEMS = 12 too.")]
        self.assertEqual(c.plan_constant_divergence(sections), [])

    def test_finding_sites_cite_section_label_and_line(self):
        import score_pd_coherence as c
        sections = [("Task 1", "MAX_LINE_ITEMS = 12"), ("Task 2", "MAX_LINE_ITEMS = 25")]
        findings = c.plan_constant_divergence(sections)
        labels = {site[0] for site in findings[0].sites}
        self.assertEqual(labels, {"Task 1", "Task 2"})

    def test_real_pd_pipeline_monolithic_layered_plan_text_is_coherent(self):
        # True negative on real corpus data: the plan TEXT states
        # MAX_LINE_ITEMS = 12 identically in every task that mentions it
        # (only the fulfillment module's FINAL CODE diverges in
        # directory-skeleton, and even there the plan text itself never
        # states a literal divergent number -- see probe-design-notes.md).
        import score_pd_coherence as c
        plan_path = list((MONOLITHIC_LAYERED / "docs" / "superpowers" / "plans").glob("*.md"))
        report = c.plan_coherence_report(plan_path)
        self.assertEqual(report["findings"], [])

    def test_real_pd_pipeline_directory_skeleton_plan_text_is_coherent(self):
        import score_pd_coherence as c
        files = sorted((DIRECTORY_SKELETON / "docs" / "superpowers" / "plans").rglob("*.md"))
        report = c.plan_coherence_report(files)
        self.assertEqual(report["findings"], [])

    def test_injected_divergence_is_caught_on_a_constructed_directory_plan(self):
        # True positive: a constructed plan directory where one task
        # section's own stated constant literally disagrees with another.
        import score_pd_coherence as c
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "task-02-validation.md").write_text("### Task 2: Validation\n\n`MAX_LINE_ITEMS = 12`\n")
            (root / "task-04-fulfillment.md").write_text("### Task 4: Fulfillment\n\n`MAX_LINE_ITEMS = 10`\n")
            report = c.plan_coherence_report(sorted(root.glob("*.md")))
            self.assertEqual(len(report["findings"]), 1)
            self.assertEqual(report["findings"][0].category, "plan-constant-divergence")


class TestFindingsToJsonAndCLI(unittest.TestCase):
    def test_findings_serialize_to_json_shape(self):
        import score_pd_coherence as c
        sections = [("Task 1", "MAX_LINE_ITEMS = 12"), ("Task 2", "MAX_LINE_ITEMS = 25")]
        result = {"findings": c.plan_constant_divergence(sections), "total_before_cap": 1, "suppressed": 0}
        payload = c._findings_to_json(result)
        self.assertEqual(payload["total_before_cap"], 1)
        self.assertEqual(len(payload["findings"]), 1)
        self.assertEqual(payload["findings"][0]["category"], "plan-constant-divergence")

    def test_main_plan_mode_prints_json(self):
        import contextlib
        import io
        import json as jsonlib
        import score_pd_coherence as c
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "task-01.md"
            a.write_text("MAX_LINE_ITEMS = 12\n")
            b = Path(tmp) / "task-02.md"
            b.write_text("MAX_LINE_ITEMS = 10\n")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = c.main(["score_pd_coherence.py", "plan", str(a), str(b)])
            self.assertEqual(rc, 0)
            payload = jsonlib.loads(buf.getvalue())
            self.assertEqual(payload["total_before_cap"], 1)

    def test_main_unknown_mode_errors(self):
        import score_pd_coherence as c
        rc = c.main(["score_pd_coherence.py", "bogus", "x"])
        self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
