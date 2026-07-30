import json, tempfile, pathlib, unittest
import rollout_parser as rp

def L(ts, typ, payload):
    return json.dumps({"timestamp": ts, "type": typ, "payload": payload})

SPAWN_FULL = L("2026-07-28T16:59:22.815Z", "response_item", {
    "type": "function_call", "id": "fc_1", "name": "spawn_agent",
    "namespace": "collaboration",
    "arguments": json.dumps({"task_name": "t_one", "fork_turns": "none",
                             "model": "gpt-5.6-terra", "reasoning_effort": "high",
                             "message": "gAAAAABencrypted"}),
    "call_id": "call_A"})
SPAWN_BARE = L("2026-07-28T16:59:30.000Z", "response_item", {
    "type": "function_call", "id": "fc_2", "name": "spawn_agent",
    "arguments": json.dumps({"task_name": "t_two", "fork_turns": "all",
                             "message": "gAAAAABx"}),
    "call_id": "call_B"})
CHILD_STARTED = L("2026-07-28T16:59:23.116Z", "event_msg", {
    "type": "sub_agent_activity", "event_id": "call_A",
    "agent_thread_id": "019fa9aa-child-uuid", "agent_path": "/root/t_one",
    "kind": "started"})
NOT_A_SPAWN = L("2026-07-28T17:00:00.000Z", "response_item", {
    "type": "function_call", "id": "fc_3", "name": "wait_agent",
    "arguments": "{}", "call_id": "call_C"})
CHILD_STARTED_NO_EVENT_ID = L("2026-07-28T16:59:24.000Z", "event_msg", {
    "type": "sub_agent_activity",
    "agent_thread_id": "019fa9aa-no-id-uuid", "agent_path": "/root/t_three",
    "kind": "started"})

USER_MSG = L("2026-07-28T16:59:00.000Z", "event_msg", {
    "type": "user_message", "message": "Please implement the feature."})
EXEC_FC = L("2026-07-28T17:01:00.000Z", "response_item", {
    "type": "function_call", "id": "fc_10", "name": "exec_command",
    "arguments": json.dumps({"cmd": "pytest -k test_thing", "yield_time_ms": 5000}),
    "call_id": "call_exec_1"})
CUSTOM_EXEC_SKILL_READ = L("2026-07-28T17:01:05.000Z", "response_item", {
    "type": "custom_tool_call", "id": "fc_11", "name": "exec",
    "input": "sed -n '1,240p' /root/.claude/skills/x/SKILL.md",
    "call_id": "call_exec_2"})
APPLY_PATCH_MENTIONS_SKILL = L("2026-07-28T17:01:10.000Z", "response_item", {
    "type": "custom_tool_call", "id": "fc_12", "name": "apply_patch",
    "input": "*** Begin Patch\n*** Update File: skills/x/SKILL.md\n*** End Patch",
    "call_id": "call_patch_1"})
COMPACTED = L("2026-07-28T17:01:15.000Z", "compacted", {})
COMPACTED_MARKER = L("2026-07-28T17:01:16.000Z", "event_msg", {
    "type": "context_compacted"})
TASK_STARTED = L("2026-07-28T17:01:20.000Z", "event_msg", {"type": "task_started"})
TASK_COMPLETE = L("2026-07-28T17:01:25.000Z", "event_msg", {"type": "task_complete"})
WAIT_CALL = L("2026-07-28T17:01:30.000Z", "response_item", {
    "type": "function_call", "id": "fc_13", "name": "wait_agent",
    "arguments": "{}", "call_id": "call_wait_1"})
PATCH_END = L("2026-07-28T17:01:35.000Z", "event_msg", {"type": "patch_apply_end"})
CUSTOM_EXEC_SPAWN_MENTION = L("2026-07-28T17:01:40.000Z", "response_item", {
    "type": "custom_tool_call", "id": "fc_14", "name": "exec",
    "input": "echo 'calling spawn_agent(task_name=\"x\") from a shell script'",
    "call_id": "call_exec_3"})

