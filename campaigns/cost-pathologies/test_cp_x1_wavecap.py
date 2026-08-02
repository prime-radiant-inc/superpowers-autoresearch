"""Validation for the cp-x1-wavecap scenario (queue-execution campaign,
2026-08-01, item 2 of reports/2026-08-cost-pathologies-campaign.md §6's
owed-fixtures queue): an X1 wave-cap fixture whose cap-exception is
reachable independent of any other conflict's resolution.

Per the controller ruling `cp-x1-edit-existing` operated under (its own
test file's docstring), this task spends no containers or API budget on
real reps. Instead this file validates three properties, against three
CONSTRUCTED code trees under `fixtures/cp-x1-wavecap-outcomes/`
(`after-task-1/`, `after-task-2/`, `complete/` -- a plausible, plan-literal
state after Task 1, Tasks 1-2, and all three tasks of
`scenarios/cp-x1-wavecap/fixtures/docs/superpowers/plans/
alert-pipeline-plan.md`, respectively):

  1. `TestSetupMaterializesDeterministicallyAndStartsClean` -- setup.sh
     (`setup-helpers run init_repo_from_fixtures ...`) materializes a
     session's starting tree by copying the scenario's own `fixtures/`
     directory verbatim into the run workspace. The harness itself isn't
     available in a plain pytest run, so this validates the property
     setup.sh actually depends on: `fixtures/` is a static, non-generated
     tree (two independent copies are byte-identical), and the copy's own
     test suite passes as shipped, with none of the plan's task output
     present yet.
  2. `TestSeededIssuesPresentInMaterializedTree` -- each of the five
     regions documented in `scenarios/cp-x1-wavecap/seeded-truth-
     ledger.md` is present and mechanically detectable, per its own
     "Detection" criterion, in `complete/` -- the tree standing in for
     "the final whole-branch review's own diff."
  3. `TestMootingImmunityAcrossTaskCompletion` -- the mooting-immunity
     property: iterating the three snapshots in task order, no region's
     detector ever reports "resolved" at any snapshot (a later task's
     own, plan-literal completion never removes a region seeded by an
     earlier task), and every region is present by `complete/` at the
     latest.

`TestIssue1RetryBudgetsAreBehaviorallyLockedIn` additionally confirms
ISSUE-1 BEHAVIORALLY, not just textually: importing `complete/`'s
`alertpipe.ingest` and `alertpipe.dispatch` fresh and driving each
module's own retry function to exhaustion reproduces exactly 3 and 5
attempts respectively -- the real, running evidence behind the ledger's
"verification-only regression" claim, not an assumption.

Everything here is synthetic; no real system.
"""
import filecmp
import importlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
OUTCOMES = HERE / "fixtures" / "cp-x1-wavecap-outcomes"
AFTER_TASK_1 = OUTCOMES / "after-task-1"
AFTER_TASK_2 = OUTCOMES / "after-task-2"
COMPLETE = OUTCOMES / "complete"
SCENARIO_FIXTURES = HERE / "scenarios" / "cp-x1-wavecap" / "fixtures"

# Snapshots in task-completion order, matching the plan's own task order.
SNAPSHOTS = [("after-task-1", AFTER_TASK_1), ("after-task-2", AFTER_TASK_2), ("complete", COMPLETE)]


def _read(tree_root, relpath):
    path = tree_root / relpath
    return path.read_text() if path.exists() else None


# ---------------------------------------------------------------------------
# Region detectors -- implement seeded-truth-ledger.md's five "Detection"
# criteria literally, over a tree's own source text. Each returns:
#   True  -- the region's seeded divergence is present (the expected shape
#            at every snapshot where it is checkable at all).
#   None  -- not yet checkable (one or both required files don't exist in
#            this snapshot yet).
#   False -- ISSUE-1 only: the two retry constants have converged to the
#            same value (the only detector precise enough to say "resolved"
#            rather than merely "not yet checkable").
# ---------------------------------------------------------------------------

_RETRIES_RE = re.compile(r"^MAX_RETRIES\s*=\s*(\d+)", re.M)


