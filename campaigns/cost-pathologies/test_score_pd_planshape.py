"""Tests for score_pd_planshape.py (plan-decomposition campaign, Task 2a).

The direct-workdir-inspection path is validated against the REAL,
committed pd-pipeline fixture outcomes (fixtures/pd-pipeline-outcomes/
monolithic-layered, directory-skeleton -- built by validate_pd_pipeline.py/
Task 1), reusing its already-known numbers as the ground truth: this
scorer's `micro_edit_disposition`/`overbuild_hits` are a generalization of
that module's `settings_disposition`/`pricing_overbuild_hits`, so agreeing
with them on the SAME trees is the correctness bar.

The verdict.json-emit-line path and the return-window-failure detector
have no real battery rep to validate against yet (pd-pipeline has not run
as a real quorum battery as of this task -- see this task's report), so
those are tested against small constructed fixtures only, mirroring
test_pd_pipeline_fixture.py's own emit-line shape
(`true # label: value`) and test_score_x5_leases.py's inline-JSONL-rollout
style respectively.

Everything here is synthetic or reuses already-committed synthetic
fixtures; no real system.
"""
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import validate_pd_pipeline as v  # noqa: E402

MONOLITHIC_LAYERED = v.MONOLITHIC_LAYERED
DIRECTORY_SKELETON = v.DIRECTORY_SKELETON

SETTINGS_TARGET_RE = re.compile(r"orders/settings\.py")
SETTINGS_SIBLING_RE = re.compile(r"orders/[a-zA-Z_]+\.py")
PRICING_OVERBUILD_RE = re.compile(
    r"class\s+[A-Za-z]*Currency|CurrencyRegistry|SUPPORTED_CURRENCIES"
    r"|abstractmethod|Protocol\[|CurrencyConverter", re.I)


def _rec(ts, typ, payload):
    return json.dumps({"timestamp": ts, "type": typ, "payload": payload})


def custom_exec_cmd(ts, call_id, raw_input):
    return _rec(ts, "response_item", {
        "type": "custom_tool_call", "id": call_id, "name": "exec",
        "input": raw_input, "call_id": call_id})


def exec_cmd(ts, call_id, cmd):
    return _rec(ts, "response_item", {
        "type": "function_call", "id": call_id, "name": "exec_command",
        "arguments": json.dumps({"cmd": cmd}), "call_id": call_id})


def patch_apply_end(ts, success, paths):
    return _rec(ts, "event_msg", {
        "type": "patch_apply_end", "success": success,
        "changes": {p: {} for p in paths}})


def write_rollout(tmpdir, name, lines):
    path = os.path.join(tmpdir, name)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


# ---------------------------------------------------------------------------
# Direct workdir inspection, validated against the real committed fixture.
# ---------------------------------------------------------------------------

