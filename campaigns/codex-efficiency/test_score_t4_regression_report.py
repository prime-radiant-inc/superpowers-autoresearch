"""Tests for score_t4_regression_report.py's cross-harness battery
aggregator (Task 11). Synthetic --out-root RUNDIR trees only -- fake
verdict.json/trajectory.json content, no real quorum run output, no
client data. Covers: arm/scenario-class parsing from the RUNDIR basename,
run-subdir discovery (missing/ambiguous), end-to-end score_run() against a
synthetic RUNDIR, per-cell aggregation math, and the output-label/
FORCE-guard convention shared with score_e1.py/score_e4.py/etc."""
import json
import pathlib
import tempfile
import unittest

import score_t4_regression_report as rpt


def write_verdict(run_dir, coding_agent, gauntlet_status="pass", final="pass",
                   scenario="cc-ceremony-bounded", cost=1.23):
    verdict = {
        "final": final,
        "final_reason": "synthetic",
        "scenario": scenario,
        "coding_agent": coding_agent,
        "credential": "synthetic_cred",
        "gauntlet": {"status": gauntlet_status},
        "economics": {"total_est_cost_usd": cost, "partial": False},
    }
    (run_dir / "verdict.json").write_text(json.dumps(verdict))


def write_trajectory(run_dir, spec_docs=0, writing_plans=False):
    steps = [{"step_id": 1, "source": "user", "message": "hi"}]
    if writing_plans:
        steps.append({"step_id": 2, "source": "agent", "tool_calls": [
            {"tool_call_id": "c1", "function_name": "Read",
             "arguments": {"file_path": "skills/writing-plans/SKILL.md"}}]})
    for i in range(spec_docs):
        steps.append({"step_id": 3 + i, "source": "agent", "tool_calls": [
            {"tool_call_id": f"s{i}", "function_name": "Write",
             "arguments": {"file_path": f"docs/superpowers/specs/x{i}.md",
                            "content": "spec"}}]})
    steps.append({"step_id": 100, "source": "agent", "tool_calls": [
        {"tool_call_id": "code", "function_name": "Write",
         "arguments": {"file_path": "server.py", "content": "code"}}]})
    traj = {"schema_version": "ATIF-v1.7",
            "agent": {"name": "synthetic", "version": "0.0.0"}, "steps": steps}
    (run_dir / "trajectory.json").write_text(json.dumps(traj))


class TestLabelParsing(unittest.TestCase):
    def test_rundir_label_parses_scenario_and_rep(self):
        arm_scenario, rep = rpt._rundir_label(
            "/x/results/cx-eff-cc-ceremony-bounded-fix-rep3")
        self.assertEqual(arm_scenario, "cc-ceremony-bounded-fix")
        self.assertEqual(rep, 3)

    def test_rundir_label_rejects_non_matching_basename(self):
        with self.assertRaises(SystemExit):
            rpt._rundir_label("/x/results/not-a-battery-dir")

    def test_scenario_key_spike_bounded_arch(self):
        self.assertEqual(rpt._scenario_key("cc-ceremony-spike-dev"), "spike")
        self.assertEqual(rpt._scenario_key("cc-ceremony-bounded-fix"), "bounded")
        self.assertEqual(rpt._scenario_key("cc-ceremony-arch-dev"), "arch")

    def test_scenario_key_raises_on_unknown_class(self):
        with self.assertRaises(SystemExit):
            rpt._scenario_key("cc-sdd-small-dev")

    def test_arm_dev_and_fix(self):
        self.assertEqual(rpt._arm("cc-ceremony-bounded-dev", "bounded"), "dev")
        self.assertEqual(rpt._arm("cc-ceremony-arch-fix", "arch"), "fix")

    def test_arm_rejects_unknown_token(self):
        with self.assertRaises(SystemExit):
            rpt._arm("cc-ceremony-bounded-spinout", "bounded")


