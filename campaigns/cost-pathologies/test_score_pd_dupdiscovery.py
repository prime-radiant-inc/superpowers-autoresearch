"""Tests for score_pd_dupdiscovery.py (plan-decomposition campaign, Task
2b). Synthetic rollout fixtures only, built inline via small JSONL-record
helpers -- mirrors test_score_x5_leases.py's own test style (that
module's closest precedent for "many small independent exec-command
shapes"), rather than a committed-fixture-directory style.

Real-corpus validation (control-rep9/control-rep10's controller
test-run-count anchors of 8/9) is NOT run here as a pytest -- the real
reps live in sibling repos (evals/results, evals-lane-b/results), not
committed to this one, so a test depending on those absolute paths would
break on any other checkout. That validation is reported directly (see
this task's report), the same "no committed real-corpus fixture" pattern
test_score_x1_chains.py's own module docstring notes for its corpus.

Everything here is synthetic; no real system, no real orders.
"""
import json
import os
import tempfile
import unittest


def _rec(ts, typ, payload):
    return json.dumps({"timestamp": ts, "type": typ, "payload": payload})


def custom_exec_cmd(ts, call_id, raw_input):
    """custom_tool_call/"exec" encoding -- the ONLY encoding observed in
    the cp-x5-leases-scaled corpus this scorer was validated against (see
    module docstring's CRITICAL FORMAT NOTE)."""
    return _rec(ts, "response_item", {
        "type": "custom_tool_call", "id": call_id, "name": "exec",
        "input": raw_input, "call_id": call_id})


def exec_cmd(ts, call_id, cmd):
    """Plain "exec_command" encoding -- JSON-decoded `cmd` string."""
    return _rec(ts, "response_item", {
        "type": "function_call", "id": call_id, "name": "exec_command",
        "arguments": json.dumps({"cmd": cmd}), "call_id": call_id})


def spawn_agent_call(ts, call_id, task_name):
    return _rec(ts, "response_item", {
        "type": "function_call", "id": call_id, "name": "spawn_agent",
        "arguments": json.dumps({"task_name": task_name}), "call_id": call_id})


def write_rollout(tmpdir, name, lines):
    path = os.path.join(tmpdir, name)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


# A real corpus custom_exec shape (cp-x5-leases-scaled-control-rep10),
# trimmed -- used to prove normalize_command strips the rep-specific
# workdir path so the SAME logical command normalizes identically no
# matter which rep/agent ran it.
def _js_exec(cmd, workdir):
    return ('const r = await tools.exec_command({cmd:"' + cmd + '","workdir":"'
            + workdir + '","yield_time_ms":30000}); text = r.output;')


class TestNormalizeCommand(unittest.TestCase):
    def test_strips_workdir_field(self):
        import score_pd_dupdiscovery as d
        a = d.normalize_command(_js_exec("pytest -q", "/workspace/rep1/coding-agent-workdir"), "custom_exec")
        b = d.normalize_command(_js_exec("pytest -q", "/workspace/rep2/coding-agent-workdir"), "custom_exec")
        self.assertEqual(a, b)
        self.assertNotIn("workdir", a)

    def test_strips_leading_cd_prefix(self):
        import score_pd_dupdiscovery as d
        stripped = d.normalize_command("cd .worktrees/dispatch-queue && pytest -q", "exec_command")
        self.assertEqual(stripped, "pytest -q")

    def test_collapses_whitespace(self):
        import score_pd_dupdiscovery as d
        self.assertEqual(d.normalize_command("pytest   -q\n\ttests/", "exec_command"), "pytest -q tests/")

    def test_exec_command_encoding_is_unaffected_by_custom_exec_only_fields(self):
        # exec_command's arguments carry no "workdir" sibling key -- the
        # workdir-strip regex must be a harmless no-op on real
        # exec_command text that happens to contain the word "workdir"
        # in unrelated content.
        import score_pd_dupdiscovery as d
        cmd = "echo workdir is not a json field here && pytest -q"
        self.assertIn("pytest -q", d.normalize_command(cmd, "exec_command"))


class TestClassify(unittest.TestCase):
    def test_test_run(self):
        import score_pd_dupdiscovery as d
        self.assertEqual(d.classify("pytest tests/"), "test-run")
        self.assertEqual(d.classify("cargo test --all-features"), "test-run")

    def test_lint_format(self):
        import score_pd_dupdiscovery as d
        self.assertEqual(d.classify("ruff check ."), "lint-format")
        self.assertEqual(d.classify("cargo fmt --check"), "lint-format")

    def test_file_read_exploration(self):
        import score_pd_dupdiscovery as d
        self.assertEqual(d.classify("cat SKILL.md"), "file-read")
        self.assertEqual(d.classify("git status --short"), "file-read")

    def test_other_fallback(self):
        import score_pd_dupdiscovery as d
        self.assertEqual(d.classify("git commit -m 'wip'"), "other")

    def test_test_run_wins_over_file_read_in_a_compound_command(self):
        # Real corpus shape (cp-x5-leases-scaled-control-rep10): an
        # exploration prefix chained before the real verification run.
        import score_pd_dupdiscovery as d
        self.assertEqual(d.classify("sed -n '1,120p' .gitignore; pytest -q"), "test-run")


