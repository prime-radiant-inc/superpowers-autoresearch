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

# --- mutation_events() fixtures (E3, Task 10). A "mutation" is a
# successful patch_apply_end OR a git command that changes repo state
# (commit/merge/rebase/reset/checkout) -- deliberately excludes read-only
# git commands (status/log/diff/branch) and the exec_command encoding is
# exercised on some, custom_tool_call "exec" on others, matching the two
# encodings exec_commands() already handles.
GIT_COMMIT_EXEC = L("2026-07-29T11:00:00.000Z", "response_item", {
    "type": "function_call", "id": "fc_m1", "name": "exec_command",
    "arguments": json.dumps({"cmd": "git commit -m 'wip'"}), "call_id": "call_m1"})
GIT_MERGE_EXEC = L("2026-07-29T11:00:01.000Z", "response_item", {
    "type": "function_call", "id": "fc_m2", "name": "exec_command",
    "arguments": json.dumps({"cmd": "git merge feature"}), "call_id": "call_m2"})
GIT_REBASE_EXEC = L("2026-07-29T11:00:02.000Z", "response_item", {
    "type": "function_call", "id": "fc_m3", "name": "exec_command",
    "arguments": json.dumps({"cmd": "git rebase main"}), "call_id": "call_m3"})
GIT_RESET_EXEC = L("2026-07-29T11:00:03.000Z", "response_item", {
    "type": "function_call", "id": "fc_m4", "name": "exec_command",
    "arguments": json.dumps({"cmd": "git reset --hard HEAD~1"}), "call_id": "call_m4"})
GIT_CHECKOUT_CUSTOM_EXEC = L("2026-07-29T11:00:04.000Z", "response_item", {
    "type": "custom_tool_call", "id": "fc_m5", "name": "exec",
    "input": "git checkout -b feature/x", "call_id": "call_m5"})
GIT_STATUS_EXEC = L("2026-07-29T11:00:05.000Z", "response_item", {
    "type": "function_call", "id": "fc_m6", "name": "exec_command",
    "arguments": json.dumps({"cmd": "git status"}), "call_id": "call_m6"})
GIT_LOG_EXEC = L("2026-07-29T11:00:06.000Z", "response_item", {
    "type": "function_call", "id": "fc_m7", "name": "exec_command",
    "arguments": json.dumps({"cmd": "git log --oneline -5"}), "call_id": "call_m7"})

# --- deescape_custom_exec() fixtures (E3, Task 10, fix round 1). Real bug:
# custom_tool_call/"exec" `input` is raw JS source, taken whole -- NOT
# JSON-decoded like the exec_command encoding's `arguments` (which goes
# through json.loads() upstream). A literal two-character `\n` escape
# left over from a JS string literal in that source sits as a real
# backslash followed by a literal "n" character, not an actual newline --
# so "...\\necho done\\ngit commit -m 'wip'" (Python repr) has a literal
# "n" immediately before "git", defeating any \b-anchored regex expecting
# a real word boundary there. GIT_COMMIT_ESCAPED_CUSTOM_EXEC reproduces
# this exact case: the Python string built here literally contains
# backslash+n (two chars, via the raw "\\n" in this source) right before
# "git commit".
GIT_COMMIT_ESCAPED_CUSTOM_EXEC = L("2026-07-29T11:00:07.000Z", "response_item", {
    "type": "custom_tool_call", "id": "fc_m8", "name": "exec",
    "input": "echo start\\ngit commit -m 'wip'\\necho done", "call_id": "call_m8"})

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


# --- final_answers()/inter_agent_messages() fixtures (E10, Task 14). Shapes
# copied verbatim from a real battery rollout (evals/results/
# cx-eff-cx-sdd-small-dev-rep1/.../rollout-*.jsonl): a session's own claim to
# its caller is an `event_msg/type=="agent_message"` record (`message`,
# `phase` -- "final_answer" for the session's actual conclusion, "commentary"
# for in-progress narration); a message ONE agent sent ANOTHER (what a
# controller received from a child, or vice versa) is a
# `response_item/type=="agent_message"` record with `author`/`recipient` and
# a `content` list of `{"type":"input_text"|"output_text","text":...}` items
# whose concatenated text follows a fixed envelope: "Message Type:
# X\nTask name: Y\nSender: Z\nPayload:\n<payload>".
OWN_FINAL_ANSWER = L("2026-07-28T20:13:00.000Z", "event_msg", {
    "type": "agent_message",
    "message": "Merged `feat/x` into `main`. All 14 tests pass.",
    "phase": "final_answer", "memory_citation": None})
