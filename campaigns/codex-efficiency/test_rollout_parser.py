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

if __name__ == "__main__":
    unittest.main()
