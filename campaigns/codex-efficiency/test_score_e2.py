"""Tests for score_e2.py's tree-walking census (Task 8, E2 FULL). Synthetic
rollout fixtures only -- fake rep-dir names, minimal hand-built
spawn_agent/sub_agent_activity/task_complete/user_message records -- no real
rollouts, no client content. Covers the parts of score_e2.py that are pure
logic and easy to get subtly wrong: transitive tree walking (recursion
depth, nonroot-spawn counting), orphan-rollout detection,
missing-task_complete detection, the root-identity assertion, and the
output-label/FORCE-guard convention shared with score_e1.py."""
import json, os, pathlib, tempfile, unittest
import score_e2 as se

REVIEW_REQUEST = ("Please do a final review of the feature branch using "
                   "your superpowers review skills before we merge.")


def _rec(ts, typ, payload):
    return json.dumps({"timestamp": ts, "type": typ, "payload": payload})


def user_message(ts, text):
    return _rec(ts, "event_msg", {"type": "user_message", "message": text})


def spawn_call(ts, call_id, task_name="reviewer"):
    return _rec(ts, "response_item", {
        "type": "function_call", "id": call_id, "name": "spawn_agent",
        "namespace": "collaboration",
        "arguments": json.dumps({"task_name": task_name, "fork_turns": "none",
                                 "model": "gpt-5.6-terra", "reasoning_effort": "high"}),
        "call_id": call_id})


def sub_agent_started(ts, event_id, thread_id):
    return _rec(ts, "event_msg", {
        "type": "sub_agent_activity", "kind": "started",
        "event_id": event_id, "agent_thread_id": thread_id})


def task_complete(ts):
    return _rec(ts, "event_msg", {
        "type": "task_complete", "turn_id": "t1",
        "last_agent_message": "done", "completed_at": 1, "duration_ms": 1})


def wait_call(ts, call_id):
    return _rec(ts, "response_item", {
        "type": "function_call", "id": call_id, "name": "wait_agent",
        "arguments": json.dumps({"timeout_ms": "10000"}), "call_id": call_id})


def write_rollout(sess_dir, ts_compact, uuid, lines):
    path = sess_dir / f"rollout-{ts_compact}-{uuid}.jsonl"
    path.write_text("\n".join(lines) + "\n")
    return path


def make_run(base, arm_scenario, rep, build_fn):
    """Builds a synthetic run dir matching run-quorum.sh's --out-root naming
    convention (<base>/cx-eff-<arm_scenario>-rep<rep>/leaf/home/.codex/
    sessions/**/*.jsonl) and hands `build_fn` the session dir to populate."""
    rundir = base / f"cx-eff-{arm_scenario}-rep{rep}" / "leaf"
    sess_dir = rundir / "home" / ".codex" / "sessions" / "2026" / "07" / "29"
    sess_dir.mkdir(parents=True)
    build_fn(sess_dir)
    return rundir