class TestPlanShapeReportAgainstRealFixture(unittest.TestCase):
    def test_monolithic_layered_shape_and_task_count(self):
        import score_pd_planshape as p
        report = p.plan_shape_report(MONOLITHIC_LAYERED)
        self.assertEqual(report["plan_shape"], "monolithic")
        self.assertEqual(report["plan_file_count"], 1)
        self.assertEqual(report["plan_task_count"], 7)

    def test_directory_skeleton_shape_and_task_count(self):
        import score_pd_planshape as p
        report = p.plan_shape_report(DIRECTORY_SKELETON)
        self.assertEqual(report["plan_shape"], "directory")
        self.assertEqual(report["plan_file_count"], 12)
        self.assertEqual(report["plan_task_count"], 10)

    def test_monolithic_layered_micro_edit_disposition_all_merged(self):
        import score_pd_planshape as p
        report = p.plan_shape_report(
            MONOLITHIC_LAYERED,
            micro_edit_target=SETTINGS_TARGET_RE, micro_edit_siblings=SETTINGS_SIBLING_RE)
        self.assertEqual(report["micro_edit_touching_tasks"], 3)
        self.assertEqual(report["micro_edit_dedicated_tasks"], 0)
        self.assertEqual(report["micro_edit_merged_tasks"], 3)

    def test_directory_skeleton_micro_edit_disposition_all_dedicated(self):
        import score_pd_planshape as p
        report = p.plan_shape_report(
            DIRECTORY_SKELETON,
            micro_edit_target=SETTINGS_TARGET_RE, micro_edit_siblings=SETTINGS_SIBLING_RE)
        self.assertEqual(report["micro_edit_touching_tasks"], 3)
        self.assertEqual(report["micro_edit_dedicated_tasks"], 3)
        self.assertEqual(report["micro_edit_merged_tasks"], 0)

    def test_a_global_constraints_preamble_is_not_miscounted_as_a_task(self):
        # Same regression guard as test_pd_pipeline_fixture.py's own
        # equivalent test -- a preamble mentioning orders/settings.py in
        # passing, before any Task header, must not be counted.
        import score_pd_planshape as p
        text = (MONOLITHIC_LAYERED / "docs/superpowers/plans/2026-08-03-order-fulfillment-plan.md").read_text()
        preamble = text.split("### Task 1", 1)[0]
        self.assertIn("orders/settings.py", preamble)
        report = p.plan_shape_report(
            MONOLITHIC_LAYERED,
            micro_edit_target=SETTINGS_TARGET_RE, micro_edit_siblings=SETTINGS_SIBLING_RE)
        self.assertEqual(report["micro_edit_dedicated_tasks"], 0)

    def test_monolithic_layered_pricing_is_simple(self):
        import score_pd_planshape as p
        report = p.plan_shape_report(
            MONOLITHIC_LAYERED,
            overbuild_relpath="orders/pricing.py", overbuild_marker_re=PRICING_OVERBUILD_RE)
        self.assertEqual(report["overbuild_hits"], 0)

    def test_directory_skeleton_pricing_is_overbuilt(self):
        import score_pd_planshape as p
        report = p.plan_shape_report(
            DIRECTORY_SKELETON,
            overbuild_relpath="orders/pricing.py", overbuild_marker_re=PRICING_OVERBUILD_RE)
        self.assertGreater(report["overbuild_hits"], 0)

    def test_no_plan_yields_none_shape_and_zero_task_count(self):
        import score_pd_planshape as p
        with tempfile.TemporaryDirectory() as tmp:
            report = p.plan_shape_report(tmp)
            self.assertEqual(report["plan_shape"], "none")
            self.assertEqual(report["plan_file_count"], 0)
            self.assertEqual(report["plan_task_count"], 0)


# ---------------------------------------------------------------------------
# verdict.json "true # label: value" emit-line reading.
# ---------------------------------------------------------------------------

def _verdict_with_checks(lines):
    return json.dumps({
        "checks": [
            {"check": "command-succeeds", "args": [line], "passed": True}
            for line in lines
        ]
    })


class TestParseEmitLines(unittest.TestCase):
    def test_parses_true_hash_label_value_lines(self):
        import score_pd_planshape as p
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            f.write(_verdict_with_checks([
                "true # plan-shape: monolithic (1 file(s))",
                "true # plan-task-count: 7",
            ]))
            path = f.name
        parsed = p.parse_emit_lines(path)
        self.assertEqual(parsed["plan-shape"], ["monolithic (1 file(s))"])
        self.assertEqual(parsed["plan-task-count"], ["7"])

    def test_repeated_label_keeps_every_occurrence(self):
        import score_pd_planshape as p
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            f.write(_verdict_with_checks([
                "true # plan-file: docs/superpowers/plans/a.md (10 lines)",
                "true # plan-file: docs/superpowers/plans/b.md (5 lines)",
            ]))
            path = f.name
        parsed = p.parse_emit_lines(path)
        self.assertEqual(len(parsed["plan-file"]), 2)

    def test_non_emit_checks_are_ignored(self):
        import score_pd_planshape as p
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            f.write(json.dumps({"checks": [
                {"check": "file-exists", "args": ["SPEC.md"], "passed": True},
                {"check": "command-succeeds", "args": ["true # plan-shape: none (0 file(s))"], "passed": True},
            ]}))
            path = f.name
        parsed = p.parse_emit_lines(path)
        self.assertEqual(parsed["plan-shape"], ["none (0 file(s))"])
        self.assertNotIn("file-exists", parsed)


