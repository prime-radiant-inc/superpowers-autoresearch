"""Tests for x10-consistency-scan.py (backlog campaign, 2026-08-02, Task
5): the general cross-module consistency scanner built alongside the
cp-x10-consistency scenario. `x10-consistency-scan.py` is not a valid
Python module name (hyphens), so it is loaded by path via `importlib` --
the same idiom test_x2b_review_micro.py already uses for the same reason.

Two required properties (task-5 brief):

  - the scanner detects >=5/5 of the fixture's seeded defects
    (seeded-truth-ledger.md) when run against
    fixtures/cp-x10-consistency-outcomes/complete/.
  - the scanner produces <=5 false-positive finding lines when run
    against the scenario's own clean pre-state
    (scenarios/cp-x10-consistency/fixtures/).

Plus unit tests for each detector in isolation, against small synthetic
ASTs, and for the top-N ranking/cap behavior.

Everything here is synthetic; no real system.
"""
import ast
import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).parent
COMPLETE = HERE / "fixtures" / "cp-x10-consistency-outcomes" / "complete"
CLEAN_PRE_STATE = HERE / "scenarios" / "cp-x10-consistency" / "fixtures"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


scan = _load("x10_consistency_scan", HERE / "x10-consistency-scan.py")


def _facts_from_source(source, filename):
    tree = ast.parse(source, filename=filename)
    collector = scan.LiteralGroupCollector()
    collector.visit(tree)
    return scan.FileFacts(
        path=pathlib.Path(filename),
        constants=list(scan._module_level_constants(tree)),
        raises=list(scan._raise_sites(tree)),
        literal_groups=dict(collector.groups),
    )


# ---------------------------------------------------------------------------
# Detector 1: constant divergence
# ---------------------------------------------------------------------------


class TestConstantDivergenceDetector(unittest.TestCase):
    def test_same_name_different_value_across_files_flagged(self):
        a = _facts_from_source("TIMEOUT_SECONDS = 30\n", "a.py")
        b = _facts_from_source("TIMEOUT_SECONDS = 90\n", "b.py")
        findings = scan.detect_constant_divergence([a, b])
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].category, "constant-divergence")
        files = {site[0] for site in findings[0].sites}
        self.assertEqual(files, {"a.py", "b.py"})

    def test_same_name_same_value_not_flagged(self):
        a = _facts_from_source("TIMEOUT_SECONDS = 30\n", "a.py")
        b = _facts_from_source("TIMEOUT_SECONDS = 30\n", "b.py")
        self.assertEqual(scan.detect_constant_divergence([a, b]), [])

    def test_same_value_in_one_file_only_not_flagged(self):
        a = _facts_from_source("TIMEOUT_SECONDS = 30\nOTHER = 30\n", "a.py")
        self.assertEqual(scan.detect_constant_divergence([a]), [])

    def test_blocklisted_names_ignored(self):
        a = _facts_from_source('__version__ = "1.0"\n', "a.py")
        b = _facts_from_source('__version__ = "2.0"\n', "b.py")
        self.assertEqual(scan.detect_constant_divergence([a, b]), [])

    def test_constant_inside_function_is_not_module_level(self):
        a = _facts_from_source("def f():\n    TIMEOUT_SECONDS = 30\n    return TIMEOUT_SECONDS\n", "a.py")
        b = _facts_from_source("TIMEOUT_SECONDS = 90\n", "b.py")
        self.assertEqual(scan.detect_constant_divergence([a, b]), [])


# ---------------------------------------------------------------------------
# Detector 2a: naming-drift constants
# ---------------------------------------------------------------------------