OWN_COMMENTARY = L("2026-07-28T20:10:00.000Z", "event_msg", {
    "type": "agent_message", "message": "Starting task 1 now.",
    "phase": "commentary", "memory_citation": None})

CHILD_FINAL_ANSWER_SUBSTANTIVE = L("2026-07-28T19:59:59.000Z", "response_item", {
    "type": "agent_message", "author": "/root/task1_reviewer", "recipient": "/root",
    "content": [{"type": "input_text",
                 "text": "Message Type: FINAL_ANSWER\nTask name: /root\n"
                         "Sender: /root/task1_reviewer\nPayload:\nApproved. No issues."}],
    "internal_chat_message_metadata_passthrough": {"turn_id": "t1"}})
# The harmless real-corpus artifact this task's pre-registration flagged and
# ruled out: a zero-payload progress ping, Message Type MESSAGE (not
# FINAL_ANSWER) -- a null-result classifier keyed on raw text length alone
# would misfire on this; inter_agent_messages() must expose message_type so
# score_e10.py can filter on it correctly.
CHILD_PROGRESS_PING_EMPTY_PAYLOAD = L("2026-07-28T19:58:50.000Z", "response_item", {
    "type": "agent_message", "author": "/root/task2_reviewer", "recipient": "/root",
    "content": [{"type": "input_text",
                 "text": "Message Type: MESSAGE\nTask name: /root\n"
                         "Sender: /root/task2_reviewer\nPayload:\n"}],
    "internal_chat_message_metadata_passthrough": {"turn_id": "t2"}})
# The engineered probe (a) case: a genuine FINAL_ANSWER with an empty payload.
CHILD_FINAL_ANSWER_EMPTY_PAYLOAD = L("2026-07-28T19:59:10.000Z", "response_item", {
    "type": "agent_message", "author": "/root/task1_implementer", "recipient": "/root",
    "content": [{"type": "input_text",
                 "text": "Message Type: FINAL_ANSWER\nTask name: /root\n"
                         "Sender: /root/task1_implementer\nPayload:\n"}],
    "internal_chat_message_metadata_passthrough": {"turn_id": "t3"}})
INTER_AGENT_UNPARSEABLE = L("2026-07-28T19:59:20.000Z", "response_item", {
    "type": "agent_message", "author": "/root/x", "recipient": "/root",
    "content": [{"type": "input_text", "text": "not the expected envelope shape"}]})
INTER_AGENT_MULTI_CONTENT_ITEMS = L("2026-07-28T19:59:30.000Z", "response_item", {
    "type": "agent_message", "author": "/root/y", "recipient": "/root",
    "content": [{"type": "input_text", "text": "Message Type: FINAL_ANSWER\nTask name: /root\n"
                                                 "Sender: /root/y\nPayload:\nfirst "},
                {"type": "input_text", "text": "second"}]})


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