class TestControllerIdentification(unittest.TestCase):
    def test_is_controller_true_iff_has_spawn(self):
        import score_pd_dupdiscovery as d
        with tempfile.TemporaryDirectory() as tmp:
            controller = write_rollout(tmp, "rollout-a.jsonl", [
                spawn_agent_call("2026-08-01T00:00:00", "c1", "task1_impl"),
            ])
            child = write_rollout(tmp, "rollout-b.jsonl", [
                exec_cmd("2026-08-01T00:01:00", "c2", "pytest -q"),
            ])
            self.assertTrue(d.is_controller(controller))
            self.assertFalse(d.is_controller(child))

    def test_find_controller_picks_earliest_timestamp_among_spawners(self):
        import score_pd_dupdiscovery as d
        with tempfile.TemporaryDirectory() as tmp:
            root = write_rollout(tmp, "rollout-root.jsonl", [
                spawn_agent_call("2026-08-01T00:00:00", "c1", "task1_impl"),
            ])
            # A nested spawner (e.g. a reviewer that itself spawns a
            # sub-reviewer) starts LATER -- must not be picked over root.
            nested = write_rollout(tmp, "rollout-nested.jsonl", [
                spawn_agent_call("2026-08-01T00:10:00", "c2", "task1_subreview"),
            ])
            self.assertEqual(d.find_controller([root, nested]), root)

    def test_find_controller_none_when_nothing_qualifies(self):
        import score_pd_dupdiscovery as d
        with tempfile.TemporaryDirectory() as tmp:
            child = write_rollout(tmp, "rollout-b.jsonl", [
                exec_cmd("2026-08-01T00:01:00", "c2", "pytest -q"),
            ])
            self.assertIsNone(d.find_controller([child]))


class TestAgentCommandEvents(unittest.TestCase):
    def test_extracts_from_both_encodings(self):
        import score_pd_dupdiscovery as d
        with tempfile.TemporaryDirectory() as tmp:
            path = write_rollout(tmp, "rollout.jsonl", [
                exec_cmd("2026-08-01T00:00:00", "c1", "pytest tests/"),
                custom_exec_cmd("2026-08-01T00:01:00", "c2",
                                 _js_exec("cargo test", "/workspace/rep/coding-agent-workdir")),
            ])
            events = d.agent_command_events(path)
            self.assertEqual(len(events), 2)
            self.assertEqual(events[0]["class"], "test-run")
            self.assertEqual(events[1]["class"], "test-run")