class TestFindRunSubdir(unittest.TestCase):
    def test_missing_run_subdir_raises(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(SystemExit):
                rpt._find_run_subdir(td)

    def test_ambiguous_run_subdirs_raises(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = pathlib.Path(td)
            for name in ("run-a", "run-b"):
                d = tdp / name
                d.mkdir()
                (d / "verdict.json").write_text("{}")
            with self.assertRaises(SystemExit):
                rpt._find_run_subdir(td)

    def test_single_run_subdir_found(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = pathlib.Path(td)
            d = tdp / "cc-ceremony-bounded-claude-opus-linux-x"
            d.mkdir()
            (d / "verdict.json").write_text("{}")
            self.assertEqual(rpt._find_run_subdir(td), str(d))


class TestScoreRunEndToEnd(unittest.TestCase):
    def test_scores_a_synthetic_rundir(self):
        with tempfile.TemporaryDirectory() as td:
            rundir = pathlib.Path(td) / "cx-eff-cc-ceremony-bounded-fix-rep2"
            rundir.mkdir()
            run_dir = rundir / "cc-ceremony-bounded-claude-opus-linux-x"
            run_dir.mkdir()
            write_verdict(run_dir, "claude")
            write_trajectory(run_dir, spec_docs=0, writing_plans=False)

            result = rpt.score_run(str(rundir))

            self.assertEqual(result["arm"], "fix")
            self.assertEqual(result["coding_agent"], "claude")
            self.assertEqual(result["scenario_class"], "bounded")
            self.assertEqual(result["rep"], 2)
            self.assertEqual(result["gauntlet_status"], "pass")
            self.assertEqual(result["total_est_cost_usd"], 1.23)
            self.assertIsNotNone(result["census"])
            self.assertEqual(result["census"]["spec_docs_written"], 0)
            self.assertFalse(result["census"]["writing_plans_invoked"])

    def test_missing_trajectory_yields_none_census(self):
        with tempfile.TemporaryDirectory() as td:
            rundir = pathlib.Path(td) / "cx-eff-cc-ceremony-arch-dev-rep1"
            rundir.mkdir()
            run_dir = rundir / "cc-ceremony-arch-gemini-x"
            run_dir.mkdir()
            write_verdict(run_dir, "gemini", gauntlet_status="investigate", final="indeterminate")

            result = rpt.score_run(str(rundir))
            self.assertIsNone(result["census"])
            self.assertEqual(result["gauntlet_status"], "investigate")


class TestSummarizeCell(unittest.TestCase):
    def _run(self, gauntlet_status, final, spec_docs, writing_plans, cost):
        return {
            "gauntlet_status": gauntlet_status, "final": final,
            "total_est_cost_usd": cost,
            "census": {
                "spec_docs_written": spec_docs, "plan_docs_written": spec_docs,
                "doc_writes_before_first_code": spec_docs * 2,
                "writing_plans_invoked": writing_plans,
                "user_turns_before_first_code": 2,
            },
        }

    def test_aggregates_pass_rate_and_means(self):
        runs = [
            self._run("pass", "pass", 1, True, 1.0),
            self._run("pass", "pass", 1, True, 2.0),
            self._run("fail", "fail", 0, False, 0.5),
        ]
        s = rpt.summarize_cell(runs)
        self.assertEqual(s["n"], 3)
        self.assertEqual(s["gauntlet_pass"], 2)
        self.assertAlmostEqual(s["gauntlet_pass_rate"], 2 / 3)
        self.assertAlmostEqual(s["mean_spec_docs_written"], 2 / 3)
        self.assertEqual(s["writing_plans_invoked_count"], 2)
        self.assertEqual(s["writing_plans_invoked_n"], 3)
        self.assertAlmostEqual(s["total_est_cost_usd"], 3.5)

    def test_handles_missing_census_gracefully(self):
        runs = [
            self._run("pass", "pass", 1, True, 1.0),
            {"gauntlet_status": "investigate", "final": "indeterminate",
             "total_est_cost_usd": 0.1, "census": None},
        ]
        s = rpt.summarize_cell(runs)
        self.assertEqual(s["n"], 2)
        self.assertEqual(s["n_scored"], 1)
        self.assertEqual(s["gauntlet_pass"], 1)


class TestOutputLabelAndForceGuard(unittest.TestCase):
    def test_rep_range_suffix_single_and_multi(self):
        self.assertEqual(rpt._rep_range_suffix([{"rep": 4}]), "rep4")
        self.assertEqual(
            rpt._rep_range_suffix([{"rep": 4}, {"rep": 5}, {"rep": 6}]), "rep4-6")

    def test_out_label_combines_arms_and_agents(self):
        runs = [
            {"arm": "dev", "coding_agent": "claude", "rep": 1},
            {"arm": "fix", "coding_agent": "gemini", "rep": 3},
        ]
        self.assertEqual(rpt._out_label(runs), "dev-fix-claude-gemini-rep1-3")

    def test_write_output_refuses_overwrite_without_force(self):
        with tempfile.TemporaryDirectory() as td:
            runs = [{"arm": "dev", "coding_agent": "claude", "rep": 1}]
            cells = {("dev", "claude", "bounded"): {"n": 1}}
            path1, wrote1 = rpt.write_output(runs, cells, td)
            self.assertTrue(wrote1)
            path2, wrote2 = rpt.write_output(runs, cells, td)
            self.assertEqual(path1, path2)
            self.assertFalse(wrote2)
            path3, wrote3 = rpt.write_output(runs, cells, td, force=True)
            self.assertTrue(wrote3)


if __name__ == "__main__":
    unittest.main()
