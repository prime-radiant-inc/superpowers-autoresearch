"""Tests for score_e6.py's compaction-recovery census (Task 9, E6). Synthetic
rollout fixtures only -- fake rep-dir names, minimal hand-built
spawn_agent/exec_command/context_compacted/sub_agent_activity/task_complete
records -- no real rollouts, no client content. Covers score_e6.py's own
logic (compaction-boundary partitioning of skill re-reads and spawn
hygiene, depth-2-spawn-by-spawner-role census, same-task duplicate-review
detection, task_family grouping) -- the tree walk itself is score_e2.py's
already-tested build_tree(), reused not reimplemented."""
import json, pathlib, tempfile, unittest
import score_e6 as se


def _rec(ts, typ, payload):
    return json.dumps({"timestamp": ts, "type": typ, "payload": payload})


def user_message(ts, text="Please execute the plan in plan.md using your subagent-driven-development skill."):
    return _rec(ts, "event_msg", {"type": "user_message", "message": text})


def spawn_call(ts, call_id, task_name, fork_turns="none", model="gpt-5.6-terra"):
    args = {"task_name": task_name, "fork_turns": fork_turns, "reasoning_effort": "high"}
    if model is not None:
        args["model"] = model
    return _rec(ts, "response_item", {
        "type": "function_call", "id": call_id, "name": "spawn_agent",
        "namespace": "collaboration", "arguments": json.dumps(args),
        "call_id": call_id})


def sub_agent_started(ts, event_id, thread_id):
    return _rec(ts, "event_msg", {
        "type": "sub_agent_activity", "kind": "started",
        "event_id": event_id, "agent_thread_id": thread_id})


def task_complete(ts):
    return _rec(ts, "event_msg", {
        "type": "task_complete", "turn_id": "t1",
        "last_agent_message": "done", "completed_at": 1, "duration_ms": 1})


def skill_read(ts, call_id, skill_path):
    return _rec(ts, "response_item", {
        "type": "function_call", "id": call_id, "name": "exec_command",
        "arguments": json.dumps({"cmd": f"cat {skill_path}"}), "call_id": call_id})


def compaction_marker(ts):
    return _rec(ts, "event_msg", {"type": "context_compacted"})


def write_rollout(sess_dir, ts_compact, uuid, lines):
    path = sess_dir / f"rollout-{ts_compact}-{uuid}.jsonl"
    path.write_text("\n".join(lines) + "\n")
    return path


def make_run(base, arm_scenario, rep, build_fn):
    rundir = base / f"cx-eff-{arm_scenario}-rep{rep}" / "leaf"
    sess_dir = rundir / "home" / ".codex" / "sessions" / "2026" / "07" / "30"
    sess_dir.mkdir(parents=True)
    build_fn(sess_dir)
    return rundir


SDD = "skills/subagent-driven-development/SKILL.md"
WP = "skills/writing-plans/SKILL.md"


