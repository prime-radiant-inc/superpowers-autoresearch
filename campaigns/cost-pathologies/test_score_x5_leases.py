"""Tests for score_x5_leases.py (X5, Task 7 of the cost-pathologies SDD
plan). Synthetic rollout fixtures only, built inline via small JSONL-record
helpers -- no real session content, no committed fixture files. This
mirrors campaigns/codex-efficiency/test_score_e3.py's own test style
(the closest precedent: X5 is explicitly the "known score_e3 upgrade" per
the design doc), rather than X1/X4/X6's committed-fixture-directory style,
since X5's test matrix (chained commands, git-evidence shapes, receipt
grammar) needs many small independent variations that inline construction
keeps far more readable than a dozen tiny fixture files would.

Four layers, matching score_x5_leases.py's own structure:
  - `_extract_test_invocations()` -- pure-function substring-aware
    extraction, no files.
  - git-evidence resolution (`_git_evidence`, `_resolve_tree_sha`) via
    `lease_stats()`'s `verification_runs[i]["tree_sha"]` field.
  - `duplicate_groups` grouping semantics (same-SHA merge, cross-SHA /
    unresolved-SHA never merge).
  - `lease_events` -- the LEASE-RECEIPT/HONORED/INVALIDATED grammar this
    module's docstring defines as the SPEC for the not-yet-authored
    cp/x5a, cp/x5b arm branches (Task 11) to emit.
"""
import json
import os
import tempfile
import unittest

FIXTURES_DIR = None  # inline construction only -- see module docstring


def _rec(ts, typ, payload):
    return json.dumps({"timestamp": ts, "type": typ, "payload": payload})


def exec_cmd(ts, call_id, cmd):
    """Plain "exec_command" encoding -- JSON-decoded `cmd` string, exactly
    like a real shell invocation (no JS wrapper)."""
    return _rec(ts, "response_item", {
        "type": "function_call", "id": call_id, "name": "exec_command",
        "arguments": json.dumps({"cmd": cmd}), "call_id": call_id})


def exec_output(ts, call_id, output_text):
    """The matching function_call_output for an exec_cmd() call -- `output`
    is a bare string, per the real corpus shape (verified directly against
    a donated-session rollout during this task's corpus validation; see
    logs/2026-07-31-cost-pathologies.md's Task 7 entry)."""
    return _rec(ts, "response_item", {
        "type": "function_call_output", "call_id": call_id, "output": output_text})


def custom_exec_cmd(ts, call_id, raw_input):
    """custom_tool_call/"exec" encoding -- `input` is raw JS source, taken
    WHOLE (see rollout_parser.exec_commands()'s docstring)."""
    return _rec(ts, "response_item", {
        "type": "custom_tool_call", "id": call_id, "name": "exec",
        "input": raw_input, "call_id": call_id})


def custom_exec_output(ts, call_id, text):
    """The matching custom_tool_call_output -- `output` is a LIST of
    content dicts (real corpus shape, verified directly against a donated
    session's rollout during this task's corpus validation)."""
    return _rec(ts, "response_item", {
        "type": "custom_tool_call_output", "call_id": call_id,
        "output": [{"type": "input_text", "text": text}]})


def final_answer(ts, message, phase="final_answer"):
    return _rec(ts, "event_msg", {"type": "agent_message", "message": message, "phase": phase})


def inter_agent_message(ts, text, author="/root/task1", recipient="/root"):
    return _rec(ts, "response_item", {
        "type": "agent_message", "author": author, "recipient": recipient,
        "content": [{"type": "output_text", "text": text}]})


def write_rollout(tmpdir, name, lines):
    path = os.path.join(tmpdir, name)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