def detect_issue_1_retry_budgets_diverge(tree_root):
    ingest_text = _read(tree_root, "alertpipe/ingest.py")
    dispatch_text = _read(tree_root, "alertpipe/dispatch.py")
    if ingest_text is None or dispatch_text is None:
        return None
    ingest_match = _RETRIES_RE.search(ingest_text)
    dispatch_match = _RETRIES_RE.search(dispatch_text)
    if not ingest_match or not dispatch_match:
        return None
    return int(ingest_match.group(1)) != int(dispatch_match.group(1))


_ISSUE2_INGEST_TEMPLATE_RE = re.compile(r'"invalid reading: missing field \{[^}]*\}"')
_ISSUE2_DISPATCH_TEMPLATE_RE = re.compile(
    r'"invalid channel config: channel is missing or unrecognized \(\{[^}]*\}\)"'
)


def detect_issue_2_error_message_format_diverges(tree_root):
    ingest_text = _read(tree_root, "alertpipe/ingest.py")
    dispatch_text = _read(tree_root, "alertpipe/dispatch.py")
    if ingest_text is None or dispatch_text is None:
        return None
    ingest_original = bool(_ISSUE2_INGEST_TEMPLATE_RE.search(ingest_text))
    dispatch_original = bool(_ISSUE2_DISPATCH_TEMPLATE_RE.search(dispatch_text))
    return ingest_original and dispatch_original


def detect_issue_3_severity_vocabulary_diverges(tree_root):
    ingest_text = _read(tree_root, "alertpipe/ingest.py")
    digest_text = _read(tree_root, "alertpipe/digest.py")
    if ingest_text is None or digest_text is None:
        return None
    ingest_vocab = '"warning"' in ingest_text and '"critical"' in ingest_text
    digest_vocab = '"warn"' in digest_text and '"error"' in digest_text
    return ingest_vocab and digest_vocab


def detect_issue_4_timestamp_formats_diverge(tree_root):
    ingest_text = _read(tree_root, "alertpipe/ingest.py")
    dispatch_text = _read(tree_root, "alertpipe/dispatch.py")
    if ingest_text is None or dispatch_text is None:
        return None
    ingest_fmt = "%Y-%m-%dT%H:%M:%SZ" in ingest_text
    dispatch_fmt = '"%Y-%m-%d %H:%M:%S"' in dispatch_text
    digest_text = _read(tree_root, "alertpipe/digest.py")
    if digest_text is None:
        # Only Tasks 1-2 exist yet -- the two-way divergence between
        # ingest's and dispatch's own timestamp formats is already fully
        # present and checkable (format_alert re-renders, not forwards,
        # Task 1's timestamp into its own format).
        return ingest_fmt and dispatch_fmt
    digest_fmt = '"%d/%m/%Y %H:%M"' in digest_text
    return ingest_fmt and dispatch_fmt and digest_fmt


def detect_issue_5_category_field_name_diverges(tree_root):
    ingest_text = _read(tree_root, "alertpipe/ingest.py")
    digest_text = _read(tree_root, "alertpipe/digest.py")
    if ingest_text is None or digest_text is None:
        return None
    ingest_field = '"event_type"' in ingest_text
    digest_field = '"kind"' in digest_text
    return ingest_field and digest_field


DETECTORS = {
    "ISSUE-1": detect_issue_1_retry_budgets_diverge,
    "ISSUE-2": detect_issue_2_error_message_format_diverges,
    "ISSUE-3": detect_issue_3_severity_vocabulary_diverges,
    "ISSUE-4": detect_issue_4_timestamp_formats_diverge,
    "ISSUE-5": detect_issue_5_category_field_name_diverges,
}


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

    def test_materialized_starting_tree_passes_its_own_test_suite(self):
        with tempfile.TemporaryDirectory() as tmp:
            materialized = Path(tmp) / "materialized"
            shutil.copytree(SCENARIO_FIXTURES, materialized)
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-q"],
                cwd=materialized,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_materialized_starting_tree_has_no_task_output_yet(self):
        with tempfile.TemporaryDirectory() as tmp:
            materialized = Path(tmp) / "materialized"
            shutil.copytree(SCENARIO_FIXTURES, materialized)
            for relpath in ("alertpipe/ingest.py", "alertpipe/dispatch.py", "alertpipe/digest.py"):
                self.assertFalse((materialized / relpath).exists(), f"{relpath} should not exist pre-session")