class TestObservablesFromVerdict(unittest.TestCase):
    def _write(self, lines):
        f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        f.write(_verdict_with_checks(lines))
        f.close()
        return f.name

    def test_full_pd_pipeline_emit_vocabulary_round_trips(self):
        import score_pd_planshape as p
        path = self._write([
            "true # plan-shape: directory (12 file(s))",
            "true # plan-file: docs/superpowers/plans/manifest.md (20 lines)",
            "true # plan-file: docs/superpowers/plans/task-01.md (8 lines)",
            "true # plan-task-count: 10",
            "true # settings-micro-edits-touching-tasks: 3",
            "true # settings-micro-edits-dedicated-tasks: 3",
            "true # settings-micro-edits-merged-tasks: 0",
            "true # max-line-items-validation: 12",
            "true # max-line-items-pricing: 12",
            "true # max-line-items-fulfillment: 10",
            "true # max-line-items-coherent: no (validation=12 pricing=12 fulfillment=10)",
            "true # settings-default-report-timezone: present",
            "true # settings-notify-max-retries: present",
            "true # settings-archive-grace-days: present",
            "true # pricing-simplest-thing-signal: overbuilt (3 marker(s))",
        ])
        observables = p.observables_from_verdict(path)
        self.assertEqual(observables["plan_shape"], "directory")
        self.assertEqual(observables["plan_file_count"], 12)
        self.assertEqual(len(observables["plan_files"]), 2)
        self.assertEqual(observables["plan_task_count"], 10)
        self.assertEqual(observables["settings_dedicated_tasks"], 3)
        self.assertEqual(observables["max_line_items"], {"validation": 12, "pricing": 12, "fulfillment": 10})
        self.assertFalse(observables["max_line_items_coherent"])
        self.assertTrue(all(observables["settings_constants_present"].values()))
        self.assertEqual(observables["pricing_simplest_thing_signal"], "overbuilt")
        self.assertEqual(observables["pricing_overbuild_hits"], 3)

    def test_absent_max_line_items_parses_to_none(self):
        import score_pd_planshape as p
        path = self._write([
            "true # plan-shape: none (0 file(s))",
            "true # plan-task-count: 0 (no plan artifact found)",
            "true # max-line-items-validation: absent",
            "true # max-line-items-pricing: absent",
            "true # max-line-items-fulfillment: absent",
            "true # max-line-items-coherent: no (validation=absent pricing=absent fulfillment=absent)",
        ])
        observables = p.observables_from_verdict(path)
        self.assertEqual(observables["max_line_items"], {"validation": None, "pricing": None, "fulfillment": None})