class TestExtractTestInvocations(unittest.TestCase):
    """Pure-function tests -- no files."""

    def test_bare_invocation_unchanged(self):
        import score_x5_leases as sx5
        self.assertEqual(sx5._extract_test_invocations("pytest tests/"), ["pytest tests/"])

    def test_cd_chained_prefix_normalizes_to_bare(self):
        # The brief's own example: "cd x && pytest ..." must normalize
        # identically to bare "pytest ...".
        import score_x5_leases as sx5
        self.assertEqual(sx5._extract_test_invocations("cd x && pytest tests/"), ["pytest tests/"])

    def test_trailing_chained_command_normalizes_to_bare(self):
        # The brief's other example: "npm test && echo done".
        import score_x5_leases as sx5
        self.assertEqual(sx5._extract_test_invocations("npm test && echo done"), ["npm test"])

    def test_semicolon_and_newline_are_also_terminators(self):
        import score_x5_leases as sx5
        self.assertEqual(sx5._extract_test_invocations("pytest tests/; echo done"), ["pytest tests/"])
        self.assertEqual(sx5._extract_test_invocations("pytest tests/\necho done"), ["pytest tests/"])

    def test_two_invocations_in_one_command_both_captured(self):
        import score_x5_leases as sx5
        self.assertEqual(
            sx5._extract_test_invocations("pytest tests/a.py && pytest tests/b.py"),
            ["pytest tests/a.py", "pytest tests/b.py"])

    def test_js_wrapped_custom_exec_trailing_artifact_stripped(self):
        # Real corpus shape (donated-session validation): a custom_exec
        # JS object literal wraps the shell command in a quoted "cmd"
        # field; the extraction must not leak the trailing JS punctuation
        # (closing quote/comma/newline) into command_norm.
        import score_x5_leases as sx5
        js = ('const r = await tools.exec_command({\n  cmd: "cargo test --all-features --quiet",\n'
              '  workdir: "/work/repo",\n  yield_time_ms: 30000,\n'
              '  max_output_tokens: 30000\n});\ntext(JSON.stringify(r));')
        self.assertEqual(sx5._extract_test_invocations(js), ["cargo test --all-features --quiet"])

    def test_single_line_json_wrapped_field_boundary_stripped(self):
        # Real corpus shape (donated-session validation, fix round 1): a
        # ONE-LINE custom_exec call has no newline between the quoted
        # "cmd" value and the next JSON/JS field -- only a comma. Neither
        # a chain terminator nor the plain trailing-punctuation cleanup
        # catches this on its own; the field-boundary must be recognized
        # explicitly.
        import score_x5_leases as sx5
        cmd = ('{"cmd":"cargo test --test widget_provider widget_schema_v2 -- --nocapture",'
               '"workdir":"/work/repo/.worktrees/widget-impl",'
               '"yield_time_ms":30000,"max_output_tokens":30000}')
        self.assertEqual(
            sx5._extract_test_invocations(cmd),
            ["cargo test --test widget_provider widget_schema_v2 -- --nocapture"])

    def test_single_line_js_shorthand_field_boundary_stripped(self):
        # Same real shape but with JS object-literal shorthand keys (no
        # quotes around the key name) and a space instead of a comma-only
        # separator.
        import score_x5_leases as sx5
        cmd = 'tools.exec_command({cmd: "npm test", workdir: "/work/repo", yield_time_ms: 30000})'
        self.assertEqual(sx5._extract_test_invocations(cmd), ["npm test"])

    def test_shell_regex_parens_and_single_quotes_survive_custom_exec_stripping(self):
        # Real corpus shape (donated-session validation, fix round 3): a
        # `go test -run '<regex>'` argument routinely closes with a
        # legitimate `)'` (regex group close, then the shell's own single
        # quote) -- the OLD blanket trailing-character-class stripper
        # corrupted this (it treated `)` and `'` as JS-wrapper noise and
        # cut the argument in half). Only a LITERAL trailing double-quote
        # marks a real JS-wrapper boundary; single quotes and parens that
        # are part of the shell command's own syntax must never be
        # stripped.
        import score_x5_leases as sx5
        js = ('const r = await tools.exec_command({"cmd":"gofmt -w x_test.go && '
              'go test ./widget -run \'Test(FooSelector|BarResolver)\'",'
              '"workdir":"/work/repo","yield_time_ms":1000,"max_output_tokens":12000});\n'
              'text(JSON.stringify(r));\n')
        self.assertEqual(
            sx5._extract_test_invocations(js, encoding="custom_exec"),
            ["go test ./widget -run 'Test(FooSelector|BarResolver)'"])

    def test_exec_command_encoding_never_strips_a_legitimate_trailing_quote(self):
        # The plain "exec_command" JSON encoding is ALREADY the fully
        # decoded, real shell command text (no JS wrapper at all) -- the
        # custom_exec-only trailing-artifact cleanup must never run on it,
        # or a genuinely double-quoted final argument would be corrupted.
        import score_x5_leases as sx5
        self.assertEqual(
            sx5._extract_test_invocations('pytest -k "test_foo"', encoding="exec_command"),
            ['pytest -k "test_foo"'])

    def test_non_test_command_yields_nothing(self):
        import score_x5_leases as sx5
        self.assertEqual(sx5._extract_test_invocations("git status"), [])
        self.assertEqual(sx5._extract_test_invocations("ls tests/"), [])

    def test_whitespace_collapsed_within_segment(self):
        import score_x5_leases as sx5
        self.assertEqual(sx5._extract_test_invocations("pytest   tests/a.py   -v"), ["pytest tests/a.py -v"])


