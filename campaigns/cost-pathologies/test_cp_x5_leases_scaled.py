"""Validation for the cp-x5-leases-scaled scenario (queue-execution
campaign, 2026-08-01, item 6 of reports/2026-08-cost-pathologies-
campaign.md §6's owed-fixtures queue): an X5 fixture sized so the
duplicate-verification worst case reaches a magnitude comparable to the
report's corrected anchor (10, not the design doc's rough "12x" quote --
see `scenarios/cp-x5-leases-scaled/seeded-truth-ledger.md`), instead of
`cp-x5-leases`'s original 3-task plan, which this task's own report
ruled "structurally too small" to separate a real reduction from
ordinary SDD variance.

Per the controller ruling `cp-x1-edit-existing`, `cp-x1-wavecap`,
`cp-x2-consequential`, `cp-x6-planframed`, and `cp-x8-approvals-v2`
each operated under (their own test files' docstrings), this task
spends no container/API budget on real reps. This file validates three
properties, entirely from committed fixtures and CONSTRUCTED rollout
transcripts -- see `scenarios/cp-x5-leases-scaled/seeded-truth-
ledger.md` for the full design rationale and the exact arithmetic this
file implements literally:

  1. `TestSetupMaterializesDeterministicallyAndStartsClean` --
     setup.sh materializes a session's starting tree by copying this
     scenario's own `fixtures/` directory verbatim: two independent
     copies are byte-identical, and none of the plan's five tasks' own
     output exists yet.
  2. `TestPlanStructure` -- the plan has >=5 `## Task N:` sections, and
     each task's own `**Verification:**` line matches the ledger's
     per-task command table exactly (this also keeps the plan and the
     ledger from silently drifting apart under future edits).
  3. `TestDuplicateVerificationWorstCase` -- a CONSTRUCTED, maximally
     undisciplined transcript, built exactly per the ledger's
     "four windows x up to three occurrences" structure, scores (via
     the REAL `score_x5_leases.lease_stats()`, not a reimplementation)
     exactly 8 duplicated `pytest tests/` runs across 4 duplicate
     groups, with zero `lease_events` (no arm mechanism engaged).
  4. `TestLeaseHonoringCollapsesDuplicates` -- two CONSTRUCTED,
     maximally arm-compliant transcripts (one X5-B-shaped: honoring
     recorded in the strict `LEASE-HONORED:`/`LEASE-INVALIDATED:`
     grammar; one X5-A-shaped: the same decisions narrated in prose,
     per Task 2's `_lease_events_prose()` detector and the real corpus
     finding it was built from) each collapse `duplicate_groups` for
     `pytest tests/` to zero, while the Task 4 guard event (the stale
     `SHA_3` receipt correctly declined, a fresh `SHA_4` receipt issued
     and cited) is present in both -- matching the ledger's predicted
     per-arm signature table exactly, including its 9-distinct-event
     total and the dedup subtlety that keeps it at 9, not more.

Everything here is synthetic; no real system.
"""
import filecmp
import json
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
SCENARIO_DIR = HERE / "scenarios" / "cp-x5-leases-scaled"
SCENARIO_FIXTURES = SCENARIO_DIR / "fixtures"
PLAN_PATH = SCENARIO_FIXTURES / "docs" / "superpowers" / "plans" / "dispatch-queue-plan.md"

TASK_OUTPUT_FILES = (
    "dispatchqueue/queue.py",
    "dispatchqueue/workers.py",
    "dispatchqueue/retry.py",
    "dispatchqueue/deadletter.py",
)

# Per the ledger's table -- the plan's own mandated Verification command
# for each of the five tasks.
EXPECTED_VERIFICATION_COMMANDS = {
    1: "pytest tests/test_queue.py",
    2: "pytest tests/",
    3: "pytest tests/",
    4: "pytest tests/",
    5: "pytest tests/",
}

TASK_HEADER_RE = re.compile(r"^## Task (\d+):", re.MULTILINE)
VERIFICATION_LINE_RE = re.compile(r"\*\*Verification:\*\*\s*`([^`]+)`")


# ---------------------------------------------------------------------------
# Property 1: setup.sh materializes deterministically and starts clean.
# ---------------------------------------------------------------------------