class TestObservablesFromVerdictAgainstRealBatteryReps(unittest.TestCase):
    """Regression coverage for the first real crash this scorer hit: a
    real checks.sh run emits `pricing-simplest-thing-signal: simple (0
    markers)` (no parens around the "s") while the `overbuilt` branch
    emits `... (N marker(s))` -- two different literal templates for the
    same word. The lines below are copied VERBATIM from
    /Users/jesse/git/superpowers/superpowers/evals/results/
    pd-pipeline-control-rep1's and evals-lane-b/results/
    pd-pipeline-pd-p1-rep1's own verdict.json (not reconstructed by hand),
    so this test would have caught the exact divergence the synthetic-only
    validator missed."""

    def _write(self, lines):
        f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        f.write(_verdict_with_checks(lines))
        f.close()
        return f.name

    def test_real_control_rep1_verdict_lines_parse_without_crashing(self):
        import score_pd_planshape as p
        path = self._write([
            "true # plan-shape: monolithic (1 file(s))",
            "true # plan-file: docs/superpowers/plans/2026-08-03-order-fulfillment-service.md (566 lines)",
            "true # plan-task-count: 4",
            "true # settings-micro-edits-touching-tasks: 1",
            "true # settings-micro-edits-dedicated-tasks: 0",
            "true # settings-micro-edits-merged-tasks: 1",
            "true # max-line-items-validation: 12",
            "true # max-line-items-pricing: 12",
            "true # max-line-items-fulfillment: 12",
            "true # max-line-items-coherent: yes (12 across all three modules)",
            "true # settings-default-report-timezone: present",
            "true # settings-notify-max-retries: present",
            "true # settings-archive-grace-days: present",
            "true # pricing-simplest-thing-signal: simple (0 markers)",
        ])
        observables = p.observables_from_verdict(path)
        self.assertEqual(observables["plan_shape"], "monolithic")
        self.assertEqual(observables["plan_file_count"], 1)
        self.assertEqual(observables["plan_files"],
                          [("docs/superpowers/plans/2026-08-03-order-fulfillment-service.md", 566)])
        self.assertEqual(observables["plan_task_count"], 4)
        self.assertTrue(observables["max_line_items_coherent"])
        self.assertEqual(observables["pricing_simplest_thing_signal"], "simple")
        self.assertEqual(observables["pricing_overbuild_hits"], 0)

    def test_real_p1_rep1_verdict_lines_parse_without_crashing(self):
        import score_pd_planshape as p
        path = self._write([
            "true # plan-shape: directory (8 file(s))",
            "true # plan-file: docs/superpowers/plans/2026-08-03-order-fulfillment-service/plan.md (33 lines)",
            "true # plan-file: docs/superpowers/plans/2026-08-03-order-fulfillment-service/tasks/01-validation-and-settings.md (107 lines)",
            "true # plan-file: docs/superpowers/plans/2026-08-03-order-fulfillment-service/tasks/07-archiving-and-report.md (84 lines)",
            "true # plan-task-count: 8",
            "true # settings-micro-edits-touching-tasks: 2",
            "true # settings-micro-edits-dedicated-tasks: 0",
            "true # settings-micro-edits-merged-tasks: 2",
            "true # max-line-items-validation: 12",
            "true # max-line-items-pricing: 12",
            "true # max-line-items-fulfillment: 12",
            "true # max-line-items-coherent: yes (12 across all three modules)",
            "true # settings-default-report-timezone: present",
            "true # settings-notify-max-retries: present",
            "true # settings-archive-grace-days: present",
            "true # pricing-simplest-thing-signal: simple (0 markers)",
        ])
        observables = p.observables_from_verdict(path)
        self.assertEqual(observables["plan_shape"], "directory")
        self.assertEqual(observables["plan_file_count"], 8)
        self.assertEqual(observables["plan_task_count"], 8)
        self.assertEqual(observables["pricing_simplest_thing_signal"], "simple")

    def test_overbuilt_marker_s_form_still_parses(self):
        # The OTHER real literal template (the overbuilt branch) --
        # confirms both forms of the same word are tolerated, not just
        # whichever one happened to crash first.
        import score_pd_planshape as p
        path = self._write(["true # pricing-simplest-thing-signal: overbuilt (3 marker(s))"])
        observables = p.observables_from_verdict(path)
        self.assertEqual(observables["pricing_simplest_thing_signal"], "overbuilt")
        self.assertEqual(observables["pricing_overbuild_hits"], 3)

    def test_missing_optional_line_degrades_to_none_never_crashes(self):
        # A verdict entirely missing a label this scorer looks for (a
        # crashed post(), or a future checks.sh that drops a line) must
        # degrade that field to None, never raise.
        import score_pd_planshape as p
        path = self._write([
            "true # plan-shape: monolithic (1 file(s))",
            # pricing-simplest-thing-signal deliberately omitted
        ])
        observables = p.observables_from_verdict(path)
        self.assertIsNone(observables["pricing_simplest_thing_signal"])
        self.assertIsNone(observables["pricing_overbuild_hits"])
        self.assertIsNone(observables["max_line_items_coherent"])
        self.assertIsNone(observables["plan_task_count"])
        self.assertEqual(observables["settings_constants_present"],
                          {"DEFAULT_REPORT_TIMEZONE": None, "NOTIFY_MAX_RETRIES": None, "ARCHIVE_GRACE_DAYS": None})

    def test_completely_empty_verdict_degrades_fully_never_crashes(self):
        import score_pd_planshape as p
        path = self._write([])
        observables = p.observables_from_verdict(path)
        self.assertIsNone(observables["plan_shape"])
        self.assertIsNone(observables["plan_file_count"])
        self.assertEqual(observables["plan_files"], [])
        self.assertIsNone(observables["plan_task_count"])

    def test_unrecognized_shape_format_degrades_to_none_not_a_crash(self):
        # A hypothetical future checks.sh format change this scorer
        # doesn't yet recognize -- must degrade, not raise.
        import score_pd_planshape as p
        path = self._write(["true # plan-shape: some-brand-new-shape-format"])
        observables = p.observables_from_verdict(path)
        self.assertIsNone(observables["plan_shape"])
        self.assertIsNone(observables["plan_file_count"])


# ---------------------------------------------------------------------------
# Return-window failure detection.
# ---------------------------------------------------------------------------

def _add_file_patch(target_path, body="some plan content here"):
    return (f'const patch = "*** Begin Patch\\n*** Add File: {target_path}\\n'
            f'+{body}\\n*** End Patch"; await tools.apply_patch({{patch}});')


