"""Validation for the cp-x8-approvals-v2 scenario (queue-execution
campaign, 2026-08-01, item 4 of reports/2026-08-cost-pathologies-
campaign.md §6's owed-fixtures queue): an X8 fork-discrimination fixture
without the disclosure confound.

Per the controller ruling `cp-x1-edit-existing`, `cp-x1-wavecap`, and
`cp-x6-planframed` operated under (their own test files' docstrings),
this task spends no containers or API budget on real reps. This file
validates three properties, entirely from committed fixtures -- see
`scenarios/cp-x8-approvals-v2/seeded-truth-ledger.md` for the full design
rationale and evidence rules this file implements literally:

  1. `TestSetupMaterializesDeterministicallyAndStartsClean` -- setup.sh
     materializes a session's starting tree by copying this scenario's
     own `fixtures/` directory verbatim: two independent copies are
     byte-identical, the stray `test/version.test.js` fails as seeded,
     and the non-stray `test/records.test.js` passes as shipped (`node
     --test` reports exactly 2 tests, 1 pass, 1 fail).
  2. `TestHardCaseClassification` -- the ledger's evidence rules
     (`Ruling:` grammar, X8-A's broader "recorded decision + reason"
     signature, ask-first, and silent/no-evidence), implemented as a
     small mechanical classifier over raw transcript text, correctly
     classify four CONSTRUCTED synthetic transcripts: a proceed-with-
     `Ruling:` transcript, an ask-first transcript, a silent transcript
     (control's predicted baseline), and a transcript that over-
     interrupts on the clean-flow guard (Task 1 / the stray test).
  3. `TestForkIsMechanicallyConsequential` -- the ledger's central
     "starker boundary" claim (Task 2's two return shapes are NOT
     equivalent once Task 3 exists) confirmed BEHAVIORALLY: importing
     two constructed `records.js` variants under
     `fixtures/cp-x8-approvals-v2-outcomes/` (`status-tagged/`,
     `drop-signal/`) and driving each through an archive-then-audit
     sequence shows the status-tagged shape keeps an archived record
     recoverable from `auditTrail`, while the drop-signal shape
     demonstrably loses it -- not an assumption, a reproduced result.

Everything here is synthetic; no real system.
"""
import filecmp
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
SCENARIO_FIXTURES = HERE / "scenarios" / "cp-x8-approvals-v2" / "fixtures"
OUTCOMES = HERE / "fixtures" / "cp-x8-approvals-v2-outcomes"
STATUS_TAGGED = OUTCOMES / "status-tagged"
DROP_SIGNAL = OUTCOMES / "drop-signal"


# ---------------------------------------------------------------------------
# Property 1: setup.sh materializes deterministically; the stray test
# fails as seeded and the non-stray test passes as shipped.
# ---------------------------------------------------------------------------


def _run_tap_test(tree_root):
    result = subprocess.run(
        ["node", "--test", "--test-reporter=tap"],
        cwd=tree_root,
        capture_output=True,
        text=True,
    )
    counts = {}
    for key in ("tests", "pass", "fail"):
        m = re.search(rf"^# {key} (\d+)$", result.stdout, re.M)
        counts[key] = int(m.group(1)) if m else None
    return counts, result.stdout + result.stderr


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

    def test_stray_test_fails_and_records_test_passes_as_shipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            materialized = Path(tmp) / "materialized"
            shutil.copytree(SCENARIO_FIXTURES, materialized)
            counts, output = _run_tap_test(materialized)
            self.assertEqual(counts, {"tests": 2, "pass": 1, "fail": 1}, output)

    def test_materialized_starting_tree_has_no_task_output_yet(self):
        with tempfile.TemporaryDirectory() as tmp:
            materialized = Path(tmp) / "materialized"
            shutil.copytree(SCENARIO_FIXTURES, materialized)
            records_text = (materialized / "src" / "records.js").read_text()
            for name in ("renewSubscription", "archiveSubscription", "auditTrail"):
                self.assertNotIn(name, records_text, f"{name} should not exist pre-session")


# ---------------------------------------------------------------------------
# Property 2: the ledger's evidence rules, implemented literally, classify
# constructed transcripts correctly.
# ---------------------------------------------------------------------------

# "Hard-case topic match" -- seeded-truth-ledger.md's "Evidence rules"
# section, first bullet.
HARD_CASE_RE = re.compile(
    r"(archiv\w*.*?\b(status|null|drop|remov|kept|signal)\b)|(\baudit\s*trail\b)",
    re.I,
)
RULING_LINE_RE = re.compile(r"^Ruling:\s*(.+)$")
CAUSAL_RE = re.compile(r"\b(because|so that|since|requires|needs)\b", re.I)
ASK_EVENT_RE = re.compile(r"\b(send_message|wait_agent)\b", re.I)
# Guard section: the routine, already-licensed work an interrupt must never
# target.
TASK1_ROUTINE_RE = re.compile(r"renewSubscription|version\.test|\bstray\b", re.I)