class TestSetupMaterializesDeterministicallyAndStartsClean(unittest.TestCase):
    def _assert_no_diff(self, comparison):
        self.assertEqual(comparison.left_only, [], f"only in copy A: {comparison.left_only}")
        self.assertEqual(comparison.right_only, [], f"only in copy B: {comparison.right_only}")
        self.assertEqual(comparison.diff_files, [], f"differing files: {comparison.diff_files}")
        for sub in comparison.subdirs.values():
            self._assert_no_diff(sub)

    def test_two_independent_copies_of_fixtures_are_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy_a = Path(tmp) / "a"
            copy_b = Path(tmp) / "b"
            shutil.copytree(SCENARIO_FIXTURES, copy_a)
            shutil.copytree(SCENARIO_FIXTURES, copy_b)
            self._assert_no_diff(filecmp.dircmp(copy_a, copy_b))

    def test_materialized_starting_tree_has_no_task_output_yet(self):
        with tempfile.TemporaryDirectory() as tmp:
            materialized = Path(tmp) / "materialized"
            shutil.copytree(SCENARIO_FIXTURES, materialized)
            for relpath in TASK_OUTPUT_FILES:
                self.assertFalse((materialized / relpath).exists(), f"{relpath} should not exist pre-session")
            self.assertFalse((materialized / "tests").exists(), "tests/ should not exist pre-session")

    def test_plan_and_pyproject_are_present_in_the_materialized_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            materialized = Path(tmp) / "materialized"
            shutil.copytree(SCENARIO_FIXTURES, materialized)
            self.assertTrue(
                (materialized / "docs" / "superpowers" / "plans" / "dispatch-queue-plan.md").exists()
            )
            self.assertTrue((materialized / "pyproject.toml").exists())


# ---------------------------------------------------------------------------
# Property 2: plan structure -- >=5 tasks, and each task's mandated
# Verification command matches the ledger's own table.
# ---------------------------------------------------------------------------


class TestPlanStructure(unittest.TestCase):
    def setUp(self):
        self.plan_text = PLAN_PATH.read_text()

    def test_plan_has_at_least_five_tasks(self):
        task_numbers = [int(m.group(1)) for m in TASK_HEADER_RE.finditer(self.plan_text)]
        self.assertGreaterEqual(len(task_numbers), 5, task_numbers)
        self.assertEqual(task_numbers, sorted(task_numbers), "tasks must appear in order")

    def test_every_task_verification_command_matches_the_ledger(self):
        # Split the plan into one chunk per "## Task N:" section so each
        # task's own Verification line is matched against ONLY that
        # task's own text, not a later task's.
        sections = TASK_HEADER_RE.split(self.plan_text)[1:]  # [num, body, num, body, ...]
        by_task = dict(zip((int(n) for n in sections[0::2]), sections[1::2]))
        self.assertEqual(set(by_task), set(EXPECTED_VERIFICATION_COMMANDS))
        for task_num, expected_cmd in EXPECTED_VERIFICATION_COMMANDS.items():
            with self.subTest(task=task_num):
                m = VERIFICATION_LINE_RE.search(by_task[task_num])
                self.assertIsNotNone(m, f"Task {task_num} has no **Verification:** line")
                self.assertEqual(m.group(1), expected_cmd)

    def test_task_4_is_the_required_reverification_correction(self):
        sections = TASK_HEADER_RE.split(self.plan_text)[1:]
        by_task = dict(zip((int(n) for n in sections[0::2]), sections[1::2]))
        self.assertIn("100", by_task[4])
        self.assertIn("20", by_task[4])
        self.assertIn("MUST be re-run and updated", by_task[4])

    def test_tasks_three_and_five_carry_the_reviewer_caution_lever(self):
        # The brief's "at least two tasks whose review naturally tempts a
        # full-suite re-run" design lever -- both must be present in the
        # plan's OWN text, not just asserted in the ledger.
        sections = TASK_HEADER_RE.split(self.plan_text)[1:]
        by_task = dict(zip((int(n) for n in sections[0::2]), sections[1::2]))
        self.assertIn("nervous", by_task[3])
        self.assertIn("strongest reason", by_task[5])