class TestMutationEvents(unittest.TestCase):
    """mutation_events() (E3, Task 10): timestamps of successful
    patch_apply_end events plus git commands that mutate repo state
    (commit/merge/rebase/reset/checkout) -- the duplicate-gate scorer's
    "did anything change the tree between these two identical test runs"
    signal."""

    def test_includes_successful_patch_apply_and_excludes_failure(self):
        p = write_fixture([PATCH_APPLY_SUCCESS_TWO_PATHS, PATCH_APPLY_FAILURE_EMPTY_CHANGES])
        events = rp.mutation_events(p)
        self.assertEqual(events, ["2026-07-29T10:00:00.000Z"])

    def test_includes_each_mutating_git_verb_both_encodings(self):
        p = write_fixture([GIT_COMMIT_EXEC, GIT_MERGE_EXEC, GIT_REBASE_EXEC,
                            GIT_RESET_EXEC, GIT_CHECKOUT_CUSTOM_EXEC])
        events = rp.mutation_events(p)
        self.assertEqual(events, [
            "2026-07-29T11:00:00.000Z", "2026-07-29T11:00:01.000Z",
            "2026-07-29T11:00:02.000Z", "2026-07-29T11:00:03.000Z",
            "2026-07-29T11:00:04.000Z"])

    def test_excludes_non_mutating_git_commands(self):
        p = write_fixture([GIT_STATUS_EXEC, GIT_LOG_EXEC])
        self.assertEqual(rp.mutation_events(p), [])

    def test_excludes_unrelated_exec_commands(self):
        p = write_fixture([EXEC_FC])  # "pytest -k test_thing"
        self.assertEqual(rp.mutation_events(p), [])

    def test_merges_and_sorts_both_sources_by_timestamp(self):
        # File order deliberately scrambled (git commit BEFORE the patch
        # apply in the raw file) -- mutation_events must sort by
        # timestamp, not just concatenate its two sources in file order.
        p = write_fixture([GIT_COMMIT_EXEC, PATCH_APPLY_SUCCESS_TWO_PATHS, GIT_STATUS_EXEC])
        self.assertEqual(rp.mutation_events(p),
                         ["2026-07-29T10:00:00.000Z", "2026-07-29T11:00:00.000Z"])

    def test_empty_file_returns_empty_list(self):
        p = write_fixture([NOT_A_SPAWN])
        self.assertEqual(rp.mutation_events(p), [])

    def test_custom_exec_literal_backslash_n_before_git_is_still_detected(self):
        # Fix round 1 (real bug, reviewer-verified against the MINE-tier
        # battery corpus): a custom_exec command's raw JS-source input can
        # carry an undecoded literal "\n" (two chars: backslash, n) right
        # before "git commit" -- the word char "n" sitting directly
        # before "git" defeats MUTATION_GIT_RE's leading \b, so the
        # mutation was silently dropped before this fix.
        p = write_fixture([GIT_COMMIT_ESCAPED_CUSTOM_EXEC])
        self.assertEqual(rp.mutation_events(p), ["2026-07-29T11:00:07.000Z"])

class TestDeescapeCustomExec(unittest.TestCase):
    """deescape_custom_exec() (E3, Task 10, fix round 1): decodes the
    common JS string-literal escapes (\\n \\t \\" \\\\) that a
    custom_exec command's raw, un-JSON-parsed `input` text can carry
    literally -- and ONLY for encoding=="custom_exec". The
    "exec_command" encoding is already JSON-decoded upstream by
    json.loads() (exec_commands()), so re-applying this there would
    double-unescape/corrupt already-correct text; this is an
    absolute-truth fix scoped to mutation_events()/score_e3.py's own
    matching, never applied to parse_session()'s corpus-parity counters
    (skill_reads_compat/strict, spawn_calls, wait_calls, test_commands),
    which must stay byte-parity with the audit's scan-rollouts.mjs."""

    def test_decodes_n_t_quote_backslash_for_custom_exec(self):
        # raw, as Python repr, is 'a\\nb\\tc\\"d\\\\e' -- four literal
        # two-char escape sequences: \n \t \" \\, each exactly the
        # reviewer's named set.
        raw = "a\\nb\\tc\\\"d\\\\e"
        self.assertEqual(rp.deescape_custom_exec(raw, "custom_exec"),
                         "a\nb\tc\"d\\e")

    def test_leaves_exec_command_encoding_unchanged(self):
        # Already JSON-decoded upstream -- must NOT be touched here.
        raw = "a\\nb"  # literal backslash-n, as it would appear if (hypothetically) present
        self.assertEqual(rp.deescape_custom_exec(raw, "exec_command"), raw)

    def test_leaves_other_escape_sequences_untouched(self):
        # Only \n \t \" \\ are in scope (the reviewer's explicit list) --
        # an unrelated escape like \d (a regex metacharacter some command
        # might legitimately contain) must pass through unchanged.
        raw = "grep '\\d+' file.txt"
        self.assertEqual(rp.deescape_custom_exec(raw, "custom_exec"), raw)

    def test_noop_on_text_with_no_escapes(self):
        raw = "git checkout -b feature/x"
        self.assertEqual(rp.deescape_custom_exec(raw, "custom_exec"), raw)

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