class TestDupStats(unittest.TestCase):
    def test_same_agent_repeat_is_reported(self):
        import score_pd_dupdiscovery as d
        with tempfile.TemporaryDirectory() as tmp:
            path = write_rollout(tmp, "rollout-a.jsonl", [
                exec_cmd("2026-08-01T00:00:00", "c1", "pytest tests/"),
                exec_cmd("2026-08-01T00:01:00", "c2", "pytest tests/"),
                exec_cmd("2026-08-01T00:02:00", "c3", "cat README.md"),
            ])
            report = d.dup_stats([path])
            agent = report["agents"][0]
            self.assertEqual(len(agent["repeat_commands"]), 1)
            self.assertEqual(agent["repeat_commands"][0]["count"], 2)
            self.assertEqual(agent["repeat_commands"][0]["class"], "test-run")
            # the single-occurrence "cat README.md" is not a repeat
            self.assertEqual(agent["class_counts"]["file-read"], 1)

    def test_cross_agent_duplicate_is_reported(self):
        import score_pd_dupdiscovery as d
        with tempfile.TemporaryDirectory() as tmp:
            a = write_rollout(tmp, "rollout-a.jsonl", [
                exec_cmd("2026-08-01T00:00:00", "c1", "pytest tests/"),
            ])
            b = write_rollout(tmp, "rollout-b.jsonl", [
                exec_cmd("2026-08-01T00:05:00", "c2", "pytest tests/"),
            ])
            report = d.dup_stats([a, b])
            self.assertEqual(len(report["cross_agent_duplicates"]), 1)
            dup = report["cross_agent_duplicates"][0]
            self.assertEqual(dup["count"], 2)
            self.assertEqual(sorted(dup["agents"]), ["rollout-a.jsonl", "rollout-b.jsonl"])
            # neither agent alone repeated it -- no same-agent repeat entries
            for agent in report["agents"]:
                self.assertEqual(agent["repeat_commands"], [])

    def test_controller_test_run_count(self):
        import score_pd_dupdiscovery as d
        with tempfile.TemporaryDirectory() as tmp:
            controller = write_rollout(tmp, "rollout-controller.jsonl", [
                spawn_agent_call("2026-08-01T00:00:00", "s1", "task1_impl"),
                exec_cmd("2026-08-01T00:01:00", "c1", "pytest -q"),
                exec_cmd("2026-08-01T00:02:00", "c2", "pytest tests/"),
                exec_cmd("2026-08-01T00:03:00", "c3", "git status"),
            ])
            implementer = write_rollout(tmp, "rollout-impl.jsonl", [
                exec_cmd("2026-08-01T00:01:30", "c4", "pytest -q"),
                exec_cmd("2026-08-01T00:01:31", "c5", "pytest -q"),
            ])
            report = d.dup_stats([controller, implementer])
            self.assertEqual(report["controller_test_run_count"], 2)

    def test_controller_test_run_count_none_without_a_controller(self):
        import score_pd_dupdiscovery as d
        with tempfile.TemporaryDirectory() as tmp:
            path = write_rollout(tmp, "rollout-a.jsonl", [
                exec_cmd("2026-08-01T00:00:00", "c1", "pytest -q"),
            ])
            report = d.dup_stats([path])
            self.assertIsNone(report["controller_test_run_count"])

    def test_cmd_id_is_stable_between_repeat_and_cross_agent_views(self):
        import score_pd_dupdiscovery as d
        with tempfile.TemporaryDirectory() as tmp:
            a = write_rollout(tmp, "rollout-a.jsonl", [
                exec_cmd("2026-08-01T00:00:00", "c1", "pytest tests/"),
                exec_cmd("2026-08-01T00:01:00", "c2", "pytest tests/"),
            ])
            b = write_rollout(tmp, "rollout-b.jsonl", [
                exec_cmd("2026-08-01T00:02:00", "c3", "pytest tests/"),
            ])
            report = d.dup_stats([a, b])
            repeat_id = next(r["cmd_id"] for agent in report["agents"]
                              for r in agent["repeat_commands"])
            cross_id = report["cross_agent_duplicates"][0]["cmd_id"]
            self.assertEqual(repeat_id, cross_id)

    def test_no_raw_command_text_leaks_into_the_report(self):
        # Privacy convention (see module docstring): only cmd_id/class/
        # count/agents ever appear, never the normalized or raw text.
        import score_pd_dupdiscovery as d
        with tempfile.TemporaryDirectory() as tmp:
            path = write_rollout(tmp, "rollout-a.jsonl", [
                exec_cmd("2026-08-01T00:00:00", "c1", "pytest tests/very_secret_path.py"),
                exec_cmd("2026-08-01T00:01:00", "c2", "pytest tests/very_secret_path.py"),
            ])
            report = d.dup_stats([path])
            serialized = json.dumps(report)
            self.assertNotIn("very_secret_path", serialized)


class TestRolloutsForRepAndCLI(unittest.TestCase):
    def test_rollouts_for_rep_finds_files_under_dot_directories(self):
        # Item 14's dot-directory glob-skip bug class -- see
        # scorer_common.find_files's own docstring. home/.codex/sessions
        # is itself a dot-prefixed path segment.
        import score_pd_dupdiscovery as d
        with tempfile.TemporaryDirectory() as tmp:
            sessions_dir = os.path.join(tmp, "home", ".codex", "sessions", "2026", "08")
            os.makedirs(sessions_dir)
            path = os.path.join(sessions_dir, "rollout-2026-08-01T00-00-00-abc.jsonl")
            with open(path, "w") as f:
                f.write(exec_cmd("2026-08-01T00:00:00", "c1", "pytest -q") + "\n")
            self.assertEqual(d.rollouts_for_rep(tmp), [path])

    def test_main_prints_json_report_for_one_rep_dir(self):
        import io
        import contextlib
        import score_pd_dupdiscovery as d
        with tempfile.TemporaryDirectory() as tmp:
            sessions_dir = os.path.join(tmp, "home", ".codex", "sessions", "2026", "08")
            os.makedirs(sessions_dir)
            path = os.path.join(sessions_dir, "rollout-2026-08-01T00-00-00-abc.jsonl")
            with open(path, "w") as f:
                f.write(spawn_agent_call("2026-08-01T00:00:00", "s1", "task1_impl") + "\n")
                f.write(exec_cmd("2026-08-01T00:01:00", "c1", "pytest -q") + "\n")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = d.main(["score_pd_dupdiscovery.py", tmp])
            self.assertEqual(rc, 0)
            parsed = json.loads(buf.getvalue())
            self.assertEqual(parsed["controller_test_run_count"], 1)


if __name__ == "__main__":
    unittest.main()