class TestNamingDriftConstantsDetector(unittest.TestCase):
    def test_near_miss_names_same_value_flagged(self):
        a = _facts_from_source("RETRY_LIMIT = 4\n", "worker.py")
        b = _facts_from_source("MAX_RETRY_ATTEMPTS = 4\n", "scheduler.py")
        findings = scan.detect_naming_drift_constants([a, b])
        self.assertEqual(len(findings), 1)
        self.assertIn("RETRY_LIMIT", findings[0].description)
        self.assertIn("MAX_RETRY_ATTEMPTS", findings[0].description)

    def test_unrelated_names_same_value_not_flagged(self):
        a = _facts_from_source("RETRY_LIMIT = 4\n", "worker.py")
        b = _facts_from_source("PAGE_SIZE = 4\n", "paginator.py")
        self.assertEqual(scan.detect_naming_drift_constants([a, b]), [])

    def test_identical_name_different_files_not_double_flagged(self):
        # Same name is detector 1's job, not detector 2a's.
        a = _facts_from_source("RETRY_LIMIT = 4\n", "worker.py")
        b = _facts_from_source("RETRY_LIMIT = 4\n", "scheduler.py")
        self.assertEqual(scan.detect_naming_drift_constants([a, b]), [])

    def test_same_file_pairs_not_flagged(self):
        a = _facts_from_source("RETRY_LIMIT = 4\nMAX_RETRY_ATTEMPTS = 4\n", "a.py")
        self.assertEqual(scan.detect_naming_drift_constants([a]), [])


# ---------------------------------------------------------------------------
# Detector 2b: naming-drift error messages
# ---------------------------------------------------------------------------


class TestNamingDriftErrorsDetector(unittest.TestCase):
    def test_topically_similar_messages_different_classes_flagged(self):
        a = _facts_from_source(
            'class JobPayloadError(Exception):\n    pass\n\n'
            'def f(field):\n    raise JobPayloadError(f"job payload missing field {field!r}")\n',
            "worker.py",
        )
        b = _facts_from_source(
            'class InvalidSubmissionError(Exception):\n    pass\n\n'
            'def g(field):\n    raise InvalidSubmissionError(f"submission rejected: field {field!r} is required")\n',
            "api.py",
        )
        findings = scan.detect_naming_drift_errors([a, b])
        self.assertEqual(len(findings), 1)
        self.assertIn("JobPayloadError", findings[0].description)
        self.assertIn("InvalidSubmissionError", findings[0].description)

    def test_topically_unrelated_messages_not_flagged(self):
        a = _facts_from_source('def f():\n    raise ValueError("disk full")\n', "a.py")
        b = _facts_from_source('def g():\n    raise TypeError("wrong currency code")\n', "b.py")
        self.assertEqual(scan.detect_naming_drift_errors([a, b]), [])

    def test_same_class_name_not_flagged(self):
        a = _facts_from_source('def f():\n    raise ValueError("missing field x")\n', "a.py")
        b = _facts_from_source('def g():\n    raise ValueError("missing field y")\n', "b.py")
        self.assertEqual(scan.detect_naming_drift_errors([a, b]), [])


# ---------------------------------------------------------------------------
# Detector 3: enum/status asymmetry
# ---------------------------------------------------------------------------


class TestEnumAsymmetryDetector(unittest.TestCase):
    def test_partial_overlap_across_files_flagged(self):
        a = _facts_from_source(
            "def next_status(n):\n    if n < 4:\n        return 'retrying'\n    return 'failed'\n",
            "scheduler.py",
        )
        b = _facts_from_source(
            '_MESSAGES = {"queued": "q", "running": "r", "done": "d", "failed": "f"}\n',
            "notifier.py",
        )
        findings = scan.detect_enum_asymmetry([a, b])
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].category, "enum-asymmetry")

    def test_identical_vocabularies_not_flagged(self):
        a = _facts_from_source(
            '_A = ("queued", "running", "done", "failed")\n', "a.py",
        )
        b = _facts_from_source(
            '_B = {"queued": 1, "running": 2, "done": 3, "failed": 4}\n', "b.py",
        )
        self.assertEqual(scan.detect_enum_asymmetry([a, b]), [])

    def test_disjoint_vocabularies_not_flagged(self):
        a = _facts_from_source('_A = ("queued", "running")\n', "a.py")
        b = _facts_from_source('_B = ("archived", "purged")\n', "b.py")
        self.assertEqual(scan.detect_enum_asymmetry([a, b]), [])

    def test_same_file_groups_not_compared(self):
        a = _facts_from_source(
            '_A = ("queued", "running")\n_B = ("queued", "done")\n', "a.py",
        )
        self.assertEqual(scan.detect_enum_asymmetry([a]), [])