# --- wait_outcomes() fixtures. Marker shapes are copied verbatim from real
# rollouts (see rollout_parser.py module docstring): the "collaboration"
# namespace envelope `{"message":...,"timed_out":bool}` (confirmed on the
# audit's 1,058-wait Remux root and Drew's stress-2703 corpus) and the
# "multi_agent_v1" namespace envelope `{"status":{...},"timed_out":bool}`
# (confirmed on Drew's codex-5_5 corpus) -- both carry the same top-level
# `timed_out` boolean key. Non-outcome error shapes (argument validation
# errors) are copied verbatim too.
WAIT_TIMEOUT_CALL = L("2026-07-28T17:02:00.000Z", "response_item", {
    "type": "function_call", "id": "fc_20", "name": "wait_agent",
    "namespace": "collaboration",
    "arguments": json.dumps({"timeout_ms": 30000}), "call_id": "call_wait_timeout"})
WAIT_TIMEOUT_OUTPUT = L("2026-07-28T17:02:30.000Z", "response_item", {
    "type": "function_call_output", "id": "fco_20",
    "call_id": "call_wait_timeout",
    "output": json.dumps({"message": "Wait timed out.", "timed_out": True})})

WAIT_SUCCESS_CALL = L("2026-07-28T17:03:00.000Z", "response_item", {
    "type": "function_call", "id": "fc_21", "name": "wait_agent",
    "namespace": "collaboration",
    "arguments": json.dumps({"timeout_ms": 10000}), "call_id": "call_wait_ok"})
WAIT_SUCCESS_OUTPUT = L("2026-07-28T17:03:05.000Z", "response_item", {
    "type": "function_call_output", "id": "fco_21",
    "call_id": "call_wait_ok",
    "output": json.dumps({"message": "Wait completed.", "timed_out": False})})

# multi_agent_v1 namespace shape (Drew's codex-5_5 corpus): different
# envelope, same top-level `timed_out` bool key -- must still be recognized.
WAIT_STATUS_SHAPE_CALL = L("2026-07-28T17:04:00.000Z", "response_item", {
    "type": "function_call", "id": "fc_22", "name": "wait_agent",
    "namespace": "multi_agent_v1",
    "arguments": json.dumps({"timeout_ms": 60000}), "call_id": "call_wait_status"})
WAIT_STATUS_SHAPE_OUTPUT = L("2026-07-28T17:04:10.000Z", "response_item", {
    "type": "function_call_output", "id": "fco_22",
    "call_id": "call_wait_status",
    "output": json.dumps({"status": {"019fake-thread-id": {"complete": True}},
                          "timed_out": False})})

# Argument-validation error: the call never actually waited, so it is not a
# genuine wait outcome -- must be excluded, not counted as timed_out=False.
WAIT_ERROR_CALL = L("2026-07-28T17:05:00.000Z", "response_item", {
    "type": "function_call", "id": "fc_23", "name": "wait_agent",
    "namespace": "collaboration",
    "arguments": json.dumps({"timeout_ms": 1000}), "call_id": "call_wait_err"})
WAIT_ERROR_OUTPUT = L("2026-07-28T17:05:01.000Z", "response_item", {
    "type": "function_call_output", "id": "fco_23",
    "call_id": "call_wait_err",
    "output": "timeout_ms must be at least 10000"})

# Unresolved: no matching function_call_output at all (e.g. session
# truncated mid-poll) -- must be excluded, not guessed at.
WAIT_UNRESOLVED_CALL = L("2026-07-28T17:06:00.000Z", "response_item", {
    "type": "function_call", "id": "fc_24", "name": "wait_agent",
    "namespace": "collaboration",
    "arguments": json.dumps({"timeout_ms": 20000}), "call_id": "call_wait_unresolved"})

# The bare "wait" tool is a DIFFERENT tool (waits on a running script/build,
# not on a spawned agent) with an incompatible output shape -- no
# `timed_out` key at all. wait_outcomes() must not pick this up even though
# parse_session's broader WAIT_NAMES classifier counts it for census
# purposes.
BARE_WAIT_CALL = L("2026-07-28T17:07:00.000Z", "response_item", {
    "type": "function_call", "id": "fc_25", "name": "wait",
    "arguments": "{}", "call_id": "call_bare_wait"})