class TestSkillRereadPartition(unittest.TestCase):
    def test_reread_only_the_path_read_on_both_sides(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                skill_read("2026-07-30T05:00:01.000Z", "call_r1", SDD),
                skill_read("2026-07-30T05:00:02.000Z", "call_r2", WP),
                compaction_marker("2026-07-30T05:00:03.000Z"),
                skill_read("2026-07-30T05:00:04.000Z", "call_r3", SDD),
                task_complete("2026-07-30T05:01:00.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-compaction-dev", 1, build)
            run = se.score_run(str(rundir))
            root = run["sessions"][0]
            self.assertTrue(root["is_root"])
            self.assertEqual(root["n_compactions"], 1)
            self.assertEqual(root["re_read_skill_paths"], [SDD])

    def test_no_reread_when_only_read_once(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                skill_read("2026-07-30T05:00:01.000Z", "call_r1", SDD),
                compaction_marker("2026-07-30T05:00:03.000Z"),
                skill_read("2026-07-30T05:00:04.000Z", "call_r2", WP),
                task_complete("2026-07-30T05:01:00.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-compaction-dev", 1, build)
            run = se.score_run(str(rundir))
            root = run["sessions"][0]
            self.assertEqual(root["re_read_skill_paths"], [])

    def test_no_compaction_means_no_partition_data(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                skill_read("2026-07-30T05:00:01.000Z", "call_r1", SDD),
                skill_read("2026-07-30T05:00:02.000Z", "call_r2", SDD),
                task_complete("2026-07-30T05:01:00.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-compaction-dev", 1, build)
            run = se.score_run(str(rundir))
            root = run["sessions"][0]
            self.assertEqual(root["n_compactions"], 0)
            self.assertFalse(root["has_compaction"])
            self.assertEqual(root["re_read_skill_paths"], [])
            self.assertEqual(root["pre_spawns"], [])
            self.assertEqual(root["post_spawns"], [])


class TestSpawnHygienePartition(unittest.TestCase):
    def test_pre_and_post_spawns_split_at_first_compaction_timestamp(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                spawn_call("2026-07-30T05:00:01.000Z", "call_A", "task1_implementer",
                          fork_turns="none", model="gpt-5.6-terra"),
                sub_agent_started("2026-07-30T05:00:02.000Z", "call_A", "impl0001"),
                compaction_marker("2026-07-30T05:00:10.000Z"),
                spawn_call("2026-07-30T05:00:11.000Z", "call_B", "task2_implementer",
                          fork_turns="all", model=None),
                sub_agent_started("2026-07-30T05:00:12.000Z", "call_B", "impl0002"),
                task_complete("2026-07-30T05:01:00.000Z"),
            ])
            write_rollout(sess_dir, "2026-07-30T05-00-05", "impl0001", [
                task_complete("2026-07-30T05:00:30.000Z")])
            write_rollout(sess_dir, "2026-07-30T05-00-15", "impl0002", [
                task_complete("2026-07-30T05:00:40.000Z")])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-compaction-dev", 1, build)
            run = se.score_run(str(rundir))
            root = run["sessions"][0]
            self.assertTrue(root["has_compaction"])
            self.assertEqual(len(root["pre_spawns"]), 1)
            self.assertEqual(len(root["post_spawns"]), 1)
            self.assertEqual(root["pre_spawns"][0]["fork_turns"], "none")
            self.assertEqual(root["pre_spawns"][0]["model"], "gpt-5.6-terra")
            self.assertEqual(root["post_spawns"][0]["fork_turns"], "all")
            self.assertEqual(root["post_spawns"][0]["model"], "(omitted)")

            hygiene = run["spawn_hygiene"]
            self.assertEqual(hygiene["pre"]["n"], 1)
            self.assertEqual(hygiene["pre"]["pct_isolated"], 100.0)
            self.assertEqual(hygiene["pre"]["pct_explicit_model"], 100.0)
            self.assertEqual(hygiene["post"]["n"], 1)
            self.assertEqual(hygiene["post"]["pct_isolated"], 0.0)
            self.assertEqual(hygiene["post"]["pct_explicit_model"], 0.0)


class TestDepth2ByRoleAndDuplicateReview(unittest.TestCase):
    def _build_implementer_spawned_reviewer_plus_controller_duplicate(self, sess_dir):
        """The 4-occurrence pattern (Amendment 3): root dispatches
        task1_implementer (depth 1); that implementer itself spawns
        task1_reviewer at depth 2 (worker-initiated review); root ALSO
        separately dispatches its own task1_reviewer at depth 1
        (controller-initiated duplicate of the SAME task family)."""
        write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
            user_message("2026-07-30T05:00:00.000Z"),
            spawn_call("2026-07-30T05:00:01.000Z", "call_A", "task1_implementer"),
            sub_agent_started("2026-07-30T05:00:02.000Z", "call_A", "impl0001"),
            spawn_call("2026-07-30T05:00:20.000Z", "call_C", "task1_reviewer"),
            sub_agent_started("2026-07-30T05:00:21.000Z", "call_C", "ctlrev01"),
            task_complete("2026-07-30T05:01:00.000Z"),
        ])
        write_rollout(sess_dir, "2026-07-30T05-00-05", "impl0001", [
            spawn_call("2026-07-30T05:00:06.000Z", "call_B", "task1_reviewer"),
            sub_agent_started("2026-07-30T05:00:07.000Z", "call_B", "wrkrev001"),
            task_complete("2026-07-30T05:00:30.000Z"),
        ])
        write_rollout(sess_dir, "2026-07-30T05-00-08", "wrkrev001", [
            task_complete("2026-07-30T05:00:15.000Z")])
        write_rollout(sess_dir, "2026-07-30T05-00-22", "ctlrev01", [
            task_complete("2026-07-30T05:00:40.000Z")])

    def test_depth2_spawn_attributed_to_implementer_spawner_role(self):
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-compaction-dev", 1,
                              self._build_implementer_spawned_reviewer_plus_controller_duplicate)
            run = se.score_run(str(rundir))
            self.assertEqual(run["depth2_by_spawner_role"], {"implementer": 1})
            self.assertEqual(len(run["depth2_details"]), 1)
            d = run["depth2_details"][0]
            self.assertEqual(d["spawner_role"], "implementer")
            self.assertEqual(d["child_task_name"], "task1_reviewer")

    def test_same_task_duplicate_review_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-compaction-dev", 1,
                              self._build_implementer_spawned_reviewer_plus_controller_duplicate)
            run = se.score_run(str(rundir))
            fams = run["duplicate_review_families"]
            self.assertEqual(len(fams), 1)
            self.assertEqual(fams[0]["family"], "task1")
            self.assertEqual(fams[0]["implementer_rollout"],
                             "rollout-2026-07-30T05-00-05-impl0001.jsonl")

    def test_no_duplicate_when_only_worker_review_exists(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                spawn_call("2026-07-30T05:00:01.000Z", "call_A", "task1_implementer"),
                sub_agent_started("2026-07-30T05:00:02.000Z", "call_A", "impl0001"),
                task_complete("2026-07-30T05:01:00.000Z"),
            ])
            write_rollout(sess_dir, "2026-07-30T05-00-05", "impl0001", [
                spawn_call("2026-07-30T05:00:06.000Z", "call_B", "task1_reviewer"),
                sub_agent_started("2026-07-30T05:00:07.000Z", "call_B", "wrkrev001"),
                task_complete("2026-07-30T05:00:30.000Z"),
            ])
            write_rollout(sess_dir, "2026-07-30T05-00-08", "wrkrev001", [
                task_complete("2026-07-30T05:00:15.000Z")])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-compaction-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["duplicate_review_families"], [])
            self.assertEqual(run["depth2_by_spawner_role"], {"implementer": 1})