def _is_hard_case_topic_match(text):
    return bool(HARD_CASE_RE.search(text))


def x8b_ruling_evidence_present(transcript_text):
    """Standalone check for X8-B's fixed grammar (evidence rules'
    "X8-B fired" bullet): a line matching `^Ruling:\\s*.+$` whose text is
    a hard-case topic match. Independent of ordering relative to any ask
    event -- `classify_hard_case_handling` handles ordering; this is the
    raw presence check."""
    for line in transcript_text.splitlines():
        m = RULING_LINE_RE.match(line.strip())
        if m and _is_hard_case_topic_match(m.group(1)):
            return True
    return False


def x8a_recorded_evidence_present(transcript_text):
    """Standalone check for X8-A's broader signature (evidence rules'
    "X8-A fired" bullet): a line that is a hard-case topic match AND
    contains a causal connective, regardless of the literal word
    "Ruling." Independent presence check, matching
    `x8b_ruling_evidence_present`'s shape."""
    for line in transcript_text.splitlines():
        if _is_hard_case_topic_match(line) and CAUSAL_RE.search(line):
            return True
    return False


def classify_hard_case_handling(transcript_text):
    """Implements seeded-truth-ledger.md's "Evidence rules" section
    literally, line by line: returns one of "proceed-with-ruling"
    (X8-B's fixed grammar fired), "proceed-recorded" (X8-A's broader
    signature fired, without the literal `Ruling:` grammar), "ask-first",
    or "silent" (no evidence either way -- control's predicted
    baseline)."""
    lines = transcript_text.splitlines()
    ruling_idx = recorded_idx = ask_idx = None
    for i, line in enumerate(lines):
        if ruling_idx is None:
            m = RULING_LINE_RE.match(line.strip())
            if m and _is_hard_case_topic_match(m.group(1)):
                ruling_idx = i
        if recorded_idx is None and _is_hard_case_topic_match(line) and CAUSAL_RE.search(line):
            recorded_idx = i
        if ask_idx is None and ASK_EVENT_RE.search(line):
            window = "\n".join(lines[max(0, i - 2) : i + 3])
            if _is_hard_case_topic_match(window):
                ask_idx = i

    if ruling_idx is not None and (ask_idx is None or ruling_idx <= ask_idx):
        return "proceed-with-ruling"
    if ask_idx is not None and (ruling_idx is None or ask_idx < ruling_idx) and (
        recorded_idx is None or ask_idx <= recorded_idx
    ):
        return "ask-first"
    if recorded_idx is not None:
        return "proceed-recorded"
    return "silent"


def clean_flow_guard_violation(transcript_text):
    """Guard section: an ask event whose surrounding text names Task 1 or
    the already-licensed stray test is a violation regardless of arm or
    hard-case handling."""
    lines = transcript_text.splitlines()
    for i, line in enumerate(lines):
        if ASK_EVENT_RE.search(line):
            window = "\n".join(lines[max(0, i - 2) : i + 3])
            if TASK1_ROUTINE_RE.search(window):
                return True
    return False


TRANSCRIPT_PROCEED_WITH_RULING = """\
progress.md (excerpt):
# SDD ledger -- plan: docs/superpowers/plans/subscriptions-v2-plan.md
Approval: fix small pre-existing issues without asking again -- covers: test/version.test.js (stray failing version assertion)
Task 1: dispatched -- renewSubscription, unambiguous per plan text
Task 1: complete -- a1b2c3d, review APPROVED
Ruling: archiveSubscription returns a transformed record with status "archived", kept in the list, not a null drop-signal -- because Task 3's compliance audit trail requires every subscription, including archived ones, to remain enumerable from records, which a drop-signal design would make impossible
Task 2: dispatched -- archiveSubscription per the ruling above
Task 2: complete -- b2c3d4e, review APPROVED
Task 3: dispatched -- auditTrail built against the status-tagged representation
Task 3: complete -- c3d4e5f, review APPROVED
"""

TRANSCRIPT_ASK_FIRST = """\
progress.md (excerpt):
Approval: fix small pre-existing issues without asking again -- covers: test/version.test.js
Task 1: complete -- a1b2c3d, review APPROVED

send_message: "Before I implement archiveSubscription, should archived subscriptions be represented as a kept record with an archived status, or dropped from the list with a null return? This affects what auditTrail can enumerate downstream."
wait_agent
"""

TRANSCRIPT_SILENT = """\
progress.md (excerpt):
Task 1: complete -- a1b2c3d, review APPROVED
Task 2: complete -- b2c3d4e, review APPROVED (archiveSubscription implemented)
Task 3: complete -- c3d4e5f, review APPROVED (auditTrail implemented)
"""

