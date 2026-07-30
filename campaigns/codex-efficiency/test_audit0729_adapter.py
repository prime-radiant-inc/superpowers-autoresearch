"""Tests for audit0729_adapter.py (Task 15 fix rounds 1-2). Synthetic
fixtures only -- fake IDs, hand-built minimal records -- no real
rollouts, no client content, nothing from the actual (still-unlocated)
2026-07-29 corpus.

Covers two fix-round-2 defects:
  1. `_pick_root(disc)` -- an earlier draft's inline fallback chain in
     main() only checked 3 of the 5 discovery legs and raised IndexError
     if the root was found solely via one of the archived_sessions legs
     added in fix round 1. Every single-leg-hit case is covered here,
     plus the DB-only (no file) case and the priority order.
  2. `AUDIT0729_SESSIONS_ROOT` env override -- `test_env_override_*`
     builds a small synthetic root+child tree under a temp dir and runs
     the adapter's own `main()` against it via subprocess with the env
     var set, exercising the full discover -> found -> _pick_root ->
     run_census -> census_node (score_e7/score_e8) path end to end --
     something fix round 1 flagged as never having run against real
     data. Still synthetic, not real data, but a genuine full-pipeline
     smoke test rather than a stub.
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit0729_adapter as aa

ADAPTER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "audit0729_adapter.py")


def _empty_disc():
    """A disc dict with every found()-relevant key empty -- callers
    override just the leg(s) under test."""
    return {
        "filename_hits": [],
        "content_hits": [],
        "full_tree_filename_hits": [],
        "archived_filename_hits": [],
        "archived_content_hits": [],
        "spawn_edge_rows": [],
    }


class TestPickRoot(unittest.TestCase):
    """Each single-leg-hit case, per the fix-round-2 instruction."""

    def test_filename_hits_only(self):
        disc = _empty_disc()
        disc["filename_hits"] = ["/a/root.jsonl"]
        self.assertEqual(aa._pick_root(disc), "/a/root.jsonl")

    def test_full_tree_filename_hits_only(self):
        disc = _empty_disc()
        disc["full_tree_filename_hits"] = ["/a/full-tree-root.jsonl"]
        self.assertEqual(aa._pick_root(disc), "/a/full-tree-root.jsonl")

    def test_content_hits_only(self):
        disc = _empty_disc()
        disc["content_hits"] = ["/a/child-mentioning-root.jsonl"]
        self.assertEqual(aa._pick_root(disc), "/a/child-mentioning-root.jsonl")

    def test_archived_filename_hits_only(self):
        """The exact case fix round 2 was filed for: found() is True
        only because of an archived_sessions filename hit, and the
        pre-fix inline fallback chain in main() didn't check this leg at
        all -- IndexError on disc["content_hits"][0] with an empty list."""
        disc = _empty_disc()
        disc["archived_filename_hits"] = ["/a/archived-root.jsonl"]
        self.assertEqual(aa._pick_root(disc), "/a/archived-root.jsonl")

    def test_archived_content_hits_only(self):
        disc = _empty_disc()
        disc["archived_content_hits"] = ["/a/archived-child.jsonl"]
        self.assertEqual(aa._pick_root(disc), "/a/archived-child.jsonl")

    def test_spawn_edge_rows_only_returns_none(self):
        """A DB-only match (thread_spawn_edges row, no backing file
        anywhere) cannot seed a root path -- _pick_root must return None,
        not crash, so main() can report this case distinctly."""
        disc = _empty_disc()
        disc["spawn_edge_rows"] = [("parent-id", "child-id", "completed")]
        self.assertIsNone(aa._pick_root(disc))

    def test_nothing_found_returns_none(self):
        self.assertIsNone(aa._pick_root(_empty_disc()))

    def test_priority_order_filename_hits_wins(self):
        disc = _empty_disc()
        disc["filename_hits"] = ["/a/narrow.jsonl"]
        disc["full_tree_filename_hits"] = ["/a/full-tree.jsonl"]
        disc["content_hits"] = ["/a/content.jsonl"]
        disc["archived_filename_hits"] = ["/a/archived-fn.jsonl"]
        disc["archived_content_hits"] = ["/a/archived-content.jsonl"]
        self.assertEqual(aa._pick_root(disc), "/a/narrow.jsonl")

    def test_priority_order_full_tree_before_content(self):
        disc = _empty_disc()
        disc["full_tree_filename_hits"] = ["/a/full-tree.jsonl"]
        disc["content_hits"] = ["/a/content.jsonl"]
        self.assertEqual(aa._pick_root(disc), "/a/full-tree.jsonl")


def _rec(ts, typ, payload):
    return json.dumps({"timestamp": ts, "type": typ, "payload": payload})


def _build_synthetic_tree(sessions_root, root_id, child_id):
    """A minimal root(implementer, 1 child, waits, list_agents, 2x
    identical go-test) + child(reviewer, mentions root_id as its
    parent -- the leg-2 content-match shape) tree, entirely synthetic."""
    date_dir = sessions_root / "2026" / "07" / "29"
    date_dir.mkdir(parents=True)

    root_lines = [
        _rec("2026-07-29T11:00:00.000Z", "event_msg",
             {"type": "user_message", "message": "Please implement the thing."}),
        _rec("2026-07-29T11:00:01.000Z", "response_item", {
            "type": "function_call", "id": "fc_spawn", "name": "spawn_agent",
            "namespace": "collaboration",
            "arguments": json.dumps({"task_name": "reviewer", "fork_turns": "none",
                                     "model": "gpt-5.6-terra"}),
            "call_id": "call_spawn"}),
        _rec("2026-07-29T11:00:02.000Z", "event_msg", {
            "type": "sub_agent_activity", "kind": "started",
            "event_id": "call_spawn", "agent_thread_id": child_id}),
        _rec("2026-07-29T11:00:03.000Z", "response_item", {
            "type": "function_call", "id": "fc_wait", "name": "wait_agent",
            "arguments": json.dumps({"timeout_ms": "30000"}), "call_id": "call_wait"}),
        _rec("2026-07-29T11:00:33.000Z", "response_item", {
            "type": "function_call_output", "call_id": "call_wait",
            "output": json.dumps({"message": "Wait completed.", "timed_out": False})}),
        _rec("2026-07-29T11:00:34.000Z", "response_item", {
            "type": "function_call", "id": "fc_list", "name": "list_agents",
            "arguments": "{}", "call_id": "call_list"}),
        _rec("2026-07-29T11:00:35.000Z", "response_item", {
            "type": "function_call", "id": "fc_exec1", "name": "exec_command",
            "arguments": json.dumps({"cmd": "go test ./..."}), "call_id": "call_exec1"}),
        _rec("2026-07-29T11:00:40.000Z", "response_item", {
            "type": "function_call", "id": "fc_exec2", "name": "exec_command",
            "arguments": json.dumps({"cmd": "go test ./..."}), "call_id": "call_exec2"}),
        _rec("2026-07-29T11:00:45.000Z", "event_msg", {
            "type": "task_complete", "turn_id": "t1", "last_agent_message": "done",
            "completed_at": 1, "duration_ms": 1}),
    ]
    root_path = date_dir / f"rollout-2026-07-29T11-00-00-{root_id}.jsonl"
    root_path.write_text("\n".join(root_lines) + "\n")

    child_lines = [
        _rec("2026-07-29T11:00:02.500Z", "session_meta", {
            "session_id": child_id, "thread_source": "subagent",
            "source": {"subagent": {"thread_spawn": {
                "parent_thread_id": root_id, "depth": 1}}}}),
        _rec("2026-07-29T11:00:03.000Z", "event_msg",
             {"type": "user_message", "message": "Please review the diff."}),
        _rec("2026-07-29T11:00:04.000Z", "event_msg", {
            "type": "task_complete", "turn_id": "t2", "last_agent_message": "done",
            "completed_at": 1, "duration_ms": 1}),
    ]
    child_path = date_dir / f"rollout-2026-07-29T11-00-02-{child_id}.jsonl"
    child_path.write_text("\n".join(child_lines) + "\n")
    return root_path, child_path


class TestSessionsRootEnvOverride(unittest.TestCase):
    """AUDIT0729_SESSIONS_ROOT (fix round 2) -- full pipeline against a
    synthetic corpus, via subprocess so the env var is actually read the
    way a real invocation reads it (module-import time), not just
    attribute-patched."""

    def test_full_pipeline_finds_and_censuses_synthetic_tree(self):
        root_id = "faketree0001root"
        child_id = "faketree0001child"
        with tempfile.TemporaryDirectory() as tmp:
            sessions_root = pathlib.Path(tmp) / "sessions"
            _build_synthetic_tree(sessions_root, root_id, child_id)

            env = dict(os.environ)
            env["AUDIT0729_SESSIONS_ROOT"] = str(sessions_root)
            result = subprocess.run(
                [sys.executable, ADAPTER_PATH, root_id],
                env=env, capture_output=True, text=True, timeout=30)

            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertIn("RESULT: FOUND", result.stdout)
            self.assertIn("tree sessions: 2", result.stdout)
            self.assertIn("total wait_agent (tree): 1", result.stdout)
            self.assertIn("total list_agents (tree): 1", result.stdout)
            self.assertIn("total go-test exec_commands (tree): 2", result.stdout)
            self.assertIn("max identical-normalized-test-command repeat, "
                           "any single session: 2", result.stdout)
            self.assertIn("'implementer': 1", result.stdout)
            self.assertIn("'reviewer': 1", result.stdout)

    def test_default_root_unaffected_when_env_unset(self):
        """Sanity check the override is additive: with the env var
        absent, SESSIONS_ROOT falls back to the real ~/.codex/sessions
        default (not asserting on its contents -- just that the
        constant, not the env var, drives the fallback)."""
        env = {k: v for k, v in os.environ.items() if k != "AUDIT0729_SESSIONS_ROOT"}
        result = subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0, %r); import audit0729_adapter as aa; "
             "print(aa.SESSIONS_ROOT)" % os.path.dirname(ADAPTER_PATH)],
            env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), os.path.expanduser("~/.codex/sessions"))


if __name__ == "__main__":
    unittest.main()