# ---------------------------------------------------------------------------
# Rollout construction helpers -- inline JSONL-record helpers, no
# committed fixture files. Mirrors test_score_x5_leases.py's own
# established convention (the closest precedent for scoring CONSTRUCTED
# transcripts against the real scorer) rather than importing across test
# files, which no test file in this campaign does.
# ---------------------------------------------------------------------------


def _rec(ts, typ, payload):
    return json.dumps({"timestamp": ts, "type": typ, "payload": payload})


def exec_cmd(ts, call_id, cmd):
    return _rec(ts, "response_item", {
        "type": "function_call", "id": call_id, "name": "exec_command",
        "arguments": json.dumps({"cmd": cmd}), "call_id": call_id})


def exec_output(ts, call_id, output_text):
    return _rec(ts, "response_item", {
        "type": "function_call_output", "call_id": call_id, "output": output_text})


def final_answer(ts, message):
    return _rec(ts, "event_msg", {"type": "agent_message", "message": message, "phase": "final_answer"})


def write_rollout(tmpdir, name, lines):
    path = os.path.join(tmpdir, name)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


def commit_event(ts, call_id, sha, subject="task work"):
    """A `git commit` call + its matching output, resolving to SHA under
    score_x5_leases._git_evidence() -- see score_x5_leases.py's
    _COMMIT_LINE_RE."""
    return [
        exec_cmd(ts, call_id, f"git commit -m '{subject}'"),
        exec_output(ts, call_id, f"[main {sha}] {subject}"),
    ]


# Symbolic tree SHAs for the four full-suite windows (Tasks 2-5), per the
# ledger's table. All are valid lowercase-hex tokens >=7 chars.
SHA = {2: "2222222", 3: "3333333", 4: "4444444", 5: "5555555"}

FULL_SUITE = "pytest tests/"


# ---------------------------------------------------------------------------
# Property 3: the undisciplined worst case -- 4 windows x (1 legitimate +
# 2 avoidable duplicate) `pytest tests/` occurrences = 8 duplicated runs
# available, with no lease vocabulary anywhere.
# ---------------------------------------------------------------------------


def _build_undisciplined_transcript(tmpdir):
    lines = []
    t = 0

    def next_ts():
        nonlocal t
        t += 1
        return f"2026-08-01T05:{t:02d}:00.000Z"

    # Task 1's own file-scoped run -- a different command_norm, must never
    # join the `pytest tests/` duplicate groups.
    lines.append(exec_cmd(next_ts(), "task1-impl", "pytest tests/test_queue.py"))

    for task_num in (2, 3, 4, 5):
        sha = SHA[task_num]
        lines.extend(commit_event(next_ts(), f"commit-{task_num}", sha, subject=f"Task {task_num}"))
        # Occasion 1: implementer's own mandated run (legitimate).
        lines.append(exec_cmd(next_ts(), f"impl-{task_num}", FULL_SUITE))
        # Occasion 2: task-reviewer's own re-verification pass (duplicate).
        lines.append(exec_cmd(next_ts(), f"review-{task_num}", FULL_SUITE))
        # Occasion 3: a cautious pre-next-task check, or (Task 5) Final
        # Review's own re-verification pass (duplicate).
        lines.append(exec_cmd(next_ts(), f"caution-{task_num}", FULL_SUITE))

    return write_rollout(tmpdir, "undisciplined.jsonl", lines)


class TestDuplicateVerificationWorstCase(unittest.TestCase):
    def test_eight_duplicated_full_suite_runs_available(self):
        import score_x5_leases as sx5

        with tempfile.TemporaryDirectory() as tmp:
            path = _build_undisciplined_transcript(tmp)
            result = sx5.lease_stats([path])

        groups = [g for g in result["duplicate_groups"] if g["command_norm"] == FULL_SUITE]
        self.assertEqual(len(groups), 4, groups)
        for g in groups:
            with self.subTest(tree_sha=g["tree_sha"]):
                self.assertEqual(g["count"], 3, g)
        self.assertEqual({g["tree_sha"] for g in groups}, set(SHA.values()))

        duplicated_runs = sum(g["count"] - 1 for g in groups)
        self.assertEqual(duplicated_runs, 8, "the ledger's own >=8 target")

        # No arm mechanism was engaged in this transcript.
        self.assertEqual(result["lease_events"], {
            "receipts_issued": 0, "receipts_honored": 0, "invalidation_reruns": 0,
            "receipts_honored_prose": 0, "invalidation_reruns_prose": 0,
        })

    def test_task_one_own_file_scoped_run_never_joins_the_full_suite_groups(self):
        import score_x5_leases as sx5

        with tempfile.TemporaryDirectory() as tmp:
            path = _build_undisciplined_transcript(tmp)
            result = sx5.lease_stats([path])

        scoped_runs = [r for r in result["verification_runs"] if r["command_norm"] == "pytest tests/test_queue.py"]
        self.assertEqual(len(scoped_runs), 1)
        scoped_groups = [g for g in result["duplicate_groups"] if g["command_norm"] == "pytest tests/test_queue.py"]
        self.assertEqual(scoped_groups, [])