class TestTaskFamily(unittest.TestCase):
    def test_strips_known_role_suffixes(self):
        self.assertEqual(se.task_family("task1_implementer"), "task1")
        self.assertEqual(se.task_family("task1_reviewer"), "task1")
        self.assertEqual(se.task_family("final_fix_reviewer"), "final")
        self.assertEqual(se.task_family("final_fixer"), "final")
        self.assertEqual(se.task_family("final_rereviewer"), "final")
        self.assertEqual(se.task_family("final_reviewer"), "final")

    def test_task_n_prefix_matches_regardless_of_role_wording(self):
        """Real dev-battery discovery (cx-eff-cx-compaction-dev-rep1): the
        controller's OWN duplicate review of task1 was named
        "task1_controller_review" -- a suffix the original
        implementer/reviewer/fixer alternation didn't cover, causing a
        real duplicate-review match to go undetected until this was
        caught by manual verification against the real rollout. The
        task{N}-prefix rule below is intentionally broader than any fixed
        role-word list."""
        self.assertEqual(se.task_family("task1_controller_review"), "task1")
        self.assertEqual(se.task_family("task2_final_branch_review"), "task2")
        self.assertEqual(se.task_family("task_nn_owner"), "task12")

    def test_final_prefix_matches_regardless_of_role_wording(self):
        self.assertEqual(se.task_family("final_branch_reviewer"), "final")
        self.assertEqual(se.task_family("final_fix_implementer"), "final")
        self.assertEqual(se.task_family("final_fix_rereviewer"), "final")

    def test_fallback_suffix_stripping_for_non_task_final_names(self):
        """Names that don't start with task<N>/final still go through the
        original suffix-stripping fallback."""
        self.assertEqual(se.task_family("widget_implementer"), "widget")
        self.assertEqual(se.task_family("widget_reviewer"), "widget")

    def test_omitted_or_none_task_name_returns_none(self):
        self.assertIsNone(se.task_family(None))
        import rollout_parser as rp
        self.assertIsNone(se.task_family(rp.OMIT))


class TestClassifyRoleByTaskName(unittest.TestCase):
    def test_review_substring_wins_reviewer(self):
        self.assertEqual(se.classify_role_by_task_name("task1_reviewer"), "reviewer")
        self.assertEqual(se.classify_role_by_task_name("rereview_widget"), "reviewer")

    def test_no_review_substring_is_implementer(self):
        self.assertEqual(se.classify_role_by_task_name("task1_implementer"), "implementer")

    def test_missing_task_name_is_unclassified(self):
        import rollout_parser as rp
        self.assertEqual(se.classify_role_by_task_name(None), "unclassified")
        self.assertEqual(se.classify_role_by_task_name(rp.OMIT), "unclassified")


class TestControllerGrowthAndOutputConvention(unittest.TestCase):
    def test_root_lines_and_compactions_reported(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                compaction_marker("2026-07-30T05:00:01.000Z"),
                compaction_marker("2026-07-30T05:00:02.000Z"),
                task_complete("2026-07-30T05:01:00.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-compaction-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["root_compactions"], 2)
            self.assertEqual(run["root_lines"], 4)
            self.assertEqual(run["total_compactions"], 2)

    def test_label_includes_rep_range(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                task_complete("2026-07-30T05:01:00.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            runs = [se.score_run(str(make_run(base, "cx-compaction-dev", r, build)))
                    for r in (1, 2, 3)]
            self.assertEqual(se._out_label(runs), "cx-compaction-dev-rep1-3")

    def test_refuses_overwrite_without_force_then_force_allows(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                task_complete("2026-07-30T05:01:00.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            battery = pathlib.Path(tmp) / "battery"
            out_dir = pathlib.Path(tmp) / "out"
            runs = [se.score_run(str(make_run(battery, "cx-compaction-dev", r, build)))
                    for r in (1, 2)]
            out_path, wrote = se.write_output(runs, str(out_dir))
            self.assertTrue(wrote)
            out_path2, wrote2 = se.write_output(runs, str(out_dir))
            self.assertFalse(wrote2)
            self.assertEqual(out_path, out_path2)
            out_path3, wrote3 = se.write_output(runs, str(out_dir), force=True)
            self.assertTrue(wrote3)


if __name__ == "__main__":
    unittest.main()