# ---------------------------------------------------------------------------
# Ranking and cap
# ---------------------------------------------------------------------------


class TestRankingAndCap(unittest.TestCase):
    def test_findings_sorted_by_confidence_descending(self):
        findings = [
            scan.Finding("cat", "low", 0.1, [("a.py", 1, "x")]),
            scan.Finding("cat", "high", 0.9, [("a.py", 1, "x")]),
            scan.Finding("cat", "mid", 0.5, [("a.py", 1, "x")]),
        ]
        findings.sort(key=lambda f: f.confidence, reverse=True)
        self.assertEqual([f.description for f in findings], ["high", "mid", "low"])

    def test_scan_repo_caps_at_top_n_and_reports_suppressed_count(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            # 6 files, each pair sharing a distinct divergent constant name
            # -- 6 constant-divergence findings from one name reused across
            # many files would collapse to one finding, so use six
            # distinct pairs instead to get more than `top` findings.
            for i in range(6):
                (root / f"m{i}.py").write_text(f"KNOB_{i} = {i}\n")
                (root / f"n{i}.py").write_text(f"KNOB_{i} = {i + 100}\n")
            result = scan.scan_repo(root, top=3)
            self.assertEqual(len(result["findings"]), 3)
            self.assertEqual(result["total_before_cap"], 6)
            self.assertEqual(result["suppressed"], 3)


# ---------------------------------------------------------------------------
# Integration: the fixture itself (task-5 brief's two required properties)
# ---------------------------------------------------------------------------


class TestFixtureDetectsAllFiveSeededDefects(unittest.TestCase):
    """>=5/5 seeded defects (seeded-truth-ledger.md) must be present among
    the scanner's findings when run against the constructed post-state."""

    @classmethod
    def setUpClass(cls):
        cls.result = scan.scan_repo(COMPLETE, top=20)
        cls.findings = cls.result["findings"]

    def _any_finding_touching(self, *fragments):
        for finding in self.findings:
            text = finding.description + " " + " ".join(s[2] for s in finding.sites)
            if all(fragment in text for fragment in fragments):
                return True
        return False

    def test_defect_1_timeout_seconds_divergence_detected(self):
        self.assertTrue(self._any_finding_touching("TIMEOUT_SECONDS"))

    def test_defect_2_retry_cap_naming_drift_detected(self):
        self.assertTrue(self._any_finding_touching("RETRY_LIMIT", "MAX_RETRY_ATTEMPTS"))

    def test_defect_3_error_message_divergence_detected(self):
        self.assertTrue(self._any_finding_touching("JobPayloadError", "InvalidSubmissionError"))

    def test_defect_4_retrying_status_asymmetry_detected(self):
        self.assertTrue(self._any_finding_touching("retrying"))

    def test_defect_5_min_priority_divergence_detected(self):
        self.assertTrue(self._any_finding_touching("MIN_PRIORITY"))

    def test_all_five_findings_land_within_top_20(self):
        # Redundant with the five tests above (each already searches only
        # `result["findings"]`, which is already capped at top=20) but
        # stated explicitly since it's the brief's own pass condition.
        self.assertLessEqual(len(self.findings), 20)
        matched = sum(
            [
                self._any_finding_touching("TIMEOUT_SECONDS"),
                self._any_finding_touching("RETRY_LIMIT", "MAX_RETRY_ATTEMPTS"),
                self._any_finding_touching("JobPayloadError", "InvalidSubmissionError"),
                self._any_finding_touching("retrying"),
                self._any_finding_touching("MIN_PRIORITY"),
            ]
        )
        self.assertGreaterEqual(matched, 5)


class TestCleanPreStateProducesFewFalsePositives(unittest.TestCase):
    """<=5 false-positive finding lines when run against the scenario's
    own clean pre-state, before any of the six tasks has run."""

    def test_at_most_five_findings_on_clean_pre_state(self):
        result = scan.scan_repo(CLEAN_PRE_STATE, top=20)
        self.assertLessEqual(
            result["total_before_cap"],
            5,
            f"expected <=5 false-positive findings on the clean pre-state, got: "
            f"{[f.format() for f in result['findings']]}",
        )


if __name__ == "__main__":
    unittest.main()
