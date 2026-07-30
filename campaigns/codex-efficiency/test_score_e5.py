"""Tests for score_e5.py's seeded-defect recall + review-scope census (Task
12, E5). Synthetic rollout fixtures only -- fake rep-dir names, minimal
hand-built spawn_agent/exec_command/agent_message/patch_apply_end records --
no real rollouts, no client content. Covers score_e5.py's own logic
(rubric-keyword recall matching, review-pass classification split at the
mid-session repair-request timestamp, same-scope duplicate-review detection
via score_e6.task_family reuse, scope-accretion commit counting,
serial-remediation cycle counting, wave-boundary violation detection) -- the
tree walk itself is score_e2.py's already-tested build_tree(), reused not
reimplemented."""
import json, pathlib, tempfile, unittest
import score_e5 as se


def _rec(ts, typ, payload):
    return json.dumps({"timestamp": ts, "type": typ, "payload": payload})


def user_message(ts, text="Please run your full review process on the feature branch and get it ready to merge."):
    return _rec(ts, "event_msg", {"type": "user_message", "message": text})


def agent_message(ts, message, phase="final_answer"):
    return _rec(ts, "event_msg", {"type": "agent_message", "message": message, "phase": phase})


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


def task_complete(ts, last_agent_message="done"):
    return _rec(ts, "event_msg", {
        "type": "task_complete", "turn_id": "t1",
        "last_agent_message": last_agent_message, "completed_at": 1, "duration_ms": 1})


def exec_cmd(ts, call_id, cmd):
    return _rec(ts, "response_item", {
        "type": "function_call", "id": call_id, "name": "exec_command",
        "arguments": json.dumps({"cmd": cmd}), "call_id": call_id})


def custom_exec_cmd(ts, call_id, raw_input):
    """custom_tool_call/"exec" encoding -- `input` is taken WHOLE, never
    JSON-decoded (see rollout_parser.exec_commands()'s docstring), same
    convention as score_e3's test helper of the same name -- used to
    exercise the deescape_custom_exec() fix (Task 10 fix round 1) that
    score_e5._git_commit_events() must also apply, since it calls
    rp.exec_commands() directly with its own GIT_COMMIT_RE, the same
    shape of call site the fix was scoped to."""
    return _rec(ts, "response_item", {
        "type": "custom_tool_call", "id": call_id, "name": "exec",
        "input": raw_input, "call_id": call_id})


def patch_apply(ts, success=True, paths=None):
    return _rec(ts, "event_msg", {
        "type": "patch_apply_end", "success": success,
        "changes": {p: {} for p in (paths or ["mtqueue/batch.py"])}})


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


REPAIR_TEXT = ("Actually, hold on -- I just tried pulling a batch from the "
               "queue without passing a size, and it only gave me back 1 "
               "item instead of the 5 the docs promise. Can you fix that "
               "and make sure the branch is ready to merge?")


class TestRubricHits(unittest.TestCase):
    def test_d1_hit_on_default_batch_size_and_numbers(self):
        text = "Found DEFAULT_BATCH_SIZE returns 1 item instead of the documented default of 5."
        self.assertTrue(se.rubric_hit("D1", text))

    def test_d1_no_hit_on_unrelated_text(self):
        self.assertFalse(se.rubric_hit("D1", "The branch looks ready to merge, no issues found."))

    def test_d2_hit_on_peek_batch_and_lock(self):
        text = "peek_batch() reads self._items without acquiring the lock -- a race with push()."
        self.assertTrue(se.rubric_hit("D2", text))

    def test_d2_no_hit_when_only_batch_mentioned(self):
        self.assertFalse(se.rubric_hit("D2", "The batch API looks fine overall."))

    def test_d3_hit_on_msgpack_dependency(self):
        text = "batch_codec.py imports msgpack but it's missing from pyproject.toml's dependencies."
        self.assertTrue(se.rubric_hit("D3", text))

    def test_d3_hit_on_modulenotfounderror(self):
        text = "Running pytest raised ModuleNotFoundError: No module named 'msgpack'."
        self.assertTrue(se.rubric_hit("D3", text))

    def test_d3_no_hit_on_unrelated_text(self):
        self.assertFalse(se.rubric_hit("D3", "All tests pass, docs look good."))