class TestFinalAnswers(unittest.TestCase):
    """final_answers() (E10, Task 14): a session's own claims to its
    caller, in file order -- both "commentary" and "final_answer" phases."""

    def test_final_answers_extracts_message_and_phase_in_order(self):
        p = write_fixture([OWN_COMMENTARY, NOT_A_SPAWN, OWN_FINAL_ANSWER])
        answers = rp.final_answers(p)
        self.assertEqual(len(answers), 2)
        self.assertEqual(answers[0].phase, "commentary")
        self.assertEqual(answers[0].message, "Starting task 1 now.")
        self.assertEqual(answers[1].phase, "final_answer")
        self.assertIn("Merged", answers[1].message)
        self.assertEqual(answers[1].timestamp, "2026-07-28T20:13:00.000Z")

    def test_final_answers_empty_when_none(self):
        p = write_fixture([NOT_A_SPAWN, CHILD_FINAL_ANSWER_SUBSTANTIVE])
        # inter-agent response_item/agent_message must NOT be picked up here
        # -- only the session's OWN event_msg/agent_message records.
        self.assertEqual(rp.final_answers(p), [])


class TestInterAgentMessages(unittest.TestCase):
    """inter_agent_messages() (E10, Task 14): every message one agent sent
    another, as recorded in THIS rollout's own transcript, parsed into the
    "Message Type: X\\nTask name: Y\\nSender: Z\\nPayload:\\n<payload>"
    envelope fields."""

    def test_parses_envelope_fields(self):
        p = write_fixture([CHILD_FINAL_ANSWER_SUBSTANTIVE])
        msgs = rp.inter_agent_messages(p)
        self.assertEqual(len(msgs), 1)
        m = msgs[0]
        self.assertEqual(m.author, "/root/task1_reviewer")
        self.assertEqual(m.recipient, "/root")
        self.assertEqual(m.message_type, "FINAL_ANSWER")
        self.assertEqual(m.task_name, "/root")
        self.assertEqual(m.sender, "/root/task1_reviewer")
        self.assertEqual(m.payload, "Approved. No issues.")
        self.assertEqual(m.timestamp, "2026-07-28T19:59:59.000Z")

    def test_distinguishes_empty_final_answer_from_empty_progress_ping(self):
        # The exact false-positive trap this task's pre-registration found
        # in the real corpus: both have an empty payload, but only the
        # FINAL_ANSWER one is a genuine null RESULT.
        p = write_fixture([CHILD_PROGRESS_PING_EMPTY_PAYLOAD, CHILD_FINAL_ANSWER_EMPTY_PAYLOAD])
        msgs = rp.inter_agent_messages(p)
        self.assertEqual(len(msgs), 2)
        ping, final = msgs
        self.assertEqual(ping.message_type, "MESSAGE")
        self.assertEqual(ping.payload, "")
        self.assertEqual(final.message_type, "FINAL_ANSWER")
        self.assertEqual(final.payload, "")

    def test_unparseable_envelope_falls_back_to_raw_text(self):
        p = write_fixture([INTER_AGENT_UNPARSEABLE])
        m = rp.inter_agent_messages(p)[0]
        self.assertEqual(m.message_type, "")
        self.assertEqual(m.payload, "not the expected envelope shape")
        self.assertEqual(m.raw_text, "not the expected envelope shape")

    def test_concatenates_multiple_content_items(self):
        p = write_fixture([INTER_AGENT_MULTI_CONTENT_ITEMS])
        m = rp.inter_agent_messages(p)[0]
        self.assertEqual(m.payload, "first second")

    def test_excludes_own_final_answer_event_msg(self):
        p = write_fixture([OWN_FINAL_ANSWER, NOT_A_SPAWN])
        self.assertEqual(rp.inter_agent_messages(p), [])

    def test_empty_when_none(self):
        p = write_fixture([NOT_A_SPAWN])
        self.assertEqual(rp.inter_agent_messages(p), [])


if __name__ == "__main__":
    unittest.main()