BARE_WAIT_OUTPUT = L("2026-07-28T17:07:05.000Z", "response_item", {
    "type": "function_call_output", "id": "fco_25",
    "call_id": "call_bare_wait",
    "output": "Script completed\nWall time 8.0 seconds\nOutput:\n"})

# --- lifecycle_calls() fixtures (E8, Amendment 1). Shapes copied verbatim
# from real rollouts (see rollout_parser.py's lifecycle_calls() comment):
# close_agent observed under BOTH the "collaboration" namespace (our battery
# runs, most of the audit corpus) and the "multi_agent_v1" namespace (Drew's
# codex-5_5 corpus, some audit sessions), same {"target": "<id>"} argument
# shape in both. interrupt_agent/followup_task also key their argument
# "target"; resume_agent keys it "id" (per its own tool_search_call schema);
# list_agents takes no arguments. None of the five carry a "task_name" key
# in any rollout inspected.
CLOSE_AGENT_COLLAB = L("2026-07-28T17:08:00.000Z", "response_item", {
    "type": "function_call", "id": "fc_30", "name": "close_agent",
    "namespace": "collaboration",
    "arguments": json.dumps({"target": "019fake-child-thread-id"}),
    "call_id": "call_close_1"})
CLOSE_AGENT_MULTI = L("2026-07-28T17:08:05.000Z", "response_item", {
    "type": "function_call", "id": "fc_31", "name": "close_agent",
    "namespace": "multi_agent_v1",
    "arguments": json.dumps({"target": "019fake-child-thread-id-2"}),
    "call_id": "call_close_2"})
INTERRUPT_AGENT_CALL = L("2026-07-28T17:08:10.000Z", "response_item", {
    "type": "function_call", "id": "fc_32", "name": "interrupt_agent",
    "namespace": "collaboration",
    "arguments": json.dumps({"target": "/root/task2_session"}),
    "call_id": "call_interrupt_1"})
FOLLOWUP_TASK_CALL = L("2026-07-28T17:08:15.000Z", "response_item", {
    "type": "function_call", "id": "fc_33", "name": "followup_task",
    "namespace": "collaboration",
    "arguments": json.dumps({"target": "/root/task2_session",
                             "message": "gAAAAABencrypted"}),
    "call_id": "call_followup_1"})
RESUME_AGENT_CALL = L("2026-07-28T17:08:20.000Z", "response_item", {
    "type": "function_call", "id": "fc_34", "name": "resume_agent",
    "namespace": "multi_agent_v1",
    "arguments": json.dumps({"id": "019fake-child-thread-id-3"}),
    "call_id": "call_resume_1"})
LIST_AGENTS_CALL = L("2026-07-28T17:08:25.000Z", "response_item", {
    "type": "function_call", "id": "fc_35", "name": "list_agents",
    "namespace": "collaboration",
    "arguments": "{}",
    "call_id": "call_list_1"})

# --- patch_applies() fixtures (E4, Task 11). Shape copied verbatim from a
# real rollout (evals/results/cx-eff-cx-sdd-small-dev-rep5/.../rollout-*.jsonl,
# see rollout_parser.py's patch_applies() docstring): a `patch_apply_end`
# event_msg carries `success` (bool) and `changes` (a dict keyed by absolute
# path, each value describing the change -- add/update/delete -- which
# patch_applies() never reads, only the keys).
PATCH_APPLY_SUCCESS_TWO_PATHS = L("2026-07-29T10:00:00.000Z", "event_msg", {
    "type": "patch_apply_end", "call_id": "exec-p1", "turn_id": "turn-1",
    "success": True,
    "changes": {
        "/work/repo/docs/USAGE.md": {"type": "add", "content": "# usage"},
        "/work/repo/README.md": {"type": "update", "unified_diff": "@@ -0,0 +1 @@\n+x\n"},
    }})
PATCH_APPLY_FAILURE_EMPTY_CHANGES = L("2026-07-29T10:00:05.000Z", "event_msg", {
    "type": "patch_apply_end", "call_id": "exec-p2", "turn_id": "turn-1",
    "success": False, "changes": {}})