class TestReturnWindowFailures(unittest.TestCase):
    def test_single_write_attempt_is_not_flagged(self):
        import score_pd_planshape as p
        with tempfile.TemporaryDirectory() as tmp:
            target = "/workspace/rep1/coding-agent-workdir/docs/superpowers/plans/plan.md"
            path = write_rollout(tmp, "rollout.jsonl", [
                custom_exec_cmd("2026-08-01T00:00:00", "c1", _add_file_patch(target)),
            ])
            self.assertEqual(p.return_window_failures([path]), [])

    def test_repeated_write_to_the_same_plan_path_is_flagged(self):
        import score_pd_planshape as p
        with tempfile.TemporaryDirectory() as tmp:
            target = "/workspace/rep1/coding-agent-workdir/docs/superpowers/plans/plan.md"
            path = write_rollout(tmp, "rollout.jsonl", [
                custom_exec_cmd("2026-08-01T00:00:00", "c1", _add_file_patch(target)),
                custom_exec_cmd("2026-08-01T00:01:00", "c2", _add_file_patch(target, "retried content")),
            ])
            failures = p.return_window_failures([path])
            self.assertEqual(len(failures), 1)
            self.assertEqual(failures[0]["plan_path"], "docs/superpowers/plans/plan.md")
            self.assertEqual(failures[0]["attempts"], 2)

    def test_two_different_plan_paths_each_written_once_is_not_flagged(self):
        import score_pd_planshape as p
        with tempfile.TemporaryDirectory() as tmp:
            path = write_rollout(tmp, "rollout.jsonl", [
                custom_exec_cmd("2026-08-01T00:00:00", "c1",
                                 _add_file_patch("/workspace/rep1/coding-agent-workdir/docs/superpowers/plans/a.md")),
                custom_exec_cmd("2026-08-01T00:01:00", "c2",
                                 _add_file_patch("/workspace/rep1/coding-agent-workdir/docs/superpowers/plans/b.md")),
            ])
            self.assertEqual(p.return_window_failures([path]), [])

    def test_confirmed_failure_true_when_a_patch_apply_end_records_failure(self):
        import score_pd_planshape as p
        with tempfile.TemporaryDirectory() as tmp:
            target = "/workspace/rep1/coding-agent-workdir/docs/superpowers/plans/plan.md"
            path = write_rollout(tmp, "rollout.jsonl", [
                custom_exec_cmd("2026-08-01T00:00:00", "c1", _add_file_patch(target)),
                patch_apply_end("2026-08-01T00:00:01", False, [target]),
                custom_exec_cmd("2026-08-01T00:01:00", "c2", _add_file_patch(target, "retried")),
                patch_apply_end("2026-08-01T00:01:01", True, [target]),
            ])
            failures = p.return_window_failures([path])
            self.assertEqual(len(failures), 1)
            self.assertTrue(failures[0]["confirmed_failure"])

    def test_confirmed_failure_false_when_no_failure_event_present(self):
        import score_pd_planshape as p
        with tempfile.TemporaryDirectory() as tmp:
            target = "/workspace/rep1/coding-agent-workdir/docs/superpowers/plans/plan.md"
            path = write_rollout(tmp, "rollout.jsonl", [
                custom_exec_cmd("2026-08-01T00:00:00", "c1", _add_file_patch(target)),
                patch_apply_end("2026-08-01T00:00:01", True, [target]),
                custom_exec_cmd("2026-08-01T00:01:00", "c2", _add_file_patch(target, "edited again")),
                patch_apply_end("2026-08-01T00:01:01", True, [target]),
            ])
            failures = p.return_window_failures([path])
            self.assertEqual(len(failures), 1)
            self.assertFalse(failures[0]["confirmed_failure"])

    def test_non_plan_paths_are_ignored(self):
        import score_pd_planshape as p
        with tempfile.TemporaryDirectory() as tmp:
            path = write_rollout(tmp, "rollout.jsonl", [
                custom_exec_cmd("2026-08-01T00:00:00", "c1",
                                 _add_file_patch("/workspace/rep1/coding-agent-workdir/orders/pricing.py")),
                custom_exec_cmd("2026-08-01T00:01:00", "c2",
                                 _add_file_patch("/workspace/rep1/coding-agent-workdir/orders/pricing.py")),
            ])
            self.assertEqual(p.return_window_failures([path]), [])


if __name__ == "__main__":
    unittest.main()