class TestGitEvidenceResolution(unittest.TestCase):
    """Tests git-evidence extraction indirectly, via lease_stats()'s
    verification_runs[i]["tree_sha"] -- the module's own internal
    representation of evidence events is not part of the public
    interface."""

    def _single_run(self, evidence_lines, run_ts, cmd="pytest tests/"):
        with tempfile.TemporaryDirectory() as tmp:
            lines = list(evidence_lines) + [exec_cmd(run_ts, "run1", cmd)]
            path = write_rollout(tmp, "a.jsonl", lines)
            import score_x5_leases as sx5
            result = sx5.lease_stats([path])
        return result["verification_runs"]

    def test_no_evidence_at_all_gives_null_tree_sha(self):
        runs = self._single_run([], "2026-07-31T05:00:00.000Z")
        self.assertEqual(len(runs), 1)
        self.assertIsNone(runs[0]["tree_sha"])

    def test_commit_evidence_resolves_sha_from_bracket_output(self):
        runs = self._single_run([
            exec_cmd("2026-07-31T05:00:00.000Z", "c1", "git commit -m 'wip'"),
            exec_output("2026-07-31T05:00:00.500Z", "c1",
                        "[main 1a2b3c4] wip\n 1 file changed, 1 insertion(+)"),
        ], "2026-07-31T05:01:00.000Z")
        self.assertEqual(runs[0]["tree_sha"], "1a2b3c4")

    def test_commit_evidence_with_root_commit_parenthetical(self):
        runs = self._single_run([
            exec_cmd("2026-07-31T05:00:00.000Z", "c1", "git commit -m 'initial'"),
            exec_output("2026-07-31T05:00:00.500Z", "c1", "[main (root-commit) 0abc123] initial"),
        ], "2026-07-31T05:01:00.000Z")
        self.assertEqual(runs[0]["tree_sha"], "0abc123")

    def test_commit_evidence_skips_unrelated_earlier_brackets(self):
        # Real corpus shape (donated-session validation, fix round 2): a
        # pre-commit hook runs `cargo build` first, whose own output
        # contains an EARLIER, unrelated bracket ("Finished `dev` profile
        # [unoptimized + debuginfo] target(s)...") before git's own
        # "[<branch> <sha>] <subject>" commit-summary line. The FIRST
        # bracket in the text is not necessarily the commit's own.
        runs = self._single_run([
            exec_cmd("2026-07-31T05:00:00.000Z", "c1", "git commit -m 'wip'"),
            exec_output("2026-07-31T05:00:00.500Z", "c1",
                        "Finished `dev` profile [unoptimized + debuginfo] target(s) in 3.38s\n"
                        "[my-branch 115f916] fix: sanitize widget labels\n"
                        " 2 files changed, 134 insertions(+), 8 deletions(-)\n"),
        ], "2026-07-31T05:01:00.000Z")
        self.assertEqual(runs[0]["tree_sha"], "115f916")

    def test_checkout_bare_sha_resolves_from_command_text(self):
        sha = "3f619c6f504f148dd116d73651c2b361f664164f"
        runs = self._single_run([
            exec_cmd("2026-07-31T05:00:00.000Z", "c1", f"git checkout {sha}"),
        ], "2026-07-31T05:01:00.000Z")
        self.assertEqual(runs[0]["tree_sha"], sha)

    def test_checkout_branch_name_is_evidence_but_unresolved(self):
        runs = self._single_run([
            exec_cmd("2026-07-31T05:00:00.000Z", "c1", "git checkout main"),
        ], "2026-07-31T05:01:00.000Z")
        self.assertIsNone(runs[0]["tree_sha"])

    def test_revparse_head_resolves_from_output(self):
        sha = "3f619c6f504f148dd116d73651c2b361f664164f"
        runs = self._single_run([
            exec_cmd("2026-07-31T05:00:00.000Z", "c1", "git rev-parse HEAD"),
            exec_output("2026-07-31T05:00:00.500Z", "c1", sha + "\n"),
        ], "2026-07-31T05:01:00.000Z")
        self.assertEqual(runs[0]["tree_sha"], sha)

    def test_non_git_command_is_not_evidence(self):
        runs = self._single_run([
            exec_cmd("2026-07-31T05:00:00.000Z", "c1", "echo hello"),
        ], "2026-07-31T05:01:00.000Z")
        self.assertIsNone(runs[0]["tree_sha"])

    def test_nearest_evidence_wins_even_if_unresolved(self):
        # An OLDER commit resolved a real SHA; a NEWER checkout-to-a-
        # branch-name is unresolved. The nearest-preceding rule must pick
        # the newer (unresolved) evidence, not fall back to the older
        # resolved one -- we genuinely don't know the tree state once an
        # unresolvable mutation happened after a resolved one.
        runs = self._single_run([
            exec_cmd("2026-07-31T05:00:00.000Z", "c1", "git commit -m 'wip'"),
            exec_output("2026-07-31T05:00:00.500Z", "c1", "[main abc1234] wip"),
            exec_cmd("2026-07-31T05:05:00.000Z", "c2", "git checkout main"),
        ], "2026-07-31T05:10:00.000Z")
        self.assertIsNone(runs[0]["tree_sha"])

    def test_evidence_across_multiple_rollout_files(self):
        # Commit evidence lives in one rollout (an implementer's own
        # session); the verification run lives in a DIFFERENT rollout (a
        # reviewer's) -- the duplicate-gate question spans sessions, same
        # as score_e3's mutation_timeline().
        with tempfile.TemporaryDirectory() as tmp:
            impl = write_rollout(tmp, "impl.jsonl", [
                exec_cmd("2026-07-31T05:00:00.000Z", "c1", "git commit -m 'wip'"),
                exec_output("2026-07-31T05:00:00.500Z", "c1", "[main abc1234] wip"),
            ])
            reviewer = write_rollout(tmp, "reviewer.jsonl", [
                exec_cmd("2026-07-31T05:05:00.000Z", "r1", "pytest tests/"),
            ])
            import score_x5_leases as sx5
            result = sx5.lease_stats([impl, reviewer])
        runs = [r for r in result["verification_runs"] if r["command_norm"] == "pytest tests/"]
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]["tree_sha"], "abc1234")
        self.assertEqual(runs[0]["session_id"], "reviewer.jsonl")


