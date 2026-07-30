"""Tests for score_e4.py's proportional-ceremony census (Task 11). Synthetic
rollout fixtures only -- fake rep-dir names, minimal hand-built
user_message/spawn_agent/sub_agent_activity/patch_apply_end records -- no
real rollouts, no client content. Covers: is_doc_path classification,
first-non-doc-patch selection (tree-wide, oldest-first, success-only),
root-only user-turn counting, tree-wide tool-call counting, the
no-non-doc-patch (T is None) edge case, the root-identity assertion per
scenario class, class summarization/discrimination-gate math, and the
output-label/FORCE-guard convention shared with score_e1.py/score_e2.py."""
import json, pathlib, tempfile, unittest
import score_e4 as se

SPIKE_TASK = ("Can we detect whether the service's port is already in use "
              "before binding? Not sure it's possible portably -- find out, "
              "quick and dirty is fine.")
BOUNDED_TASK = ("Add a --quiet flag that suppresses request logging. The "
                 "logging call sites are in server.py.")
ARCH_TASK = ("We need to split the service into a reusable library + thin "
              "CLI so another team can embed it.")


def _rec(ts, typ, payload):
    return json.dumps({"timestamp": ts, "type": typ, "payload": payload})


def user_message(ts, text):
    return _rec(ts, "event_msg", {"type": "user_message", "message": text})


def tool_call(ts, call_id, name="exec_command"):
    return _rec(ts, "response_item", {
        "type": "function_call", "id": call_id, "name": name,
        "arguments": json.dumps({"cmd": "ls"}), "call_id": call_id})


def spawn_call(ts, call_id, task_name="implementer"):
    return _rec(ts, "response_item", {
        "type": "function_call", "id": call_id, "name": "spawn_agent",
        "namespace": "collaboration",
        "arguments": json.dumps({"task_name": task_name, "fork_turns": "none",
                                 "model": "gpt-5.6-terra"}),
        "call_id": call_id})


def sub_agent_started(ts, event_id, thread_id):
    return _rec(ts, "event_msg", {
        "type": "sub_agent_activity", "kind": "started",
        "event_id": event_id, "agent_thread_id": thread_id})


def patch_apply(ts, call_id, success, changes):
    return _rec(ts, "event_msg", {
        "type": "patch_apply_end", "call_id": call_id, "turn_id": "t1",
        "success": success, "changes": changes})


def write_rollout(sess_dir, ts_compact, uuid, lines):
    path = sess_dir / f"rollout-{ts_compact}-{uuid}.jsonl"
    path.write_text("\n".join(lines) + "\n")
    return path


def make_run(base, arm_scenario, rep, build_fn):
    """Identical convention to score_e2.py's test helper of the same name."""
    rundir = base / f"cx-eff-{arm_scenario}-rep{rep}" / "leaf"
    sess_dir = rundir / "home" / ".codex" / "sessions" / "2026" / "07" / "29"
    sess_dir.mkdir(parents=True)
    build_fn(sess_dir)
    return rundir


class TestIsDocPath(unittest.TestCase):
    def test_md_file_is_doc(self):
        self.assertTrue(se.is_doc_path("/work/repo/README.md"))
        self.assertTrue(se.is_doc_path("/work/repo/.superpowers/sdd/plan/task-1-report.MD"))

    def test_docs_directory_component_is_doc(self):
        self.assertTrue(se.is_doc_path("/work/repo/docs/USAGE.txt"))
        self.assertTrue(se.is_doc_path("/work/repo/docs/nested/deep.py"))

    def test_docs_as_filename_not_directory_is_not_doc(self):
        # "docs" the FILE (no extension, not a directory component) is not
        # a doc path -- only a "docs" *directory segment* counts.
        self.assertFalse(se.is_doc_path("/work/repo/docs"))

    def test_python_file_outside_docs_is_not_doc(self):
        self.assertFalse(se.is_doc_path("/work/repo/server.py"))
        self.assertFalse(se.is_doc_path("/work/repo/strutils/core.py"))