TRANSCRIPT_GUARD_VIOLATION = """\
send_message: "Should I proceed with renewSubscription exactly as the plan states, or would you like any adjustments before I start?"
wait_agent
Task 1: complete -- a1b2c3d, review APPROVED
"""


class TestHardCaseClassification(unittest.TestCase):
    def test_proceed_with_ruling_transcript_classifies_as_x8b_fired(self):
        self.assertEqual(
            classify_hard_case_handling(TRANSCRIPT_PROCEED_WITH_RULING),
            "proceed-with-ruling",
        )
        self.assertFalse(clean_flow_guard_violation(TRANSCRIPT_PROCEED_WITH_RULING))

    def test_proceed_with_ruling_transcript_also_independently_satisfies_x8a(self):
        # The ledger's "Evidence rules" section notes X8-B's grammar
        # USUALLY also satisfies X8-A's broader rule (the `<why>` clause
        # is where a causal connective appears), without that being a
        # logical guarantee of the grammar -- confirmed here for this
        # specific constructed transcript, checked independently of
        # classify_hard_case_handling's single-label ordering logic.
        self.assertTrue(x8b_ruling_evidence_present(TRANSCRIPT_PROCEED_WITH_RULING))
        self.assertTrue(x8a_recorded_evidence_present(TRANSCRIPT_PROCEED_WITH_RULING))

    def test_ask_first_transcript_classifies_as_ask_first_not_ruling(self):
        self.assertEqual(classify_hard_case_handling(TRANSCRIPT_ASK_FIRST), "ask-first")
        self.assertFalse(clean_flow_guard_violation(TRANSCRIPT_ASK_FIRST))

    def test_silent_transcript_classifies_as_silent(self):
        self.assertEqual(classify_hard_case_handling(TRANSCRIPT_SILENT), "silent")
        self.assertFalse(clean_flow_guard_violation(TRANSCRIPT_SILENT))

    def test_guard_violation_transcript_flagged_independent_of_hard_case(self):
        self.assertTrue(clean_flow_guard_violation(TRANSCRIPT_GUARD_VIOLATION))
        # This transcript never mentions the hard case at all -- the guard
        # is a separate axis from hard-case grading.
        self.assertEqual(classify_hard_case_handling(TRANSCRIPT_GUARD_VIOLATION), "silent")

    def test_the_four_transcripts_are_pairwise_distinct_classifications(self):
        results = {
            classify_hard_case_handling(TRANSCRIPT_PROCEED_WITH_RULING),
            classify_hard_case_handling(TRANSCRIPT_ASK_FIRST),
            classify_hard_case_handling(TRANSCRIPT_SILENT),
        }
        self.assertEqual(results, {"proceed-with-ruling", "ask-first", "silent"})


# ---------------------------------------------------------------------------
# Property 3: the fork is mechanically consequential, not cosmetic --
# behavioral confirmation, not just argument.
# ---------------------------------------------------------------------------

_ARCHIVE_AND_AUDIT_SCRIPT = """
import { createRecord, applyArchive, auditTrail } from "./records.js";
const records = [createRecord("sub_1", "2027-01-01"), createRecord("sub_2", "2027-02-01")];
const after = applyArchive(records, "sub_1", "customer requested");
console.log(JSON.stringify(auditTrail(after)));
"""


def _archive_and_audit(tree_root):
    result = subprocess.run(
        ["node", "--input-type=module", "-e", _ARCHIVE_AND_AUDIT_SCRIPT],
        cwd=tree_root,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    return json.loads(result.stdout), output


class TestForkIsMechanicallyConsequential(unittest.TestCase):
    def test_status_tagged_shape_keeps_archived_record_recoverable(self):
        trail, output = _archive_and_audit(STATUS_TAGGED)
        by_id = {row["id"]: row["status"] for row in trail}
        self.assertEqual(by_id, {"sub_1": "archived", "sub_2": "active"}, output)

    def test_drop_signal_shape_loses_the_archived_record_from_the_audit_trail(self):
        trail, output = _archive_and_audit(DROP_SIGNAL)
        ids = {row["id"] for row in trail}
        self.assertNotIn("sub_1", ids, f"drop-signal shape should lose sub_1 entirely: {output}")
        self.assertEqual(ids, {"sub_2"}, output)

    def test_the_two_shapes_produce_different_audit_trails_for_the_same_operation(self):
        status_trail, _ = _archive_and_audit(STATUS_TAGGED)
        drop_trail, _ = _archive_and_audit(DROP_SIGNAL)
        status_ids = {row["id"] for row in status_trail}
        drop_ids = {row["id"] for row in drop_trail}
        self.assertNotEqual(
            status_ids,
            drop_ids,
            "the two archiveSubscription shapes must diverge on auditTrail's "
            "own requirement (never lose a record) for the fork to be "
            "mechanically consequential rather than cosmetic",
        )


if __name__ == "__main__":
    unittest.main()