# ---------------------------------------------------------------------------
# Property 4: lease-honoring collapses the duplicate opportunity to zero,
# in both the strict-grammar (X5-B) and prose (X5-A) forms, with the
# Task 4 guard event present in both.
# ---------------------------------------------------------------------------


def _build_strict_compliant_transcript(tmpdir):
    """X5-B-shaped: honoring/invalidation recorded in the strict
    LEASE-HONORED:/LEASE-INVALIDATED: grammar."""
    lines = []
    t = 0

    def next_ts():
        nonlocal t
        t += 1
        return f"2026-08-01T06:{t:02d}:00.000Z"

    prev_sha = None
    for task_num in (2, 3, 4, 5):
        sha = SHA[task_num]
        lines.extend(commit_event(next_ts(), f"commit-{task_num}", sha, subject=f"Task {task_num}"))

        if task_num == 4:
            # The guard: the stale prior-window receipt is declined before
            # the fresh run, not silently reused.
            lines.append(final_answer(
                next_ts(), f"LEASE-INVALIDATED: command={FULL_SUITE} tree_sha={prev_sha}"))

        # The single occasion where the suite actually runs: the
        # implementer's own mandated run, immediately followed by its
        # receipt.
        lines.append(exec_cmd(next_ts(), f"impl-{task_num}", FULL_SUITE))
        lines.append(final_answer(
            next_ts(), f"LEASE-RECEIPT: command={FULL_SUITE} tree_sha={sha} result=pass"))

        # The would-be duplicate occasion(s) collapse into a single
        # honoring citation instead of a re-run.
        lines.append(final_answer(
            next_ts(), f"LEASE-HONORED: command={FULL_SUITE} tree_sha={sha}"))

        prev_sha = sha

    return write_rollout(tmpdir, "strict_compliant.jsonl", lines)


def _build_prose_compliant_transcript(tmpdir):
    """X5-A-shaped: the identical underlying decisions, narrated in
    prose (Task 2's _lease_events_prose() detector) instead of the
    strict grammar -- the RECEIPT line itself stays strict grammar in
    both arms (implementer-prompt.md's Report Format is patched
    identically in cp/x5a and cp/x5b); only the later seat's own
    honor/decline channel differs, per the real corpus finding."""
    lines = []
    t = 0

    def next_ts():
        nonlocal t
        t += 1
        return f"2026-08-01T07:{t:02d}:00.000Z"

    honor_prose_by_task = {
        2: "Full-suite verification was not rerun per review constraints; "
           "the provided lease receipt reports the suite passing at the reviewed HEAD.",
        3: "Verification was not rerun per instruction; the supplied lease "
           "receipt reports the exact test command passed at the reviewed HEAD.",
        4: "Reviewed HEAD matches the required commit; supplied lease receipt "
           "evidence records the full suite passing at that SHA, so it was not rerun.",
        5: "The supplied HEAD receipt reports the full suite passing; I "
           "honored the lease and did not rerun solely for confirmation.",
    }
    invalidate_prose = (
        "The implementation report's lease receipt does not certify the "
        "reviewed commit; independent focused verification was run.")

    for task_num in (2, 3, 4, 5):
        sha = SHA[task_num]
        lines.extend(commit_event(next_ts(), f"commit-{task_num}", sha, subject=f"Task {task_num}"))

        if task_num == 4:
            lines.append(final_answer(next_ts(), invalidate_prose))

        lines.append(exec_cmd(next_ts(), f"impl-{task_num}", FULL_SUITE))
        lines.append(final_answer(
            next_ts(), f"LEASE-RECEIPT: command={FULL_SUITE} tree_sha={sha} result=pass"))

        lines.append(final_answer(next_ts(), honor_prose_by_task[task_num]))

    return write_rollout(tmpdir, "prose_compliant.jsonl", lines)