PATCH_APPLY_NO_CHANGES_KEY = L("2026-07-29T10:00:10.000Z", "event_msg", {
    "type": "patch_apply_end", "call_id": "exec-p3", "turn_id": "turn-1",
    "success": True})

# --- skill_reads()/compaction_events() fixtures (E6, Task 9). skill_reads()
# must extract the literal SKILL.md path token (not just a boolean match)
# so a caller can tell WHICH skill was read before vs after a compaction.
SKILL_READ_CAT = L("2026-07-28T18:00:00.000Z", "response_item", {
    "type": "function_call", "id": "fc_40", "name": "exec_command",
    "arguments": json.dumps({"cmd": "cat skills/subagent-driven-development/SKILL.md"}),
    "call_id": "call_skill_1"})
SKILL_READ_CUSTOM_EXEC_2 = L("2026-07-28T18:00:05.000Z", "response_item", {
    "type": "custom_tool_call", "id": "fc_41", "name": "exec",
    "input": "sed -n '1,50p' skills/writing-plans/SKILL.md",
    "call_id": "call_skill_2"})
NON_SKILL_READ = L("2026-07-28T18:00:10.000Z", "response_item", {
    "type": "function_call", "id": "fc_42", "name": "exec_command",
    "arguments": json.dumps({"cmd": "ls skills/"}), "call_id": "call_ls_1"})
COMPACTED_MARKER_2 = L("2026-07-28T18:00:20.000Z", "event_msg", {
    "type": "context_compacted"})


def write_fixture(lines):
    f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
    f.write("\n".join(lines) + "\n")
    f.close()
    return pathlib.Path(f.name)

class TestSpawns(unittest.TestCase):
    def test_extract_spawns_full_and_omitted(self):
        p = write_fixture([SPAWN_FULL, CHILD_STARTED, SPAWN_BARE, NOT_A_SPAWN, "not json"])
        s = rp.extract_spawns(p)
        self.assertEqual(len(s), 2)
        self.assertEqual((s[0].call_id, s[0].fork_turns, s[0].model), ("call_A", "none", "gpt-5.6-terra"))
        self.assertEqual((s[1].fork_turns, s[1].model, s[1].reasoning_effort), ("all", "(omitted)", "(omitted)"))

    def test_child_links(self):
        p = write_fixture([SPAWN_FULL, CHILD_STARTED, SPAWN_BARE])
        self.assertEqual(rp.child_links(p), {"call_A": "019fa9aa-child-uuid"})

    def test_child_links_missing_event_id(self):
        p = write_fixture([SPAWN_FULL, CHILD_STARTED, CHILD_STARTED_NO_EVENT_ID])
        # Should skip the record without event_id and return only the valid link
        self.assertEqual(rp.child_links(p), {"call_A": "019fa9aa-child-uuid"})

class TestSessionMetrics(unittest.TestCase):
    def test_parse_session_counters(self):
        p = write_fixture([USER_MSG, SPAWN_FULL, EXEC_FC, CUSTOM_EXEC_SKILL_READ,
                           APPLY_PATCH_MENTIONS_SKILL, COMPACTED, COMPACTED_MARKER,
                           TASK_STARTED, TASK_COMPLETE, WAIT_CALL, PATCH_END])
        m = rp.parse_session(p)
        self.assertEqual(m.compactions, 1)
        self.assertEqual(m.task_started, 1)
        self.assertEqual(m.task_complete, 1)
        self.assertEqual(m.skill_reads_compat, 2)   # real read + apply_patch mention
        self.assertEqual(m.skill_reads_strict, 1)   # real read only
        self.assertEqual(m.spawn_calls, 1)
        self.assertEqual(m.wait_calls, 1)
        self.assertEqual(m.user_messages, 1)
        self.assertEqual(m.patch_applies, 1)
        self.assertEqual(m.first_instruction_line, 0)

    def test_exec_commands_both_encodings(self):
        p = write_fixture([EXEC_FC, CUSTOM_EXEC_SKILL_READ])
        cmds = rp.exec_commands(p)
        self.assertEqual([c.encoding for c in cmds], ["exec_command", "custom_exec"])
        self.assertIn("pytest", cmds[0].cmd)

    def test_spawn_calls_matches_broad_audit_classifier(self):
        # A custom_tool_call exec whose input merely *mentions* spawn_agent(
        # (not a real function_call named spawn_agent) must still count in
        # the parse_session spawn_calls counter, mirroring the audit's
        # isSpawn classifier (name === "spawn_agent" || /\bspawn_agent\(/),
        # while extract_spawns' structured-tuple extraction — which only
        # recognizes function_call records named spawn_agent — must NOT
        # produce a Spawn tuple for it.
        p = write_fixture([CUSTOM_EXEC_SPAWN_MENTION])
        m = rp.parse_session(p)
        self.assertEqual(m.spawn_calls, 1)
        self.assertEqual(rp.extract_spawns(p), [])