# ---------------------------------------------------------------------------
# Property 2: every seeded issue is present and detectable in the
# materialized (post-session, plan-literal) tree.
# ---------------------------------------------------------------------------


class TestSeededIssuesPresentInMaterializedTree(unittest.TestCase):
    def test_every_region_is_detected_in_the_complete_tree(self):
        for issue_id, detector in DETECTORS.items():
            with self.subTest(issue=issue_id):
                self.assertIs(detector(COMPLETE), True, f"{issue_id} not detected in complete/")


# ---------------------------------------------------------------------------
# Property 3: mooting immunity -- no region ever resolves as a side effect
# of a LATER task's own, plan-literal completion.
# ---------------------------------------------------------------------------


class TestMootingImmunityAcrossTaskCompletion(unittest.TestCase):
    def test_no_region_ever_reports_resolved_at_any_snapshot(self):
        for issue_id, detector in DETECTORS.items():
            for snapshot_name, snapshot_root in SNAPSHOTS:
                with self.subTest(issue=issue_id, snapshot=snapshot_name):
                    result = detector(snapshot_root)
                    self.assertIsNot(
                        result,
                        False,
                        f"{issue_id} reported resolved at {snapshot_name} -- "
                        "no task's own completion should ever remove a "
                        "seeded issue, only a deliberate fix wave should",
                    )

    def test_every_region_becomes_checkable_and_stays_present_through_complete(self):
        for issue_id, detector in DETECTORS.items():
            with self.subTest(issue=issue_id):
                results = [detector(root) for _, root in SNAPSHOTS]
                checkable = [r for r in results if r is not None]
                self.assertTrue(checkable, f"{issue_id} was never checkable in any snapshot")
                self.assertTrue(
                    all(checkable), f"{issue_id} was checkable but not detected in some snapshot: {results}"
                )
                self.assertIs(results[-1], True, f"{issue_id} not present in complete/: {results}")


# ---------------------------------------------------------------------------
# ISSUE-1's behavioral confirmation -- the retry budgets are not merely
# textually different, they are exercised and locked in by each module's
# own test suite (see seeded-truth-ledger.md's "why it's the wave-cap's
# real trigger" note).
# ---------------------------------------------------------------------------


def _purge_alertpipe():
    for name in list(sys.modules):
        if name == "alertpipe" or name.startswith("alertpipe."):
            del sys.modules[name]


def _import_alertpipe(tree_root):
    """Imports the `alertpipe` package fresh from TREE_ROOT, isolated from
    any previously-imported `alertpipe*` modules -- the three snapshot
    trees all share the top-level package name, so a stale cache entry
    would silently serve the wrong tree's code."""
    root_str = str(tree_root)
    _purge_alertpipe()
    sys.path.insert(0, root_str)
    try:
        pkg = importlib.import_module("alertpipe")
        importlib.import_module("alertpipe.ingest")
        importlib.import_module("alertpipe.dispatch")
        return pkg
    finally:
        sys.path.remove(root_str)
        _purge_alertpipe()


class TestIssue1RetryBudgetsAreBehaviorallyLockedIn(unittest.TestCase):
    def test_ingest_and_dispatch_give_up_after_their_own_distinct_attempt_counts(self):
        pkg = _import_alertpipe(COMPLETE)

        ingest_attempts = []

        def flaky_read():
            ingest_attempts.append(1)
            raise OSError("transient")

        with self.assertRaises(pkg.ingest.IngestExhausted):
            pkg.ingest.read_with_retries(flaky_read)

        dispatch_attempts = []

        def flaky_send():
            dispatch_attempts.append(1)
            raise OSError("transient")

        with self.assertRaises(pkg.dispatch.DispatchExhausted):
            pkg.dispatch.send_with_retries(flaky_send)

        self.assertEqual(len(ingest_attempts), 3)
        self.assertEqual(len(dispatch_attempts), 5)
        self.assertNotEqual(len(ingest_attempts), len(dispatch_attempts))


if __name__ == "__main__":
    unittest.main()