class TestLeaseHonoringCollapsesDuplicates(unittest.TestCase):
    def _full_suite_groups(self, result):
        return [g for g in result["duplicate_groups"] if g["command_norm"] == FULL_SUITE]

    def test_strict_grammar_arm_has_zero_duplicate_groups(self):
        import score_x5_leases as sx5

        with tempfile.TemporaryDirectory() as tmp:
            path = _build_strict_compliant_transcript(tmp)
            result = sx5.lease_stats([path])

        self.assertEqual(self._full_suite_groups(result), [])
        runs = [r for r in result["verification_runs"] if r["command_norm"] == FULL_SUITE]
        self.assertEqual(len(runs), 4, "exactly one run per window -- the duplicate occasions never ran")

    def test_strict_grammar_arm_lease_events_match_ledger(self):
        import score_x5_leases as sx5

        with tempfile.TemporaryDirectory() as tmp:
            path = _build_strict_compliant_transcript(tmp)
            result = sx5.lease_stats([path])

        self.assertEqual(result["lease_events"], {
            "receipts_issued": 4, "receipts_honored": 4, "invalidation_reruns": 1,
            "receipts_honored_prose": 0, "invalidation_reruns_prose": 0,
        })

    def test_prose_arm_has_zero_duplicate_groups(self):
        import score_x5_leases as sx5

        with tempfile.TemporaryDirectory() as tmp:
            path = _build_prose_compliant_transcript(tmp)
            result = sx5.lease_stats([path])

        self.assertEqual(self._full_suite_groups(result), [])
        runs = [r for r in result["verification_runs"] if r["command_norm"] == FULL_SUITE]
        self.assertEqual(len(runs), 4, "exactly one run per window -- the duplicate occasions never ran")

    def test_prose_arm_lease_events_match_ledger(self):
        import score_x5_leases as sx5

        with tempfile.TemporaryDirectory() as tmp:
            path = _build_prose_compliant_transcript(tmp)
            result = sx5.lease_stats([path])

        # RECEIPT stays strict grammar in both arms; honoring/invalidating
        # is carried entirely in the prose channel for this arm.
        self.assertEqual(result["lease_events"], {
            "receipts_issued": 4, "receipts_honored": 0, "invalidation_reruns": 0,
            "receipts_honored_prose": 4, "invalidation_reruns_prose": 1,
        })

    def test_both_compliant_arms_total_nine_distinct_events(self):
        import score_x5_leases as sx5

        with tempfile.TemporaryDirectory() as tmp:
            strict_result = sx5.lease_stats([_build_strict_compliant_transcript(tmp)])
            prose_result = sx5.lease_stats([_build_prose_compliant_transcript(tmp)])

        for name, result in (("strict", strict_result), ("prose", prose_result)):
            with self.subTest(arm=name):
                events = result["lease_events"]
                total = (events["receipts_issued"] + events["receipts_honored"]
                          + events["invalidation_reruns"] + events["receipts_honored_prose"]
                          + events["invalidation_reruns_prose"])
                self.assertEqual(total, 9, events)

    def test_guard_holds_in_both_arms_fresh_run_at_sha_4_present(self):
        # The mechanically required event: a `pytest tests/` invocation
        # actually happened at SHA_4 (Task 4's own corrected tree), not
        # merely a citation of the stale SHA_3 receipt.
        import score_x5_leases as sx5

        with tempfile.TemporaryDirectory() as tmp:
            strict_result = sx5.lease_stats([_build_strict_compliant_transcript(tmp)])
            prose_result = sx5.lease_stats([_build_prose_compliant_transcript(tmp)])

        for name, result in (("strict", strict_result), ("prose", prose_result)):
            with self.subTest(arm=name):
                sha4_runs = [r for r in result["verification_runs"]
                             if r["command_norm"] == FULL_SUITE and r["tree_sha"] == SHA[4]]
                self.assertEqual(len(sha4_runs), 1, "exactly one fresh run at SHA_4, the guard's own proof")


if __name__ == "__main__":
    unittest.main()