class TestWaitOutcomes(unittest.TestCase):
    def test_wait_outcomes_pairing_and_classification(self):
        p = write_fixture([
            WAIT_TIMEOUT_CALL, WAIT_TIMEOUT_OUTPUT,
            WAIT_SUCCESS_CALL, WAIT_SUCCESS_OUTPUT,
            WAIT_STATUS_SHAPE_CALL, WAIT_STATUS_SHAPE_OUTPUT,
            WAIT_ERROR_CALL, WAIT_ERROR_OUTPUT,
            WAIT_UNRESOLVED_CALL,
            BARE_WAIT_CALL, BARE_WAIT_OUTPUT,
        ])
        waits = rp.wait_outcomes(p)
        # error / unresolved / bare-"wait"-tool calls are excluded; only the
        # 3 genuine wait_agent outcomes remain
        self.assertEqual(len(waits), 3)
        by_id = {w.call_id: w for w in waits}
        self.assertEqual(set(by_id), {"call_wait_timeout", "call_wait_ok", "call_wait_status"})

        timeout = by_id["call_wait_timeout"]
        self.assertTrue(timeout.timed_out)
        self.assertEqual(timeout.duration_hint, "30000")
        self.assertEqual(timeout.timestamp, "2026-07-28T17:02:00.000Z")

        ok = by_id["call_wait_ok"]
        self.assertFalse(ok.timed_out)
        self.assertEqual(ok.duration_hint, "10000")

        # multi_agent_v1 envelope: different shape, same timed_out semantics
        status_shape = by_id["call_wait_status"]
        self.assertFalse(status_shape.timed_out)

    def test_wait_outcomes_empty_file(self):
        p = write_fixture([NOT_A_SPAWN])
        self.assertEqual(rp.wait_outcomes(p), [])

class TestLifecycleCalls(unittest.TestCase):
    def test_lifecycle_calls_all_names_and_namespaces(self):
        p = write_fixture([
            CLOSE_AGENT_COLLAB, CLOSE_AGENT_MULTI, INTERRUPT_AGENT_CALL,
            FOLLOWUP_TASK_CALL, RESUME_AGENT_CALL, LIST_AGENTS_CALL,
            SPAWN_FULL, WAIT_CALL,
        ])
        calls = rp.lifecycle_calls(p)
        self.assertEqual(
            [c.name for c in calls],
            ["close_agent", "close_agent", "interrupt_agent",
             "followup_task", "resume_agent", "list_agents"])
        self.assertEqual(
            [c.call_id for c in calls],
            ["call_close_1", "call_close_2", "call_interrupt_1",
             "call_followup_1", "call_resume_1", "call_list_1"])
        # None of the five tools carry a "task_name" argument in any
        # observed rollout shape -- args_task_name stays the omitted
        # sentinel for every one of them.
        self.assertTrue(all(c.args_task_name == rp.OMIT for c in calls))
        self.assertEqual(calls[0].timestamp, "2026-07-28T17:08:00.000Z")

    def test_lifecycle_calls_excludes_spawn_and_wait(self):
        p = write_fixture([SPAWN_FULL, WAIT_CALL, NOT_A_SPAWN])
        self.assertEqual(rp.lifecycle_calls(p), [])