class TestRecallMatrix(unittest.TestCase):
    def test_root_pre_repair_message_credited_to_review_pass(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                agent_message("2026-07-30T05:00:10.000Z",
                              "Found DEFAULT_BATCH_SIZE is 1, should be 5 per docs/BATCH.md."),
                task_complete("2026-07-30T05:00:11.000Z"),
                user_message("2026-07-30T05:00:20.000Z", REPAIR_TEXT),
                agent_message("2026-07-30T05:00:30.000Z", "Fixed the default, branch is ready."),
                task_complete("2026-07-30T05:00:31.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            d1_hits = run["recall_matrix"]["D1"]
            self.assertEqual(len(d1_hits), 1)
            self.assertEqual(d1_hits[0]["pass"], "review")

    def test_post_repair_message_credited_to_fix_review_pass(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                agent_message("2026-07-30T05:00:10.000Z", "Branch looks ready to merge."),
                task_complete("2026-07-30T05:00:11.000Z"),
                user_message("2026-07-30T05:00:20.000Z", REPAIR_TEXT),
                agent_message("2026-07-30T05:00:30.000Z",
                               "Fixed it -- DEFAULT_BATCH_SIZE was 1, now 5."),
                task_complete("2026-07-30T05:00:31.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            d1_hits = run["recall_matrix"]["D1"]
            self.assertEqual(len(d1_hits), 1)
            self.assertEqual(d1_hits[0]["pass"], "fix_review")

    def test_defect_never_mentioned_is_a_miss(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                agent_message("2026-07-30T05:00:10.000Z", "Branch looks ready to merge, no issues."),
                task_complete("2026-07-30T05:00:11.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["recall_matrix"]["D1"], [])
            self.assertEqual(run["recall_matrix"]["D2"], [])
            self.assertEqual(run["recall_matrix"]["D3"], [])

    def test_dispatched_reviewer_final_answer_also_searched(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                spawn_call("2026-07-30T05:00:01.000Z", "call_A", "branch_review"),
                sub_agent_started("2026-07-30T05:00:02.000Z", "call_A", "rev00001"),
                task_complete("2026-07-30T05:01:00.000Z"),
            ])
            write_rollout(sess_dir, "2026-07-30T05-00-05", "rev00001", [
                agent_message("2026-07-30T05:00:20.000Z",
                               "peek_batch reads self._items without the lock -- a race with push()."),
                task_complete("2026-07-30T05:00:30.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            d2_hits = run["recall_matrix"]["D2"]
            self.assertEqual(len(d2_hits), 1)
            self.assertEqual(d2_hits[0]["rollout"], "rollout-2026-07-30T05-00-05-rev00001.jsonl")


class TestPassClassification(unittest.TestCase):
    def test_dispatch_with_fix_in_task_name_is_fix_review(self):
        self.assertEqual(se.classify_pass_by_task_name("fix_review"), "fix_review")
        self.assertEqual(se.classify_pass_by_task_name("repair_reviewer"), "fix_review")

    def test_dispatch_with_branch_in_task_name_is_branch_review(self):
        self.assertEqual(se.classify_pass_by_task_name("branch_review"), "branch_review")

    def test_dispatch_with_task_in_task_name_is_task_review(self):
        self.assertEqual(se.classify_pass_by_task_name("task1_review"), "task_review")

    def test_unclassified_task_name(self):
        self.assertEqual(se.classify_pass_by_task_name("widget_thing"), "unclassified")

    def test_omitted_task_name(self):
        import rollout_parser as rp
        self.assertEqual(se.classify_pass_by_task_name(rp.OMIT), "unclassified")
        self.assertEqual(se.classify_pass_by_task_name(None), "unclassified")


class TestRepairRequestTimestamp(unittest.TestCase):
    def test_finds_repair_request_by_marker(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                task_complete("2026-07-30T05:00:11.000Z"),
                user_message("2026-07-30T05:00:20.000Z", REPAIR_TEXT),
                task_complete("2026-07-30T05:00:31.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            rollouts = se.find_rollouts(str(rundir))
            ts = se.find_repair_request_timestamp(rollouts)
            self.assertEqual(ts, "2026-07-30T05:00:20.000Z")

    def test_none_when_marker_never_appears(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                task_complete("2026-07-30T05:00:11.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            rollouts = se.find_rollouts(str(rundir))
            self.assertIsNone(se.find_repair_request_timestamp(rollouts))


class TestScopeAccretion(unittest.TestCase):
    def test_counts_commits_strictly_after_first_completion_claim(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                exec_cmd("2026-07-30T05:00:05.000Z", "call_1", "git commit -qm 'wip before done'"),
                task_complete("2026-07-30T05:00:10.000Z"),
                exec_cmd("2026-07-30T05:00:15.000Z", "call_2", "git commit -qm 'accretion 1'"),
                exec_cmd("2026-07-30T05:00:20.000Z", "call_3", "git commit -qm 'accretion 2'"),
                task_complete("2026-07-30T05:00:31.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            acc = run["scope_accretion"]
            self.assertEqual(acc["first_completion_timestamp"], "2026-07-30T05:00:10.000Z")
            self.assertEqual(acc["n_commits_after"], 2)

    def test_zero_accretion_commits_when_none_follow(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                exec_cmd("2026-07-30T05:00:05.000Z", "call_1", "git commit -qm 'only commit'"),
                task_complete("2026-07-30T05:00:10.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["scope_accretion"]["n_commits_after"], 0)

    def test_custom_exec_literal_backslash_n_before_git_commit_is_still_detected(self):
        """Same real bug score_e3/rollout_parser fix round 1 found
        (Task 10): a custom_exec command's raw JS-source input can carry
        a literal two-character backslash-n (never JSON-decoded, unlike
        the exec_command encoding), which defeats GIT_COMMIT_RE's
        leading \\b if left un-deescaped. score_e5._git_commit_events()
        calls rp.exec_commands() directly (not rp.mutation_events(),
        which already applies the fix) with its own regex, so it needs
        the same deescape_custom_exec() call."""
        raw = r"echo start\ngit commit -qm 'wip'"  # literal backslash-n, not a real newline
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                custom_exec_cmd("2026-07-30T05:00:05.000Z", "call_1", raw),
                task_complete("2026-07-30T05:00:10.000Z"),
                custom_exec_cmd("2026-07-30T05:00:15.000Z", "call_2", raw),
                task_complete("2026-07-30T05:00:31.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["scope_accretion"]["n_commits_after"], 1)

    def test_no_completion_claim_means_no_accretion_data(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                exec_cmd("2026-07-30T05:00:05.000Z", "call_1", "git commit -qm 'only commit'"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertIsNone(run["scope_accretion"]["first_completion_timestamp"])
            self.assertEqual(run["scope_accretion"]["n_commits_after"], 0)


class TestSameScopeDuplicateReview(unittest.TestCase):
    def test_two_branch_review_dispatches_flagged_as_duplicate(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                spawn_call("2026-07-30T05:00:01.000Z", "call_A", "branch_reviewer"),
                sub_agent_started("2026-07-30T05:00:02.000Z", "call_A", "rev00001"),
                spawn_call("2026-07-30T05:00:03.000Z", "call_B", "branch_reviewer"),
                sub_agent_started("2026-07-30T05:00:04.000Z", "call_B", "rev00002"),
                task_complete("2026-07-30T05:01:00.000Z"),
            ])
            write_rollout(sess_dir, "2026-07-30T05-00-05", "rev00001", [
                task_complete("2026-07-30T05:00:30.000Z")])
            write_rollout(sess_dir, "2026-07-30T05-00-08", "rev00002", [
                task_complete("2026-07-30T05:00:40.000Z")])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            dups = run["same_scope_duplicates"]
            self.assertEqual(len(dups), 1)
            self.assertEqual(dups[0]["family"], "branch")
            self.assertEqual(len(dups[0]["rollouts"]), 2)

    def test_single_dispatch_is_not_a_duplicate(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                spawn_call("2026-07-30T05:00:01.000Z", "call_A", "branch_reviewer"),
                sub_agent_started("2026-07-30T05:00:02.000Z", "call_A", "rev00001"),
                task_complete("2026-07-30T05:01:00.000Z"),
            ])
            write_rollout(sess_dir, "2026-07-30T05-00-05", "rev00001", [
                task_complete("2026-07-30T05:00:30.000Z")])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["same_scope_duplicates"], [])

    def test_implementer_plus_reviewer_same_family_is_not_a_duplicate(self):
        """The ordinary single-review SDD shape -- one implementer, one
        reviewer, same task family -- must NOT be flagged: only 2+
        REVIEWER-role dispatches of the same family are a genuine
        same-scope duplicate."""
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                spawn_call("2026-07-30T05:00:01.000Z", "call_A", "task1_implementer"),
                sub_agent_started("2026-07-30T05:00:02.000Z", "call_A", "impl0001"),
                spawn_call("2026-07-30T05:00:03.000Z", "call_B", "task1_reviewer"),
                sub_agent_started("2026-07-30T05:00:04.000Z", "call_B", "rev00001"),
                task_complete("2026-07-30T05:01:00.000Z"),
            ])
            write_rollout(sess_dir, "2026-07-30T05-00-05", "impl0001", [
                task_complete("2026-07-30T05:00:30.000Z")])
            write_rollout(sess_dir, "2026-07-30T05-00-08", "rev00001", [
                task_complete("2026-07-30T05:00:40.000Z")])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["same_scope_duplicates"], [])

    def test_zero_descendants_means_no_duplicates_by_construction(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                task_complete("2026-07-30T05:01:00.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["same_scope_duplicates"], [])


class TestSerialRemediationCycles(unittest.TestCase):
    def test_two_post_repair_test_runs_is_one_cycle(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                task_complete("2026-07-30T05:00:11.000Z"),
                user_message("2026-07-30T05:00:20.000Z", REPAIR_TEXT),
                exec_cmd("2026-07-30T05:00:21.000Z", "call_1", "pytest tests/"),
                patch_apply("2026-07-30T05:00:22.000Z", success=True),
                exec_cmd("2026-07-30T05:00:23.000Z", "call_2", "pytest tests/"),
                task_complete("2026-07-30T05:00:31.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["serial_remediation_cycles"], 1)

    def test_single_post_repair_test_run_is_zero_cycles(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                task_complete("2026-07-30T05:00:11.000Z"),
                user_message("2026-07-30T05:00:20.000Z", REPAIR_TEXT),
                exec_cmd("2026-07-30T05:00:21.000Z", "call_1", "pytest tests/"),
                task_complete("2026-07-30T05:00:31.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["serial_remediation_cycles"], 0)

    def test_no_repair_request_means_zero_cycles(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                exec_cmd("2026-07-30T05:00:05.000Z", "call_1", "pytest tests/"),
                exec_cmd("2026-07-30T05:00:06.000Z", "call_2", "pytest tests/"),
                task_complete("2026-07-30T05:00:11.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["serial_remediation_cycles"], 0)


class TestFixReviewScope(unittest.TestCase):
    """D4 (the live-emerging defect) has no keyword rubric -- out/e5-
    defect-key.md scores it structurally instead: did the post-repair
    re-review examine only the repair's own diff, or re-scope to the
    whole branch?"""

    def test_no_repair_request_is_reported_distinctly(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                exec_cmd("2026-07-30T05:00:05.000Z", "call_1", "pytest tests/"),
                task_complete("2026-07-30T05:00:11.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["fix_review_scope"], "no_repair_request")

    def test_repair_request_with_no_post_repair_test_run(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                task_complete("2026-07-30T05:00:11.000Z"),
                user_message("2026-07-30T05:00:20.000Z", REPAIR_TEXT),
                patch_apply("2026-07-30T05:00:21.000Z", success=True, paths=["mtqueue/batch.py"]),
                task_complete("2026-07-30T05:00:31.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["fix_review_scope"], "no_post_repair_test_run")

    def test_scoped_file_targeted_test_run_after_repair(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                task_complete("2026-07-30T05:00:11.000Z"),
                user_message("2026-07-30T05:00:20.000Z", REPAIR_TEXT),
                patch_apply("2026-07-30T05:00:21.000Z", success=True, paths=["mtqueue/batch.py"]),
                exec_cmd("2026-07-30T05:00:22.000Z", "call_1", "pytest tests/test_batch.py"),
                task_complete("2026-07-30T05:00:31.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["fix_review_scope"], "repair_scoped")

    def test_whole_suite_rerun_after_repair_is_full_branch_rescope(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                task_complete("2026-07-30T05:00:11.000Z"),
                user_message("2026-07-30T05:00:20.000Z", REPAIR_TEXT),
                patch_apply("2026-07-30T05:00:21.000Z", success=True, paths=["mtqueue/batch.py"]),
                exec_cmd("2026-07-30T05:00:22.000Z", "call_1", "pytest tests/"),
                task_complete("2026-07-30T05:00:31.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["fix_review_scope"], "full_branch_rescope")


class TestWaveBoundaryViolation(unittest.TestCase):
    def test_mutation_from_another_session_during_fix_review_is_a_violation(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                task_complete("2026-07-30T05:00:11.000Z"),
                user_message("2026-07-30T05:00:20.000Z", REPAIR_TEXT),
                spawn_call("2026-07-30T05:00:21.000Z", "call_A", "fix_review"),
                sub_agent_started("2026-07-30T05:00:22.000Z", "call_A", "fix00001"),
                # root itself keeps mutating the tree while the fix-review runs
                exec_cmd("2026-07-30T05:00:25.000Z", "call_2", "git commit -qm 'more changes mid-review'"),
                task_complete("2026-07-30T05:00:40.000Z"),
            ])
            write_rollout(sess_dir, "2026-07-30T05-00-22", "fix00001", [
                task_complete("2026-07-30T05:00:35.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            violations = run["wave_boundary_violations"]
            self.assertEqual(len(violations), 1)
            self.assertEqual(violations[0]["fix_review_rollout"], "rollout-2026-07-30T05-00-22-fix00001.jsonl")
            self.assertEqual(violations[0]["mutating_rollout"], "rollout-2026-07-30T05-00-00-root0000.jsonl")

    def test_no_violation_when_no_mutation_during_fix_review(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                task_complete("2026-07-30T05:00:11.000Z"),
                user_message("2026-07-30T05:00:20.000Z", REPAIR_TEXT),
                spawn_call("2026-07-30T05:00:21.000Z", "call_A", "fix_review"),
                sub_agent_started("2026-07-30T05:00:22.000Z", "call_A", "fix00001"),
                task_complete("2026-07-30T05:00:40.000Z"),
            ])
            write_rollout(sess_dir, "2026-07-30T05-00-22", "fix00001", [
                task_complete("2026-07-30T05:00:35.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["wave_boundary_violations"], [])

    def test_no_fix_review_session_means_no_violations(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                task_complete("2026-07-30T05:00:11.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            self.assertEqual(run["wave_boundary_violations"], [])


class TestManualVerificationHelper(unittest.TestCase):
    def test_matching_context_returns_actual_text_for_a_hit(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                agent_message("2026-07-30T05:00:10.000Z",
                              "DEFAULT_BATCH_SIZE returns 1 item instead of the documented 5."),
                task_complete("2026-07-30T05:00:11.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-scope-review-dev", 1, build)
            run = se.score_run(str(rundir))
            hit = run["recall_matrix"]["D1"][0]
            self.assertIn("DEFAULT_BATCH_SIZE", hit["matched_text"])


class TestOutputConvention(unittest.TestCase):
    def test_label_includes_rep_range(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                task_complete("2026-07-30T05:01:00.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            runs = [se.score_run(str(make_run(base, "cx-scope-review-dev", r, build)))
                    for r in (1, 2, 3)]
            self.assertEqual(se._out_label(runs), "cx-scope-review-dev-rep1-3")

    def test_refuses_overwrite_without_force_then_force_allows(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                user_message("2026-07-30T05:00:00.000Z"),
                task_complete("2026-07-30T05:01:00.000Z"),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            battery = pathlib.Path(tmp) / "battery"
            out_dir = pathlib.Path(tmp) / "out"
            runs = [se.score_run(str(make_run(battery, "cx-scope-review-dev", r, build)))
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
