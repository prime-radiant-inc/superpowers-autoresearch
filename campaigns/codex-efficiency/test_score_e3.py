"""Tests for score_e3.py's duplicate-gate / evidence-receipts census (Task
10, E3). Synthetic rollout fixtures only -- fake rep-dir names, minimal
hand-built exec_command/patch_apply_end/user_message records -- no real
rollouts, no client/corpus content.

Privacy-by-construction check woven through these tests: score_e3.py's
report-facing records (duplicate_gate_pairs, waiver_violations) must never
carry the raw or normalized command TEXT, only an anonymized per-run
`cmd_id` label (assigned by first-appearance order) -- several tests below
assert the absence of a "cmd"/"cmd_norm" key on those output records, not
just the presence of the right counts."""
import json, os, pathlib, tempfile, unittest
import score_e3 as se
import rollout_parser as rp


def _rec(ts, typ, payload):
    return json.dumps({"timestamp": ts, "type": typ, "payload": payload})


def user_message(ts, text):
    return _rec(ts, "event_msg", {"type": "user_message", "message": text})


def exec_cmd(ts, call_id, cmd):
    return _rec(ts, "response_item", {
        "type": "function_call", "id": call_id, "name": "exec_command",
        "arguments": json.dumps({"cmd": cmd}), "call_id": call_id})


def custom_exec_cmd(ts, call_id, raw_input):
    """custom_tool_call/"exec" encoding -- `input` is taken WHOLE, never
    JSON-decoded (see rollout_parser.exec_commands()'s docstring), unlike
    exec_cmd() above's "exec_command" encoding."""
    return _rec(ts, "response_item", {
        "type": "custom_tool_call", "id": call_id, "name": "exec",
        "input": raw_input, "call_id": call_id})


def patch_apply(ts, call_id, success=True):
    return _rec(ts, "event_msg", {
        "type": "patch_apply_end", "call_id": call_id, "turn_id": "t1",
        "success": success, "changes": ({"/work/repo/x.py": {"type": "update"}} if success else {})})


def git_commit(ts, call_id):
    return exec_cmd(ts, call_id, "git commit -m 'wip'")


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


FULL_SUITE = "python3 -m unittest discover -s tests -v"
OTHER_SUITE = "python3 -m unittest tests.test_cli -v"


class TestNormalizeCmd(unittest.TestCase):
    def test_collapses_whitespace_runs_and_strips(self):
        self.assertEqual(
            se._normalize_cmd("python   -m  unittest\ndiscover  -s tests"),
            "python -m unittest discover -s tests")

    def test_identical_after_normalization_are_equal(self):
        a = se._normalize_cmd("python3 -m unittest discover -s tests -v")
        b = se._normalize_cmd("python3  -m  unittest   discover -s tests -v")
        self.assertEqual(a, b)


class TestTestInvocationRe(unittest.TestCase):
    def test_matches_python_unittest_variants(self):
        self.assertTrue(se.TEST_INVOCATION_RE.search("python -m unittest discover -s tests"))
        self.assertTrue(se.TEST_INVOCATION_RE.search("python3 -m unittest tests.test_core -v"))

    def test_matches_other_known_runners(self):
        self.assertTrue(se.TEST_INVOCATION_RE.search("pytest tests/"))
        self.assertTrue(se.TEST_INVOCATION_RE.search("go test ./..."))

    def test_does_not_match_non_test_commands(self):
        self.assertFalse(se.TEST_INVOCATION_RE.search("ls tests/"))
        self.assertFalse(se.TEST_INVOCATION_RE.search("git status"))
        self.assertFalse(se.TEST_INVOCATION_RE.search("cat tests/test_core.py"))