class TestPatchApplies(unittest.TestCase):
    def test_patch_applies_extracts_sorted_paths_and_success(self):
        p = write_fixture([PATCH_APPLY_SUCCESS_TWO_PATHS])
        applies = rp.patch_applies(p)
        self.assertEqual(len(applies), 1)
        a = applies[0]
        self.assertEqual(a.call_id, "exec-p1")
        self.assertEqual(a.timestamp, "2026-07-29T10:00:00.000Z")
        self.assertTrue(a.success)
        self.assertEqual(a.paths, ["/work/repo/README.md", "/work/repo/docs/USAGE.md"])

    def test_patch_applies_failure_with_empty_changes(self):
        p = write_fixture([PATCH_APPLY_FAILURE_EMPTY_CHANGES])
        a = rp.patch_applies(p)[0]
        self.assertFalse(a.success)
        self.assertEqual(a.paths, [])

    def test_patch_applies_missing_changes_key(self):
        p = write_fixture([PATCH_APPLY_NO_CHANGES_KEY])
        a = rp.patch_applies(p)[0]
        self.assertTrue(a.success)
        self.assertEqual(a.paths, [])

    def test_patch_applies_multiple_events_in_file_order(self):
        p = write_fixture([
            PATCH_APPLY_SUCCESS_TWO_PATHS, PATCH_APPLY_FAILURE_EMPTY_CHANGES,
            NOT_A_SPAWN, PATCH_APPLY_NO_CHANGES_KEY,
        ])
        applies = rp.patch_applies(p)
        self.assertEqual([a.call_id for a in applies], ["exec-p1", "exec-p2", "exec-p3"])

    def test_patch_applies_empty_file(self):
        p = write_fixture([NOT_A_SPAWN])
        self.assertEqual(rp.patch_applies(p), [])

class TestSkillReadsAndCompactionEvents(unittest.TestCase):
    """skill_reads()/compaction_events() (E6, Task 9): per-event (not
    aggregate-count) extraction so a caller can partition a session's
    timeline at a compaction boundary and compare WHICH skill paths were
    read before vs after."""

    def test_skill_reads_extracts_path_both_encodings_excludes_non_strict(self):
        p = write_fixture([SKILL_READ_CAT, CUSTOM_EXEC_SKILL_READ,
                           SKILL_READ_CUSTOM_EXEC_2, APPLY_PATCH_MENTIONS_SKILL,
                           NON_SKILL_READ])
        reads = rp.skill_reads(p)
        # APPLY_PATCH_MENTIONS_SKILL (not exec-like) and NON_SKILL_READ (no
        # SKILL.md match) must both be excluded -- exactly the 3 genuine reads.
        self.assertEqual(len(reads), 3)
        self.assertEqual(reads[0].skill_path, "skills/subagent-driven-development/SKILL.md")
        self.assertEqual(reads[0].cmd_encoding, "exec_command")
        self.assertEqual(reads[1].skill_path, "/root/.claude/skills/x/SKILL.md")
        self.assertEqual(reads[1].cmd_encoding, "exec")
        self.assertEqual(reads[2].skill_path, "skills/writing-plans/SKILL.md")

    def test_skill_reads_preserves_file_order_with_lineno_and_timestamp(self):
        p = write_fixture([SKILL_READ_CAT, NON_SKILL_READ, SKILL_READ_CUSTOM_EXEC_2])
        reads = rp.skill_reads(p)
        self.assertEqual([r.lineno for r in reads], [0, 2])
        self.assertEqual([r.timestamp for r in reads],
                         ["2026-07-28T18:00:00.000Z", "2026-07-28T18:00:05.000Z"])

    def test_skill_reads_empty_when_none(self):
        p = write_fixture([NON_SKILL_READ, NOT_A_SPAWN])
        self.assertEqual(rp.skill_reads(p), [])

    def test_compaction_events_marker_only_not_bare_compacted(self):
        p = write_fixture([COMPACTED, COMPACTED_MARKER, COMPACTED_MARKER_2])
        events = rp.compaction_events(p)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].timestamp, "2026-07-28T17:01:16.000Z")
        self.assertEqual(events[0].lineno, 1)
        self.assertEqual(events[1].lineno, 2)

    def test_compaction_events_empty_when_none(self):
        p = write_fixture([SKILL_READ_CAT, NOT_A_SPAWN])
        self.assertEqual(rp.compaction_events(p), [])

if __name__ == "__main__":
    unittest.main()