class TestDuplicateGroups(unittest.TestCase):
    def test_same_command_same_sha_is_duplicate_group(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = write_rollout(tmp, "a.jsonl", [
                exec_cmd("2026-07-31T05:00:00.000Z", "c1", "git commit -m 'wip'"),
                exec_output("2026-07-31T05:00:00.500Z", "c1", "[main abc1234] wip"),
                exec_cmd("2026-07-31T05:01:00.000Z", "r1", "pytest tests/"),
            ])
            b = write_rollout(tmp, "b.jsonl", [
                exec_cmd("2026-07-31T05:02:00.000Z", "r2", "pytest tests/"),
            ])
            import score_x5_leases as sx5
            result = sx5.lease_stats([a, b])
        groups = result["duplicate_groups"]
        self.assertEqual(len(groups), 1)
        g = groups[0]
        self.assertEqual(g["command_norm"], "pytest tests/")
        self.assertEqual(g["tree_sha"], "abc1234")
        self.assertEqual(g["count"], 2)
        self.assertEqual(g["sessions"], ["a.jsonl", "b.jsonl"])

    def test_same_command_different_sha_not_merged(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_rollout(tmp, "a.jsonl", [
                exec_cmd("2026-07-31T05:00:00.000Z", "c1", "git commit -m 'wip'"),
                exec_output("2026-07-31T05:00:00.500Z", "c1", "[main abc1234] wip"),
                exec_cmd("2026-07-31T05:01:00.000Z", "r1", "pytest tests/"),
                exec_cmd("2026-07-31T05:02:00.000Z", "c2", "git commit -m 'fix'"),
                exec_output("2026-07-31T05:02:00.500Z", "c2", "[main def5678] fix"),
                exec_cmd("2026-07-31T05:03:00.000Z", "r2", "pytest tests/"),
            ])
            import score_x5_leases as sx5
            result = sx5.lease_stats([path])
        self.assertEqual(result["duplicate_groups"], [])
        shas = [r["tree_sha"] for r in result["verification_runs"] if r["command_norm"] == "pytest tests/"]
        self.assertEqual(shas, ["abc1234", "def5678"])

    def test_null_sha_occurrences_never_merged_into_a_group(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_rollout(tmp, "a.jsonl", [
                exec_cmd("2026-07-31T05:00:00.000Z", "r1", "pytest tests/"),
                exec_cmd("2026-07-31T05:01:00.000Z", "r2", "pytest tests/"),
            ])
            import score_x5_leases as sx5
            result = sx5.lease_stats([path])
        self.assertEqual(result["duplicate_groups"], [])
        self.assertTrue(all(r["tree_sha"] is None for r in result["verification_runs"]))

    def test_twelve_occurrences_same_sha_one_group_count_twelve(self):
        with tempfile.TemporaryDirectory() as tmp:
            lines = [
                exec_cmd("2026-07-31T05:00:00.000Z", "c1", "git commit -m 'wip'"),
                exec_output("2026-07-31T05:00:00.500Z", "c1", "[main abc1234] wip"),
            ]
            for i in range(1, 13):
                lines.append(exec_cmd(f"2026-07-31T05:{i:02d}:00.000Z", f"r{i}", "go test ./..."))
            path = write_rollout(tmp, "a.jsonl", lines)
            import score_x5_leases as sx5
            result = sx5.lease_stats([path])
        groups = [g for g in result["duplicate_groups"] if g["command_norm"] == "go test ./..."]
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["count"], 12)


class TestLeaseEvents(unittest.TestCase):
    """LEASE-RECEIPT / LEASE-HONORED / LEASE-INVALIDATED -- the receipt-line
    grammar this module's docstring defines as the SPEC for the
    not-yet-authored cp/x5a / cp/x5b arm branches (Task 11) to emit. These
    tests are the grammar's own executable definition; there is no real
    corpus to validate them against yet (see this task's corpus-validation
    log entry -- receipts_issued/honored/invalidation_reruns legitimately
    read 0 on any pre-arm session)."""

    def _stats(self, lines):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_rollout(tmp, "a.jsonl", lines)
            import score_x5_leases as sx5
            return sx5.lease_stats([path])

    # NOTE: `lease_events`'s dict shape now always carries the Task 2
    # prose-detector fields (`receipts_honored_prose`/
    # `invalidation_reruns_prose`) alongside the strict-grammar three --
    # see TestLeaseEventsDistinctCounting/TestLeaseEventsProseDetector
    # below. None of the fixtures in THIS class contain any prose-honoring
    # language, so every assertion here expects both new fields at 0;
    # that they stay 0 is itself part of what these tests check (the
    # strict-line text is masked out of prose scanning -- see
    # test_strict_matched_line_never_also_counted_as_prose below).
    _ZERO_PROSE = {"receipts_honored_prose": 0, "invalidation_reruns_prose": 0}

    def test_receipt_line_counted(self):
        result = self._stats([
            final_answer("2026-07-31T05:00:00.000Z",
                          "LEASE-RECEIPT: command=pytest tests/ tree_sha=abc1234 result=pass"),
        ])
        self.assertEqual(result["lease_events"],
                          {"receipts_issued": 1, "receipts_honored": 0, "invalidation_reruns": 0,
                           **self._ZERO_PROSE})

    def test_honored_line_counted(self):
        result = self._stats([
            final_answer("2026-07-31T05:00:00.000Z",
                          "LEASE-HONORED: command=pytest tests/ tree_sha=abc1234"),
        ])
        self.assertEqual(result["lease_events"],
                          {"receipts_issued": 0, "receipts_honored": 1, "invalidation_reruns": 0,
                           **self._ZERO_PROSE})

    def test_invalidated_line_counted(self):
        result = self._stats([
            final_answer("2026-07-31T05:00:00.000Z",
                          "LEASE-INVALIDATED: command=pytest tests/ tree_sha=def5678"),
        ])
        self.assertEqual(result["lease_events"],
                          {"receipts_issued": 0, "receipts_honored": 0, "invalidation_reruns": 1,
                           **self._ZERO_PROSE})

    def test_multiple_lines_one_message(self):
        text = ("Verification receipts:\n"
                "LEASE-RECEIPT: command=pytest tests/test_a.py tree_sha=abc1234 result=pass\n"
                "LEASE-RECEIPT: command=pytest tests/test_b.py tree_sha=abc1234 result=pass\n"
                "LEASE-HONORED: command=pytest tests/ tree_sha=abc1234\n")
        result = self._stats([final_answer("2026-07-31T05:00:00.000Z", text)])
        self.assertEqual(result["lease_events"],
                          {"receipts_issued": 2, "receipts_honored": 1, "invalidation_reruns": 0,
                           **self._ZERO_PROSE})

    def test_lines_scanned_across_final_answer_inter_agent_and_exec_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            lines = [
                final_answer("2026-07-31T05:00:00.000Z",
                              "LEASE-RECEIPT: command=pytest tests/ tree_sha=abc1234 result=pass"),
                inter_agent_message("2026-07-31T05:01:00.000Z",
                                     "LEASE-HONORED: command=pytest tests/ tree_sha=abc1234"),
                exec_cmd("2026-07-31T05:02:00.000Z", "c1", "cat lease-receipts.txt"),
                exec_output("2026-07-31T05:02:00.500Z", "c1",
                            "LEASE-INVALIDATED: command=pytest tests/ tree_sha=def5678"),
            ]
            path = write_rollout(tmp, "a.jsonl", lines)
            import score_x5_leases as sx5
            result = sx5.lease_stats([path])
        self.assertEqual(result["lease_events"],
                          {"receipts_issued": 1, "receipts_honored": 1, "invalidation_reruns": 1,
                           **self._ZERO_PROSE})

    def test_malformed_lines_ignored(self):
        result = self._stats([
            final_answer("2026-07-31T05:00:00.000Z", "LEASE-RECEIPT: nonsense, no fields here"),
            final_answer("2026-07-31T05:01:00.000Z",
                          "lease-receipt: command=pytest tests/ tree_sha=abc1234 result=pass"),
        ])
        self.assertEqual(result["lease_events"],
                          {"receipts_issued": 0, "receipts_honored": 0, "invalidation_reruns": 0,
                           **self._ZERO_PROSE})

    def test_no_lines_zero_everything(self):
        result = self._stats([
            final_answer("2026-07-31T05:00:00.000Z", "All tests pass, nothing else to report."),
        ])
        self.assertEqual(result["lease_events"],
                          {"receipts_issued": 0, "receipts_honored": 0, "invalidation_reruns": 0,
                           **self._ZERO_PROSE})


class TestLeaseEventsDistinctCounting(unittest.TestCase):
    """Task 2 (queue-campaign) item 10: `lease_events` counts DISTINCT
    (kind, command_norm, tree_sha) events, not raw marker-line regex
    occurrences. Root-caused by this campaign's own C1/I2 correction
    (logs/2026-07-31-cost-pathologies.md, 2026-08-01 entry): a real X5-B
    rep (x5b-rep3) whose append-only receipts file gets read back by every
    later `cat`/apply_patch-diff view shows 10 raw `LEASE-RECEIPT` regex
    matches collapsing to only 4 distinct tree_sha values once
    deduplicated -- each earlier receipt gets re-matched at every later
    read of the same or a newer file state. The other, opposite failure
    mode named in that same correction: a marker written via an exec CALL
    (not merely its matching output) that is never read back afterward was
    invisible under the OLD `_text_sources()`, which scanned only exec
    OUTPUT text."""

    def _stats(self, lines):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_rollout(tmp, "a.jsonl", lines)
            import score_x5_leases as sx5
            return sx5.lease_stats([path])

    def test_rereading_the_same_receipt_twice_counts_once(self):
        # Two separate `cat receipts.txt` calls returning the IDENTICAL
        # LEASE-RECEIPT line -- the real re-read-inflation mechanism the
        # I2 correction root-caused.
        line = "LEASE-RECEIPT: command=pytest tests/ tree_sha=abc1234 result=pass"
        result = self._stats([
            exec_cmd("2026-07-31T05:00:00.000Z", "c1", "cat receipts.txt"),
            exec_output("2026-07-31T05:00:00.500Z", "c1", line),
            exec_cmd("2026-07-31T05:01:00.000Z", "c2", "cat receipts.txt"),
            exec_output("2026-07-31T05:01:00.500Z", "c2", line),
        ])
        self.assertEqual(result["lease_events"]["receipts_issued"], 1)

    def test_same_command_different_tree_sha_receipts_both_count(self):
        # Regression against OVER-dedup: two receipts for the SAME command
        # at two DIFFERENT tree_sha values are genuinely distinct
        # verification events (a real re-run after the tree changed), not
        # re-reads of one event -- must not collapse to 1.
        result = self._stats([
            final_answer("2026-07-31T05:00:00.000Z",
                          "LEASE-RECEIPT: command=pytest tests/ tree_sha=abc1234 result=pass"),
            final_answer("2026-07-31T05:01:00.000Z",
                          "LEASE-RECEIPT: command=pytest tests/ tree_sha=def5678 result=pass"),
        ])
        self.assertEqual(result["lease_events"]["receipts_issued"], 2)

    def test_dedup_key_includes_kind_not_just_command_and_sha(self):
        # A RECEIPT and a HONORED line sharing the identical command_norm/
        # tree_sha are two DIFFERENT kinds of event (one issues, the other
        # honors) -- must not collapse into a single dedup bucket.
        result = self._stats([
            final_answer("2026-07-31T05:00:00.000Z",
                          "LEASE-RECEIPT: command=pytest tests/ tree_sha=abc1234 result=pass"),
            final_answer("2026-07-31T05:01:00.000Z",
                          "LEASE-HONORED: command=pytest tests/ tree_sha=abc1234"),
        ])
        events = result["lease_events"]
        self.assertEqual((events["receipts_issued"], events["receipts_honored"]), (1, 1))

    def test_dedup_is_global_across_rollout_paths(self):
        # The SAME event relayed into two different sessions' transcripts
        # (e.g. an implementer's own report AND a reviewer's relayed view
        # of it) must still collapse to one distinct event -- dedup can't
        # be scoped per-path.
        line = "LEASE-RECEIPT: command=pytest tests/ tree_sha=abc1234 result=pass"
        with tempfile.TemporaryDirectory() as tmp:
            a = write_rollout(tmp, "a.jsonl", [final_answer("2026-07-31T05:00:00.000Z", line)])
            b = write_rollout(tmp, "b.jsonl", [final_answer("2026-07-31T05:01:00.000Z", line)])
            import score_x5_leases as sx5
            result = sx5.lease_stats([a, b])
        self.assertEqual(result["lease_events"]["receipts_issued"], 1)

    def test_exec_call_command_text_scanned_for_a_marker_never_read_back(self):
        # A marker WRITTEN via an exec CALL (a heredoc append, here) whose
        # content is never subsequently read back by any later `cat`/
        # output must still be counted -- the OLD _text_sources() only
        # scanned exec OUTPUT text, never the CALL's own command text, so
        # this write was silently invisible before the fix.
        cmd = ("cat <<'EOF' >> receipts.txt\n"
               "LEASE-HONORED: command=pytest tests/ tree_sha=abc1234\n"
               "EOF")
        result = self._stats([
            exec_cmd("2026-07-31T05:00:00.000Z", "c1", cmd),
        ])
        self.assertEqual(result["lease_events"]["receipts_honored"], 1)

    def test_apply_patch_diff_prefixed_lease_line_recovered_from_command_text(self):
        # Real corpus shape (cp-x5-leases-x5b-rep3, rollout
        # rollout-2026-08-01T18-59-09-019fbeb1-c4a3-7ee3-beae-b2d639d1dfee
        # .jsonl, .../home/.codex/sessions/2026/08/01/): X5-B's
        # machine-checkable receipts file is written entirely via
        # `apply_patch` unified-diff hunks -- every line in an Add/Update
        # File hunk carries a leading +/-/space diff marker, so a written
        # LEASE- line ("+LEASE-RECEIPT: command=... tree_sha=...") never
        # satisfies the strict grammar's line-start anchor even once exec
        # CALL text is scanned, unless that leading diff marker is
        # stripped first. Confirmed directly in the raw rollout during
        # this task's corpus validation -- this exact receipts file is
        # never read back via a plain `cat` in this rep, so without
        # diff-marker stripping this write is invisible to any scanner.
        js = ('const patch = "*** Begin Patch\n'
              '*** Add File: /work/.superpowers/sdd/plan/task-1-receipts.md\n'
              '+LEASE-RECEIPT: command=PYTHONPATH=. .venv/bin/pytest tests/test_token_bucket.py -q '
              'tree_sha=6502982d9ec22bc0eba1d85575a4f62dc5744523 result=pass\n'
              '*** End Patch";\n'
              'text(await tools.apply_patch(patch));')
        result = self._stats([
            custom_exec_cmd("2026-08-01T18:59:09.000Z", "c1", js),
        ])
        self.assertEqual(result["lease_events"]["receipts_issued"], 1)


class TestLeaseEventsProseDetector(unittest.TestCase):
    """Task 2 (queue-campaign) item 9: a prose-aware honor/invalidate
    detector, ALONGSIDE (never replacing) the strict LEASE-HONORED:/
    LEASE-INVALIDATED: grammar -- reported as separate
    `receipts_honored_prose`/`invalidation_reruns_prose` fields, never
    folded into the strict counts.

    Positive corpus: this campaign's own C1 correction
    (logs/2026-07-31-cost-pathologies.md, 2026-08-01 entry, "X5-A's
    honoring/invalidation mechanism IS observable in plaintext") found
    "8 messages across 3/3 [x5a] reps discuss the supplied lease receipt
    in prose and act on it" -- none of which reproduce the strict marker
    syntax, because codex reviewers here narrate the honor/decline
    decision in their own words. Only 5 of the 8 are quoted verbatim in
    that log entry; this task re-scanned the raw x5a-rep{1,2,3} rollouts
    directly (`cp-x5-leases-x5a-rep{1,2,3}`, under
    .../home/.codex/sessions/2026/08/01/) and located all 8. 7 of the 8
    are unambiguous enough for a conservative, high-precision detector to
    catch (cases A-G below); the 8th is a citation with no explicit
    rerun-or-not statement and is a deliberate, disclosed recall miss
    (test_ambiguous_receipt_citation_without_explicit_rerun_language_
    not_counted below) -- see the module docstring and this task's
    report for the precision/recall tradeoff.
    """

    def _prose(self, lines):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_rollout(tmp, "a.jsonl", lines)
            import score_x5_leases as sx5
            events = sx5.lease_stats([path])["lease_events"]
        return events["receipts_honored_prose"], events["invalidation_reruns_prose"]

    # --- positive corpus: 7 of the 8 real X5-A reviewer exchanges ---------

    def test_corpus_A_rep1_task1_review_declining_is_invalidation(self):
        # cp-x5-leases-x5a-rep1, rollout-2026-08-01T17-07-03-019fbe4b-...
        # .jsonl (task1_review) -- declines the receipt, reruns instead.
        text = ("⚠️ The implementation report’s lease receipt does not certify the "
                "stated commit, as noted in the task prompt; independent focused "
                "verification was run.")
        honored, invalidated = self._prose([final_answer("2026-08-01T17:07:03.000Z", text)])
        self.assertEqual((honored, invalidated), (0, 1))

    def test_corpus_B_rep1_task2_review_honoring(self):
        # cp-x5-leases-x5a-rep1, rollout-2026-08-01T17-11-25-019fbe4f-...
        # .jsonl (task2_review)
        text = ("⚠️ Full-suite verification was not rerun per review constraints; "
                "the provided lease receipt reports `4 passed`.")
        honored, invalidated = self._prose([final_answer("2026-08-01T17:11:25.000Z", text)])
        self.assertEqual((honored, invalidated), (1, 0))

    def test_corpus_C_rep2_task2_review_honoring(self):
        # cp-x5-leases-x5a-rep2, rollout-2026-08-01T17-36-18-019fbe65-...
        # .jsonl (task2_reviewer)
        text = ("Cannot independently verify the report’s historical TDD/output claims; "
                "per instruction, I did not rerun the suite. The supplied verification "
                "receipt matches the stated HEAD.")
        honored, invalidated = self._prose([final_answer("2026-08-01T17:36:18.000Z", text)])
        self.assertEqual((honored, invalidated), (1, 0))

    def test_corpus_D_rep2_task3_review_honoring(self):
        # cp-x5-leases-x5a-rep2, rollout-2026-08-01T17-40-09-019fbe69-...
        # .jsonl (task3_reviewer)
        text = ("Cannot independently verify the report’s claimed RED/GREEN history or "
                "full-suite output without rerunning tests; per the supplied lease "
                "receipt, `pytest tests/` passed at the reviewed HEAD `865c13f`.")
        honored, invalidated = self._prose([final_answer("2026-08-01T17:40:09.000Z", text)])
        self.assertEqual((honored, invalidated), (1, 0))

    def test_corpus_E_rep2_final_review_honoring_literal_honored_the_lease(self):
        # cp-x5-leases-x5a-rep2, rollout-2026-08-01T17-41-13-019fbe6a-...
        # .jsonl (final review) -- not quoted in the log's own 5 examples;
        # found by this task's own re-scan.
        text = ("The supplied HEAD receipt reports all three tests passing; I honored "
                "the lease and did not rerun solely for confirmation.")
        honored, invalidated = self._prose([final_answer("2026-08-01T17:41:13.000Z", text)])
        self.assertEqual((honored, invalidated), (1, 0))

    def test_corpus_F_rep3_task1_review_honoring(self):
        # cp-x5-leases-x5a-rep3, rollout-2026-08-01T17-58-43-019fbe7a-...
        # .jsonl (task1 review) -- not quoted in the log's own 5 examples;
        # found by this task's own re-scan.
        text = ("⚠️ Verification was not rerun per instruction; the supplied lease "
                "receipt reports the exact test command passed at the reviewed HEAD.")
        honored, invalidated = self._prose([final_answer("2026-08-01T17:58:43.000Z", text)])
        self.assertEqual((honored, invalidated), (1, 0))

    def test_corpus_G_rep3_task3_review_honoring_literal_LEASE_HONORED_in_prose(self):
        # cp-x5-leases-x5a-rep3, rollout-2026-08-01T18-04-14-019fbe7f-...
        # .jsonl (task3_review) -- the literal word "LEASE-HONORED"
        # embedded mid-sentence, NOT as a line-anchored strict marker (no
        # colon, no command=/tree_sha= fields on the same line) -- must be
        # caught by the prose detector, not the strict one.
        text = ("- Reviewed HEAD matches required "
                "`6e49b665a5b5b06899befaa94987148550dba683`; supplied LEASE-HONORED "
                "evidence records `../../.venv/bin/python -m pytest tests/` passing at "
                "that SHA.")
        honored, invalidated = self._prose([final_answer("2026-08-01T18:04:14.000Z", text)])
        self.assertEqual((honored, invalidated), (1, 0))

    # --- precision: conservative misses and non-matches -------------------

    def test_ambiguous_receipt_citation_without_explicit_rerun_language_not_counted(self):
        # cp-x5-leases-x5a-rep3, rollout-2026-08-01T18-05-07-019fbe80-...
        # .jsonl -- cites "the supplied HEAD receipt records the full
        # suite passing" as one of several observations supporting merge
        # readiness, but never states whether the reviewer reran tests or
        # relied on the receipt instead. This is the log's 8th real
        # exchange; a conservative, high-precision detector correctly
        # does NOT credit it (disclosed recall miss, not a bug) since it
        # lacks the explicit "not rerun"/"honored"/"without rerunning"
        # signal every genuine positive case above carries.
        text = ("Ready to merge: **Yes.** The branch aligns with REQ-1 through REQ-3 and "
                "the supplied HEAD receipt records the full suite passing; the sole "
                "finding is a non-blocking test-strengthening opportunity around "
                "failed-take atomicity.")
        honored, invalidated = self._prose([final_answer("2026-08-01T18:05:07.000Z", text)])
        self.assertEqual((honored, invalidated), (0, 0))

    def test_receipt_mentioned_as_a_recommendation_not_a_live_decision_not_counted(self):
        # cp-x5-leases-x5a-rep1, rollout-2026-08-01T17-14-52-019fbe52-...
        # .jsonl -- recommends retaining a future verification receipt (no
        # receipt existed yet in this rep; the report was missing) --
        # not a decision about an EXISTING receipt, must not match.
        text = ("Add `task-report.md` summarizing the implementation and full-suite "
                "result. Because that changes HEAD, rerun `pytest tests/` at the "
                "resulting final commit and retain an exact-head verification receipt.")
        honored, invalidated = self._prose([final_answer("2026-08-01T17:14:52.000Z", text)])
        self.assertEqual((honored, invalidated), (0, 0))

    def test_grammar_spec_quoted_in_plan_dispatch_text_not_counted(self):
        # cp-x5-leases-x5a-rep1, rollout-2026-08-01T17-02-28-019fbe46-...
        # .jsonl (the root SDD-plan dispatch, read back by every seat in
        # every one of this task's 6 x5a/x5b reps): the X5-A/X5-B plan's
        # OWN dispatch instructions quote the LEASE- grammar verbatim as a
        # worked example, using literal "<the command>"/"<the sha>"
        # placeholder tokens rather than real values -- e.g. "backticks):
        # `LEASE-HONORED: command=<the command> tree_sha=<the sha>`. A".
        # This is a real corpus-validated false-positive class found
        # during this task's full-corpus precision check: without a
        # template guard, this identical boilerplate line false-triggers
        # the phrase heuristic on EVERY rep of BOTH arms (same plan file,
        # read repeatedly), since it literally contains the LEASE-HONORED/
        # LEASE-INVALIDATED tokens. A literal "<" where a real command or
        # tree_sha value would be is the reliable, conservative signal
        # that a line is quoting the SPEC, not reporting a live decision.
        honored_text = "backticks): `LEASE-HONORED: command=<the command> tree_sha=<the sha>`. A"
        invalidated_text = "`LEASE-INVALIDATED: command=<the command> tree_sha=<the current sha>`"
        honored, invalidated = self._prose([
            final_answer("2026-08-01T17:02:28.000Z", honored_text),
            final_answer("2026-08-01T17:02:28.500Z", invalidated_text),
        ])
        self.assertEqual((honored, invalidated), (0, 0))

    def test_please_does_not_false_positive_on_lease_substring(self):
        # "please" contains the literal substring "lease" -- a naive
        # substring search (this task's own first-draft mining script hit
        # this exact bug) must not treat it as a lease/receipt mention.
        text = "Please rerun the suite before merging; nothing was honored here."
        honored, invalidated = self._prose([final_answer("2026-08-01T05:00:00.000Z", text)])
        self.assertEqual((honored, invalidated), (0, 0))

    def test_release_does_not_false_positive_on_lease_substring(self):
        text = "This change is ready for the next release; verification was not rerun."
        honored, invalidated = self._prose([final_answer("2026-08-01T05:00:00.000Z", text)])
        self.assertEqual((honored, invalidated), (0, 0))

    # --- interaction with the strict grammar -------------------------------

    def test_strict_matched_line_never_also_counted_as_prose(self):
        # A genuine strict-grammar LEASE-HONORED: line also contains the
        # literal substrings the prose heuristic looks for ("lease",
        # "HONORED") -- it must be masked out of prose scanning so it is
        # counted ONCE, under the strict field, never twice.
        result = self._prose([
            final_answer("2026-08-01T05:00:00.000Z",
                          "LEASE-HONORED: command=pytest tests/ tree_sha=abc1234"),
        ])
        self.assertEqual(result, (0, 0))

    def test_prose_counts_are_separate_fields_never_folded_into_strict(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_rollout(tmp, "a.jsonl", [
                final_answer("2026-08-01T05:00:00.000Z",
                              "LEASE-HONORED: command=pytest tests/ tree_sha=abc1234"),
                final_answer("2026-08-01T05:01:00.000Z",
                              "The provided lease receipt reports 4 passed; verification "
                              "was not rerun per review constraints."),
            ])
            import score_x5_leases as sx5
            events = sx5.lease_stats([path])["lease_events"]
        self.assertEqual(events["receipts_honored"], 1)
        self.assertEqual(events["receipts_honored_prose"], 1)

    def test_rereading_the_same_prose_line_twice_counts_once(self):
        # Same re-read-inflation concern as the strict grammar's item-10
        # fix, applied consistently to the prose counts: the identical
        # reviewer sentence relayed into two different text sources (its
        # own final_answer AND a parent's inter-agent relay of it) must
        # still collapse to one distinct prose event.
        text = ("The provided lease receipt reports 4 passed; verification was not "
                "rerun per review constraints.")
        result = self._prose([
            final_answer("2026-08-01T05:00:00.000Z", text),
            inter_agent_message("2026-08-01T05:01:00.000Z", text),
        ])
        self.assertEqual(result, (1, 0))


class TestLeaseStatsIntegration(unittest.TestCase):
    def test_empty_input_returns_zeroed_shape(self):
        import score_x5_leases as sx5
        result = sx5.lease_stats([])
        self.assertEqual(result, {
            "verification_runs": [],
            "duplicate_groups": [],
            "lease_events": {"receipts_issued": 0, "receipts_honored": 0, "invalidation_reruns": 0,
                              "receipts_honored_prose": 0, "invalidation_reruns_prose": 0},
        })

    def test_verification_runs_sorted_by_timestamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = write_rollout(tmp, "a.jsonl", [
                exec_cmd("2026-07-31T05:05:00.000Z", "r1", "npm test"),
            ])
            b = write_rollout(tmp, "b.jsonl", [
                exec_cmd("2026-07-31T05:00:00.000Z", "r2", "pytest tests/"),
            ])
            import score_x5_leases as sx5
            result = sx5.lease_stats([a, b])
        timestamps = [r["timestamp"] for r in result["verification_runs"]]
        self.assertEqual(timestamps, sorted(timestamps))


if __name__ == "__main__":
    unittest.main()