class TestTestCommandEvents(unittest.TestCase):
    def test_extracts_only_test_shaped_commands_with_normalized_cmd(self):
        lines = [
            exec_cmd("2026-07-30T05:00:00.000Z", "c1", FULL_SUITE),
            exec_cmd("2026-07-30T05:00:01.000Z", "c2", "ls tests/"),
            exec_cmd("2026-07-30T05:00:02.000Z", "c3", "git status"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "r.jsonl"
            p.write_text("\n".join(lines) + "\n")
            events = se.test_command_events(p)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["timestamp"], "2026-07-30T05:00:00.000Z")
        self.assertEqual(events[0]["cmd_norm"], se._normalize_cmd(FULL_SUITE))

    def test_empty_when_no_test_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "r.jsonl"
            p.write_text(exec_cmd("2026-07-30T05:00:00.000Z", "c1", "ls tests/") + "\n")
            self.assertEqual(se.test_command_events(p), [])

    def test_custom_exec_literal_backslash_n_before_test_invocation_is_still_detected(self):
        # Fix round 1 (real bug, reviewer-verified against the MINE-tier
        # battery corpus): a custom_exec command's raw JS-source input
        # can carry a literal, undecoded "\n" (backslash + n, two chars)
        # right before "python3 -m unittest ..." -- the "n" defeats
        # TEST_INVOCATION_RE's leading \b, silently dropping the
        # occurrence before this fix.
        raw = "echo start\\n" + FULL_SUITE  # literal backslash-n before FULL_SUITE
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "r.jsonl"
            p.write_text(custom_exec_cmd("2026-07-30T05:00:00.000Z", "c1", raw) + "\n")
            events = se.test_command_events(p)
        self.assertEqual(len(events), 1)
        # cmd_norm reflects the DE-ESCAPED whole-command text (the
        # literal 2-char "\n" became a real newline, which whitespace-
        # normalization then collapses to a single space) -- proving the
        # match came from genuinely decoded text, not a fluke.
        self.assertEqual(events[0]["cmd_norm"], "echo start " + se._normalize_cmd(FULL_SUITE))

    def test_exec_command_encoding_with_literal_backslash_n_is_unaffected(self):
        # Sanity check: the "exec_command" encoding is already
        # JSON-decoded upstream, so a command that happens to legitimately
        # contain a literal backslash-n substring (not a real newline)
        # after JSON decoding must NOT be touched by the de-escape fix --
        # it stays exactly as exec_commands() already returns it, and
        # TEST_INVOCATION_RE's own \b still requires a genuine boundary.
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "r.jsonl"
            p.write_text(exec_cmd("2026-07-30T05:00:00.000Z", "c1", "echo start\\n" + FULL_SUITE) + "\n")
            events = se.test_command_events(p)
        # "echo start\nFULL_SUITE" (literal 2-char \n, exec_command
        # encoding, never de-escaped) still defeats the leading \b --
        # correctly still excluded, exactly like before this fix.
        self.assertEqual(events, [])


class TestMutationTimeline(unittest.TestCase):
    def test_merges_and_sorts_across_multiple_rollouts(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            p1 = base / "a.jsonl"
            p1.write_text(git_commit("2026-07-30T05:00:10.000Z", "c1") + "\n")
            p2 = base / "b.jsonl"
            p2.write_text(patch_apply("2026-07-30T05:00:05.000Z", "c2") + "\n")
            self.assertEqual(se.mutation_timeline([p1, p2]),
                             ["2026-07-30T05:00:05.000Z", "2026-07-30T05:00:10.000Z"])

    def test_empty_when_no_rollouts_mutate(self):
        with tempfile.TemporaryDirectory() as tmp:
            p1 = pathlib.Path(tmp) / "a.jsonl"
            p1.write_text(exec_cmd("2026-07-30T05:00:00.000Z", "c1", "git status") + "\n")
            self.assertEqual(se.mutation_timeline([p1]), [])


class TestDuplicateGatePairs(unittest.TestCase):
    def _two_session_run(self, second_session_lines_extra=()):
        """Session A (implementer-shaped) runs FULL_SUITE once; session B
        (reviewer-shaped) reruns the identical normalized command later,
        with whatever extra lines the caller supplies in between (e.g. a
        mutation) injected into session B before its rerun."""
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            pa = base / "a.jsonl"
            pa.write_text(exec_cmd("2026-07-30T05:00:00.000Z", "c1", FULL_SUITE) + "\n")
            pb_lines = list(second_session_lines_extra) + [
                exec_cmd("2026-07-30T05:05:00.000Z", "c2", FULL_SUITE)]
            pb = base / "b.jsonl"
            pb.write_text("\n".join(pb_lines) + "\n")
            return se.score_tree([pa, pb], label="test")

    def test_flags_identical_pair_across_sessions_with_zero_mutations_between(self):
        result = self._two_session_run()
        pairs = result["duplicate_gate_pairs"]
        self.assertEqual(len(pairs), 1)
        pair = pairs[0]
        self.assertTrue(pair["is_duplicate_gate"])
        self.assertEqual(pair["mutations_between"], 0)
        self.assertEqual(pair["first"]["timestamp"], "2026-07-30T05:00:00.000Z")
        self.assertEqual(pair["second"]["timestamp"], "2026-07-30T05:05:00.000Z")
        # Privacy: never the raw/normalized command text on the output record.
        self.assertNotIn("cmd", pair)
        self.assertNotIn("cmd_norm", pair)
        self.assertIn("cmd_id", pair)

    def test_intervening_mutation_clears_the_flag(self):
        result = self._two_session_run(
            second_session_lines_extra=[git_commit("2026-07-30T05:02:00.000Z", "mut1")])
        pairs = result["duplicate_gate_pairs"]
        self.assertEqual(len(pairs), 1)
        pair = pairs[0]
        self.assertFalse(pair["is_duplicate_gate"])
        self.assertEqual(pair["mutations_between"], 1)

    def test_different_normalized_commands_are_not_paired(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            pa = base / "a.jsonl"
            pa.write_text(exec_cmd("2026-07-30T05:00:00.000Z", "c1", FULL_SUITE) + "\n")
            pb = base / "b.jsonl"
            pb.write_text(exec_cmd("2026-07-30T05:05:00.000Z", "c2", OTHER_SUITE) + "\n")
            result = se.score_tree([pa, pb], label="test")
        self.assertEqual(result["duplicate_gate_pairs"], [])

    def test_three_identical_occurrences_yield_two_consecutive_pairs_not_three(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            p = base / "a.jsonl"
            p.write_text("\n".join([
                exec_cmd("2026-07-30T05:00:00.000Z", "c1", FULL_SUITE),
                exec_cmd("2026-07-30T05:01:00.000Z", "c2", FULL_SUITE),
                exec_cmd("2026-07-30T05:02:00.000Z", "c3", FULL_SUITE),
            ]) + "\n")
            result = se.score_tree([p], label="test")
        self.assertEqual(len(result["duplicate_gate_pairs"]), 2)
        self.assertEqual(
            [(pr["first"]["timestamp"], pr["second"]["timestamp"]) for pr in result["duplicate_gate_pairs"]],
            [("2026-07-30T05:00:00.000Z", "2026-07-30T05:01:00.000Z"),
             ("2026-07-30T05:01:00.000Z", "2026-07-30T05:02:00.000Z")])

    def test_no_pairs_when_command_runs_only_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "a.jsonl"
            p.write_text(exec_cmd("2026-07-30T05:00:00.000Z", "c1", FULL_SUITE) + "\n")
            result = se.score_tree([p], label="test")
        self.assertEqual(result["duplicate_gate_pairs"], [])


class TestPerSessionRepeatCounts(unittest.TestCase):
    def test_session_max_and_run_distribution(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            # session "a": FULL_SUITE run 9 times (matches the corpus
            # validation target's magnitude), one minute apart.
            a_lines = [exec_cmd(f"2026-07-30T05:0{i}:00.000Z", f"c{i}", FULL_SUITE)
                       for i in range(9)]
            pa = base / "a.jsonl"
            pa.write_text("\n".join(a_lines) + "\n")
            # session "b": a single occurrence only.
            pb = base / "b.jsonl"
            pb.write_text(exec_cmd("2026-07-30T06:00:00.000Z", "cb", OTHER_SUITE) + "\n")
            result = se.score_tree([pa, pb], label="test")
        per_session = result["per_session_repeat"]
        self.assertEqual(per_session[os.path.basename(pa)]["max_repeat"], 9)
        self.assertEqual(per_session[os.path.basename(pb)]["max_repeat"], 1)
        self.assertEqual(result["run_max_repeat"], 9)
        self.assertEqual(sorted(result["repeat_distribution"]), [1, 9])


class TestWaiverDetection(unittest.TestCase):
    WAIVER_TEXT = "that's a known-red baseline failure, ignore it and proceed"

    def test_finds_earliest_waiver_timestamp_case_insensitive(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "a.jsonl"
            p.write_text("\n".join([
                user_message("2026-07-30T05:00:00.000Z", "please finish up"),
                user_message("2026-07-30T05:10:00.000Z",
                             "That's A Known-Red Baseline Failure, Ignore It And Proceed"),
            ]) + "\n")
            ts = se.find_waiver_timestamp([p], self.WAIVER_TEXT)
        self.assertEqual(ts, "2026-07-30T05:10:00.000Z")

    def test_returns_none_when_marker_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "a.jsonl"
            p.write_text(user_message("2026-07-30T05:00:00.000Z", "please finish up") + "\n")
            self.assertIsNone(se.find_waiver_timestamp([p], self.WAIVER_TEXT))

    def test_returns_none_when_marker_is_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "a.jsonl"
            p.write_text(user_message("2026-07-30T05:00:00.000Z", "please finish up") + "\n")
            self.assertIsNone(se.find_waiver_timestamp([p], None))


class TestWaiverViolations(unittest.TestCase):
    def _build(self, extra_between=()):
        lines = [
            exec_cmd("2026-07-30T05:00:00.000Z", "c1", FULL_SUITE),  # fails
            user_message("2026-07-30T05:01:00.000Z",
                         "that's a known-red baseline failure, ignore it and proceed"),
        ]
        lines += list(extra_between)
        lines.append(exec_cmd("2026-07-30T05:02:00.000Z", "c2", FULL_SUITE))  # rerun
        return lines

    def test_flags_rerun_after_waiver_with_no_intervening_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "a.jsonl"
            p.write_text("\n".join(self._build()) + "\n")
            result = se.score_tree([p], label="test",
                                   waiver_marker="ignore it and proceed")
        self.assertTrue(result["waiver"]["found"])
        self.assertEqual(result["waiver"]["timestamp"], "2026-07-30T05:01:00.000Z")
        violations = result["waiver"]["violations"]
        self.assertEqual(len(violations), 1)
        v = violations[0]
        self.assertEqual(v["rerun_timestamp"], "2026-07-30T05:02:00.000Z")
        self.assertNotIn("cmd", v)
        self.assertNotIn("cmd_norm", v)

    def test_no_violation_when_mutation_follows_waiver(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "a.jsonl"
            p.write_text("\n".join(self._build(
                extra_between=[git_commit("2026-07-30T05:01:30.000Z", "fixcommit")])) + "\n")
            result = se.score_tree([p], label="test",
                                   waiver_marker="ignore it and proceed")
        self.assertEqual(result["waiver"]["violations"], [])

    def test_no_waiver_marker_means_not_found_and_no_violations(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "a.jsonl"
            p.write_text("\n".join(self._build()) + "\n")
            result = se.score_tree([p], label="test", waiver_marker=None)
        self.assertFalse(result["waiver"]["found"])
        self.assertEqual(result["waiver"]["violations"], [])

    def test_unrelated_command_never_run_before_waiver_is_not_a_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "a.jsonl"
            lines = [
                user_message("2026-07-30T05:01:00.000Z",
                             "that's a known-red baseline failure, ignore it and proceed"),
                # OTHER_SUITE never ran before the waiver -- its post-waiver
                # appearance is a normal first run, not a waived rerun.
                exec_cmd("2026-07-30T05:02:00.000Z", "c2", OTHER_SUITE),
            ]
            p.write_text("\n".join(lines) + "\n")
            result = se.score_tree([p], label="test",
                                   waiver_marker="ignore it and proceed")
        self.assertEqual(result["waiver"]["violations"], [])


class TestEventsBetween(unittest.TestCase):
    """Content-free manual-verification helper: for a flagged pair, show
    WHAT happened between the two timestamps (kind + timestamp + rollout
    only) without ever touching raw command text -- used to manually
    verify a flagged duplicate-gate pair really had nothing intervene."""

    def test_returns_mutation_and_test_events_strictly_between_bounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            p = base / "a.jsonl"
            p.write_text("\n".join([
                exec_cmd("2026-07-30T05:00:00.000Z", "c1", FULL_SUITE),
                git_commit("2026-07-30T05:00:30.000Z", "m1"),
                exec_cmd("2026-07-30T05:01:00.000Z", "c2", OTHER_SUITE),
                exec_cmd("2026-07-30T05:02:00.000Z", "c3", FULL_SUITE),
            ]) + "\n")
            events = se.events_between([p], "2026-07-30T05:00:00.000Z", "2026-07-30T05:02:00.000Z")
        kinds = [(e["kind"], e["timestamp"]) for e in events]
        self.assertEqual(kinds, [
            ("mutation", "2026-07-30T05:00:30.000Z"),
            ("test_cmd", "2026-07-30T05:01:00.000Z"),
        ])
        for e in events:
            self.assertNotIn("cmd", e)
            self.assertNotIn("cmd_norm", e)

    def test_empty_when_bounds_are_adjacent(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "a.jsonl"
            p.write_text(exec_cmd("2026-07-30T05:00:00.000Z", "c1", FULL_SUITE) + "\n")
            self.assertEqual(
                se.events_between([p], "2026-07-30T05:00:00.000Z", "2026-07-30T05:00:00.000Z"), [])


class TestInvalidationGuardPassed(unittest.TestCase):
    """invalidation_guard_passed() (Task 10 brief Step 4): the
    CORRECTNESS counterpart to the duplicate-gate check -- proves SOME
    re-verification happened after a real mutation. Deliberately does
    NOT require an exact-string-identical rerun the way the duplicate-
    gate check does: fix round 1's real `cx-finishing-invalidation`
    probe run showed a dev-arm coding agent bundling its test invocation
    with a DIFFERENT set of surrounding git-diagnostic commands every
    single time (Promise.all-batched exec calls), so no two occurrences
    were ever byte-identical -- an exact-match implementation of this
    guard would have returned a FALSE NEGATIVE on a real, confirmed
    rerun-after-mutation. This is the regression guard any future
    duplicate-gate treatment must keep passing, so it must reflect
    reality on real command-bundling styles, not just clean synthetic
    fixtures."""

    def test_true_when_a_test_occurrence_follows_a_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "a.jsonl"
            p.write_text("\n".join([
                exec_cmd("2026-07-30T05:00:00.000Z", "c1", FULL_SUITE),
                git_commit("2026-07-30T05:01:00.000Z", "m1"),
                exec_cmd("2026-07-30T05:02:00.000Z", "c2", FULL_SUITE),
            ]) + "\n")
            result = se.score_tree([p], label="test")
        self.assertTrue(result["invalidation_guard_passed"])

    def test_true_even_when_the_rerun_is_bundled_differently_and_never_exact_matches(self):
        # Reproduces the real fix-round-1 finding: the rerun is a
        # DIFFERENT full command (different surrounding diagnostics)
        # each time, so duplicate_gate_pairs is empty (0 pairs) -- the
        # guard must still recognize the genuine rerun-after-mutation.
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "a.jsonl"
            p.write_text("\n".join([
                exec_cmd("2026-07-30T05:00:00.000Z", "c1", FULL_SUITE + "; git status"),
                git_commit("2026-07-30T05:01:00.000Z", "m1"),
                exec_cmd("2026-07-30T05:02:00.000Z", "c2", FULL_SUITE + "; git log -1"),
            ]) + "\n")
            result = se.score_tree([p], label="test")
        self.assertEqual(result["duplicate_gate_pairs"], [])  # confirms no exact-match pair
        self.assertTrue(result["invalidation_guard_passed"])

    def test_false_when_no_test_occurrence_follows_any_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "a.jsonl"
            p.write_text("\n".join([
                exec_cmd("2026-07-30T05:00:00.000Z", "c1", FULL_SUITE),
                git_commit("2026-07-30T05:01:00.000Z", "m1"),
            ]) + "\n")
            result = se.score_tree([p], label="test")
        self.assertFalse(result["invalidation_guard_passed"])

    def test_false_when_no_mutation_exists_at_all(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "a.jsonl"
            p.write_text("\n".join([
                exec_cmd("2026-07-30T05:00:00.000Z", "c1", FULL_SUITE),
                exec_cmd("2026-07-30T05:02:00.000Z", "c2", FULL_SUITE),
            ]) + "\n")
            result = se.score_tree([p], label="test")
        self.assertFalse(result["invalidation_guard_passed"])


class TestScoreRunAndOutput(unittest.TestCase):
    def test_score_run_discovers_rollouts_and_labels(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                exec_cmd("2026-07-30T05:00:00.000Z", "c1", FULL_SUITE),
                exec_cmd("2026-07-30T05:05:00.000Z", "c2", FULL_SUITE),
            ])
        with tempfile.TemporaryDirectory() as tmp:
            rundir = make_run(pathlib.Path(tmp), "cx-finishing-dev", 1, build)
            run = se.score_run(str(rundir))
        self.assertEqual(run["arm_scenario"], "cx-finishing-dev")
        self.assertEqual(run["rep"], 1)
        self.assertEqual(len(run["duplicate_gate_pairs"]), 1)

    def test_score_run_raises_when_no_rollouts(self):
        with tempfile.TemporaryDirectory() as tmp:
            rundir = pathlib.Path(tmp) / "empty"
            (rundir / "home" / ".codex" / "sessions").mkdir(parents=True)
            with self.assertRaises(SystemExit):
                se.score_run(str(rundir))

    def test_label_includes_rep_range(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                exec_cmd("2026-07-30T05:00:00.000Z", "c1", FULL_SUITE)])
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            runs = [se.score_run(str(make_run(base, "cx-finishing-dev", r, build)))
                    for r in (1, 2, 3)]
            self.assertEqual(se._out_label(runs), "cx-finishing-dev-rep1-3")

    def test_refuses_overwrite_without_force_then_force_allows(self):
        def build(sess_dir):
            write_rollout(sess_dir, "2026-07-30T05-00-00", "root0000", [
                exec_cmd("2026-07-30T05:00:00.000Z", "c1", FULL_SUITE)])
        with tempfile.TemporaryDirectory() as tmp:
            battery = pathlib.Path(tmp) / "battery"
            out_dir = pathlib.Path(tmp) / "out"
            runs = [se.score_run(str(make_run(battery, "cx-finishing-dev", r, build)))
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
