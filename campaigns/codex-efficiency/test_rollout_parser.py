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

if __name__ == "__main__":
    unittest.main()