class TestRootIdentity(unittest.TestCase):
    def test_root_matching_review_request_passes(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-29T05-00-00", "root0000", [
                user_message("2026-07-29T05:00:00.000Z", REVIEW_REQUEST),
                task_complete("2026-07-29T05:01:00.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-branch-review-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertTrue(run["root_matches_review_request"])
            self.assertEqual(run["total_sessions"], 1)
            self.assertEqual(run["max_depth"], 0)

    def test_root_not_matching_review_request_raises(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-29T05-00-00", "root0000", [
                user_message("2026-07-29T05:00:00.000Z", "unrelated instruction"),
                task_complete("2026-07-29T05:01:00.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-branch-review-dev", 1, build)
            with self.assertRaises(SystemExit):
                se.score_run(str(rundir))


class TestTreeWalk(unittest.TestCase):
    def test_root_with_two_isolated_children_no_recursion(self):
        """Root dispatches 2 children; neither child spawns further. This
        is the "healthy" shape the E2 treatment target wants: descendants
        exist (the root's own expected dispatch(es)) but nothing recurses
        past depth 1."""
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-29T05-00-00", "root0000", [
                user_message("2026-07-29T05:00:00.000Z", REVIEW_REQUEST),
                spawn_call("2026-07-29T05:00:01.000Z", "call_A", "reviewer_a"),
                sub_agent_started("2026-07-29T05:00:02.000Z", "call_A", "childaaaa"),
                spawn_call("2026-07-29T05:00:03.000Z", "call_B", "reviewer_b"),
                sub_agent_started("2026-07-29T05:00:04.000Z", "call_B", "childbbbb"),
                task_complete("2026-07-29T05:05:00.000Z"),
            ])
            write_rollout(sess_dir, "2026-07-29T05-00-05", "childaaaa", [
                task_complete("2026-07-29T05:02:00.000Z"),
            ])
            write_rollout(sess_dir, "2026-07-29T05-00-06", "childbbbb", [
                task_complete("2026-07-29T05:02:00.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-branch-review-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["total_sessions"], 3)
            self.assertEqual(run["max_depth"], 1)
            self.assertEqual(run["spawns_by_nonroot"], 0)
            self.assertEqual(run["orphan_rollouts"], [])
            self.assertEqual(run["missing_task_complete"], [])

    def test_recursive_reviewer_reaches_depth_two(self):
        """Root dispatches 1 reviewer; that reviewer itself spawns a
        grandchild -- the recursion pathology E2 is built to detect.
        spawns_by_nonroot must count the reviewer's own spawn call."""
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-29T05-00-00", "root0000", [
                user_message("2026-07-29T05:00:00.000Z", REVIEW_REQUEST),
                spawn_call("2026-07-29T05:00:01.000Z", "call_A", "final_reviewer"),
                sub_agent_started("2026-07-29T05:00:02.000Z", "call_A", "reviewerc"),
                task_complete("2026-07-29T05:10:00.000Z"),
            ])
            write_rollout(sess_dir, "2026-07-29T05-00-05", "reviewerc", [
                spawn_call("2026-07-29T05:01:00.000Z", "call_C", "sub_reviewer"),
                sub_agent_started("2026-07-29T05:01:01.000Z", "call_C", "grandchild"),
                task_complete("2026-07-29T05:03:00.000Z"),
            ])
            write_rollout(sess_dir, "2026-07-29T05-00-06", "grandchild", [
                task_complete("2026-07-29T05:02:00.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-branch-review-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["total_sessions"], 3)
            self.assertEqual(run["max_depth"], 2)
            self.assertEqual(run["spawns_by_nonroot"], 1)

    def test_unresolved_spawn_and_unrelated_rollout_are_orphans(self):
        """A rollout file that no tree spawn links to (a leftover/unrelated
        session file) must be reported as an orphan, not silently folded
        into the tree or silently dropped from the report."""
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-29T05-00-00", "root0000", [
                user_message("2026-07-29T05:00:00.000Z", REVIEW_REQUEST),
                task_complete("2026-07-29T05:01:00.000Z"),
            ])
            write_rollout(sess_dir, "2026-07-29T05-00-05", "strayxxxx", [
                task_complete("2026-07-29T05:02:00.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-branch-review-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["total_sessions"], 1)
            self.assertIn("rollout-2026-07-29T05-00-05-strayxxxx.jsonl", run["orphan_rollouts"])

    def test_missing_task_complete_flagged(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-29T05-00-00", "root0000", [
                user_message("2026-07-29T05:00:00.000Z", REVIEW_REQUEST),
                spawn_call("2026-07-29T05:00:01.000Z", "call_A", "reviewer_a"),
                sub_agent_started("2026-07-29T05:00:02.000Z", "call_A", "childaaaa"),
                task_complete("2026-07-29T05:05:00.000Z"),
            ])
            # child never emits task_complete -- e.g. it timed out / crashed.
            write_rollout(sess_dir, "2026-07-29T05-00-05", "childaaaa", [
                spawn_call("2026-07-29T05:00:06.000Z", "call_X", "noop"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-branch-review-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["missing_task_complete"],
                              ["rollout-2026-07-29T05-00-05-childaaaa.jsonl"])
            self.assertEqual(run["n_missing_task_complete"], 1)

    def test_wait_calls_summed_across_tree(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-29T05-00-00", "root0000", [
                user_message("2026-07-29T05:00:00.000Z", REVIEW_REQUEST),
                spawn_call("2026-07-29T05:00:01.000Z", "call_A", "reviewer_a"),
                sub_agent_started("2026-07-29T05:00:02.000Z", "call_A", "childaaaa"),
                wait_call("2026-07-29T05:00:03.000Z", "wait_1"),
                wait_call("2026-07-29T05:00:04.000Z", "wait_2"),
                task_complete("2026-07-29T05:05:00.000Z"),
            ])
            write_rollout(sess_dir, "2026-07-29T05-00-05", "childaaaa", [
                wait_call("2026-07-29T05:01:00.000Z", "wait_3"),
                task_complete("2026-07-29T05:02:00.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-branch-review-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["root_wait_calls"], 2)
            self.assertEqual(run["total_wait_calls"], 3)


class TestOutputLabelAndForceGuard(unittest.TestCase):
    """Same convention as score_e1.py's TestOutLabel/TestWriteOutputCollision
    -- verifying score_e2.py's copy of that logic wasn't silently altered."""

    def _run(self, base, arm_scenario, rep):
        def build(sess_dir):
            write_rollout(sess_dir, f"2026-07-29T05-00-0{rep}", f"root{rep:04d}", [
                user_message(f"2026-07-29T05:00:0{rep}.000Z", REVIEW_REQUEST),
                task_complete(f"2026-07-29T05:01:0{rep}.000Z"),
            ])
        rundir = make_run(base, arm_scenario, rep, build)
        return se.score_run(str(rundir))

    def test_label_includes_rep_range(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            runs = [self._run(base, "cx-branch-review-dev", r) for r in (1, 2, 3, 4)]
            self.assertEqual(se._out_label(runs), "cx-branch-review-dev-rep1-4")

    def test_refuses_overwrite_without_force_then_force_allows(self):
        with tempfile.TemporaryDirectory() as tmp:
            battery = pathlib.Path(tmp) / "battery"
            out_dir = pathlib.Path(tmp) / "out"
            runs = [self._run(battery, "cx-branch-review-dev", r) for r in (1, 2)]

            out_path, wrote = se.write_output(runs, str(out_dir))
            self.assertTrue(wrote)
            out_path2, wrote2 = se.write_output(runs, str(out_dir))
            self.assertFalse(wrote2)
            self.assertEqual(out_path, out_path2)

            out_path3, wrote3 = se.write_output(runs, str(out_dir), force=True)
            self.assertTrue(wrote3)


if __name__ == "__main__":
    unittest.main()