class TestRootIdentity(unittest.TestCase):
    def test_root_matching_spike_task_passes(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-29T05-00-00", "root0000", [
                user_message("2026-07-29T05:00:00.000Z", SPIKE_TASK),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-ceremony-spike-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertTrue(run["root_matches_task"])
            self.assertEqual(run["scenario_class"], "spike")

    def test_root_not_matching_task_raises(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-29T05-00-00", "root0000", [
                user_message("2026-07-29T05:00:00.000Z", "unrelated instruction"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-ceremony-spike-dev", 1, build)
            with self.assertRaises(SystemExit):
                se.score_run(str(rundir))

    def test_unknown_scenario_class_raises(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-29T05-00-00", "root0000", [
                user_message("2026-07-29T05:00:00.000Z", SPIKE_TASK),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-something-else-dev", 1, build)
            with self.assertRaises(SystemExit):
                se.score_run(str(rundir))


class TestCensus(unittest.TestCase):
    def test_root_only_patch_before_docs_and_code(self):
        """A doc patch (plan.md) lands first, then a real code patch. T
        must land at the code patch, not the doc patch; docs-written
        counts only the doc patch (before T); tool calls/user turns count
        only what happened strictly before T."""
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-29T05-00-00", "root0000", [
                user_message("2026-07-29T05:00:00.000Z", BOUNDED_TASK),
                tool_call("2026-07-29T05:00:01.000Z", "call_1"),
                patch_apply("2026-07-29T05:00:02.000Z", "p1", True,
                            {"/work/repo/.superpowers/sdd/plan/task-1-brief.md":
                                 {"type": "add", "content": "brief"}}),
                tool_call("2026-07-29T05:00:03.000Z", "call_2"),
                patch_apply("2026-07-29T05:00:04.000Z", "p2", True,
                            {"/work/repo/server.py": {"type": "update"}}),
                tool_call("2026-07-29T05:00:05.000Z", "call_3"),  # after T -- not counted
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-ceremony-bounded-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertFalse(run["no_non_doc_patch"])
            self.assertEqual(run["first_non_doc_patch_timestamp"], "2026-07-29T05:00:04.000Z")
            self.assertEqual(run["docs_written_before_first_non_doc_patch"], 1)
            self.assertEqual(run["doc_paths_written_before_first_non_doc_patch"],
                              ["/work/repo/.superpowers/sdd/plan/task-1-brief.md"])
            # tool calls strictly before T: call_1 (05:00:01) and call_2
            # (05:00:03); call_3 (05:00:05) is AFTER T (05:00:04) and must
            # not be counted.
            self.assertEqual(run["tool_calls_before_first_non_doc_patch"], 2)
            self.assertEqual(run["user_turns_before_first_non_doc_patch"], 1)
            self.assertAlmostEqual(run["wall_clock_seconds_to_first_non_doc_patch"], 4.0)

    def test_failed_patch_is_never_the_first_non_doc_patch(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-29T05-00-00", "root0000", [
                user_message("2026-07-29T05:00:00.000Z", SPIKE_TASK),
                patch_apply("2026-07-29T05:00:01.000Z", "p1", False,
                            {"/work/repo/server.py": {"type": "update"}}),
                patch_apply("2026-07-29T05:00:02.000Z", "p2", True,
                            {"/work/repo/server.py": {"type": "update"}}),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-ceremony-spike-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["first_non_doc_patch_timestamp"], "2026-07-29T05:00:02.000Z")

    def test_doc_only_patches_never_set_t_and_no_non_doc_patch_is_true(self):
        """A spike that only ever touches docs/*.md (or never patches at
        all) must report no_non_doc_patch=True and every T-gated field as
        None, not a stretched/imputed value. docs_written falls back to
        counting the WHOLE session (no T cutoff) in this case."""
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-29T05-00-00", "root0000", [
                user_message("2026-07-29T05:00:00.000Z", SPIKE_TASK),
                tool_call("2026-07-29T05:00:01.000Z", "call_1"),
                patch_apply("2026-07-29T05:00:02.000Z", "p1", True,
                            {"/work/repo/docs/FINDINGS.md": {"type": "add"}}),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-ceremony-spike-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertTrue(run["no_non_doc_patch"])
            self.assertIsNone(run["first_non_doc_patch_timestamp"])
            self.assertIsNone(run["user_turns_before_first_non_doc_patch"])
            self.assertIsNone(run["tool_calls_before_first_non_doc_patch"])
            self.assertIsNone(run["wall_clock_seconds_to_first_non_doc_patch"])
            self.assertEqual(run["docs_written_before_first_non_doc_patch"], 1)

    def test_first_non_doc_patch_can_come_from_a_spawned_child(self):
        """The controller only plans (doc patches); an implementer CHILD
        makes the real code change. T must resolve from the child's
        rollout, not just the root's own patches -- the whole point of
        walking the tree instead of scoring the root alone."""
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-29T05-00-00", "root0000", [
                user_message("2026-07-29T05:00:00.000Z", ARCH_TASK),
                patch_apply("2026-07-29T05:00:01.000Z", "p1", True,
                            {"/work/repo/docs/DESIGN.md": {"type": "add"}}),
                spawn_call("2026-07-29T05:00:02.000Z", "call_A", "implementer_1"),
                sub_agent_started("2026-07-29T05:00:03.000Z", "call_A", "childaaaa"),
            ])
            write_rollout(sess_dir, "2026-07-29T05-00-05", "childaaaa", [
                tool_call("2026-07-29T05:01:00.000Z", "call_child_1"),
                patch_apply("2026-07-29T05:01:01.000Z", "cp1", True,
                            {"/work/repo/lib/service.py": {"type": "add"}}),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-ceremony-arch-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertFalse(run["no_non_doc_patch"])
            self.assertEqual(run["first_non_doc_patch_timestamp"], "2026-07-29T05:01:01.000Z")
            self.assertEqual(run["docs_written_before_first_non_doc_patch"], 1)
            # tree-wide tool calls before T: the root's own spawn_agent
            # call (a function_call, in TOOL_CALL_TYPES) plus the child's
            # exec call -- both count even though they span two rollouts.
            self.assertEqual(run["tool_calls_before_first_non_doc_patch"], 2)

    def test_user_turns_counts_root_only_not_child_dispatch_message(self):
        """A spawned child's own initial "user_message" (its dispatch
        task) must NOT inflate the human-turn count -- only the root's
        own user_message events count."""
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-29T05-00-00", "root0000", [
                user_message("2026-07-29T05:00:00.000Z", ARCH_TASK),
                spawn_call("2026-07-29T05:00:01.000Z", "call_A", "implementer_1"),
                sub_agent_started("2026-07-29T05:00:02.000Z", "call_A", "childaaaa"),
            ])
            write_rollout(sess_dir, "2026-07-29T05-00-05", "childaaaa", [
                user_message("2026-07-29T05:00:06.000Z", "your dispatch task: ..."),
                patch_apply("2026-07-29T05:00:07.000Z", "cp1", True,
                            {"/work/repo/lib/service.py": {"type": "add"}}),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-ceremony-arch-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["user_turns_before_first_non_doc_patch"], 1)

    def test_orphan_rollout_reported(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-29T05-00-00", "root0000", [
                user_message("2026-07-29T05:00:00.000Z", SPIKE_TASK),
            ])
            write_rollout(sess_dir, "2026-07-29T05-00-05", "strayxxxx", [
                user_message("2026-07-29T05:00:05.000Z", "unrelated"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-ceremony-spike-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertIn("rollout-2026-07-29T05-00-05-strayxxxx.jsonl", run["orphan_rollouts"])


class TestClassSummaryAndGate(unittest.TestCase):
    def _run(self, tool_calls, no_patch=False):
        return {
            "no_non_doc_patch": no_patch,
            "user_turns_before_first_non_doc_patch": None if no_patch else 1,
            "docs_written_before_first_non_doc_patch": 1,
            "tool_calls_before_first_non_doc_patch": None if no_patch else tool_calls,
            "wall_clock_seconds_to_first_non_doc_patch": None if no_patch else 30.0,
        }

    def test_summarize_class_means_ignore_none(self):
        runs = [self._run(10), self._run(20), self._run(0, no_patch=True)]
        s = se.summarize_class(runs)
        self.assertEqual(s["n"], 3)
        self.assertEqual(s["n_no_non_doc_patch"], 1)
        self.assertEqual(s["mean_tool_calls"], 15.0)

    def test_gate_within_25pct_confirms_pathology(self):
        spike = se.summarize_class([self._run(38), self._run(40), self._run(42)])
        arch = se.summarize_class([self._run(40), self._run(40), self._run(40)])
        gate = se.discrimination_gate(spike, arch)
        self.assertTrue(gate["within_25pct"])
        self.assertIn("CONFIRMED", gate["verdict"])

    def test_gate_outside_25pct_is_inconclusive_by_zero(self):
        spike = se.summarize_class([self._run(5), self._run(5), self._run(5)])
        arch = se.summarize_class([self._run(40), self._run(40), self._run(40)])
        gate = se.discrimination_gate(spike, arch)
        self.assertFalse(gate["within_25pct"])
        self.assertIn("inconclusive-by-zero", gate["verdict"])

    def test_gate_handles_all_reps_no_patch(self):
        spike = se.summarize_class([self._run(0, no_patch=True)] * 3)
        arch = se.summarize_class([self._run(40), self._run(40), self._run(40)])
        gate = se.discrimination_gate(spike, arch)
        self.assertIsNone(gate["ratio"])
        self.assertIn("inconclusive-by-zero", gate["verdict"])


class TestOutputLabelAndForceGuard(unittest.TestCase):
    def _run(self, base, arm_scenario, rep, task_text):
        def build(sess_dir):
            write_rollout(sess_dir, f"2026-07-29T05-00-0{rep}", f"root{rep:04d}", [
                user_message(f"2026-07-29T05:00:0{rep}.000Z", task_text),
            ])
        rundir = make_run(base, arm_scenario, rep, build)
        return se.score_run(str(rundir))

    def test_label_includes_rep_range(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            runs = [self._run(base, "cx-ceremony-spike-dev", r, SPIKE_TASK) for r in (1, 2, 3)]
            self.assertEqual(se._out_label(runs), "cx-ceremony-spike-dev-rep1-3")

    def test_refuses_overwrite_without_force_then_force_allows(self):
        with tempfile.TemporaryDirectory() as tmp:
            battery = pathlib.Path(tmp) / "battery"
            out_dir = pathlib.Path(tmp) / "out"
            runs = [self._run(battery, "cx-ceremony-spike-dev", r, SPIKE_TASK) for r in (1, 2)]

            out_path, wrote = se.write_output(runs, {}, None, str(out_dir))
            self.assertTrue(wrote)
            out_path2, wrote2 = se.write_output(runs, {}, None, str(out_dir))
            self.assertFalse(wrote2)
            self.assertEqual(out_path, out_path2)

            out_path3, wrote3 = se.write_output(runs, {}, None, str(out_dir), force=True)
            self.assertTrue(wrote3)


if __name__ == "__main__":
    unittest.main()
