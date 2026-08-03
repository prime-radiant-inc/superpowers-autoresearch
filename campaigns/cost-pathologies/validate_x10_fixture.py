#!/usr/bin/env python3
"""Validation for the cp-x10-consistency scenario (backlog campaign,
2026-08-02, Task 5): a fixture whose plan induces five real cross-module
consistency defects (seeded-truth-ledger.md) when its six tasks are
followed faithfully.

Per the controller ruling `cp-x1-edit-existing` and `cp-x1-wavecap`
operated under (their own test files' docstrings), this task spends no
containers or API budget on real reps. Instead this script constructs the
expected post-state mechanically -- `campaigns/cost-pathologies/fixtures/
cp-x10-consistency-outcomes/complete/` is a committed tree containing a
plausible, plan-literal implementation of all six tasks in
`scenarios/cp-x10-consistency/fixtures/docs/superpowers/plans/
job-queue-plan.md` -- and proves, against that tree and the scenario's own
pre-state `fixtures/`:

  1. The pre-state passes its own `pytest`, with none of the six tasks'
     output files present yet.
  2. The post-state passes its own `pytest` (all six modules plus the
     untouched `config.py`).
  3. Each of the five seeded defects (seeded-truth-ledger.md) is present
     in the post-state, per its own detection recipe, and not (falsely)
     detected in the pre-state, where the files it needs don't exist yet.

Usage: python3 validate_x10_fixture.py [-v]

Exits 0 if every property holds, 1 otherwise. Everything here is
synthetic; no real system.
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
SCENARIO_FIXTURES = HERE / "scenarios" / "cp-x10-consistency" / "fixtures"
COMPLETE = HERE / "fixtures" / "cp-x10-consistency-outcomes" / "complete"


def _read(tree_root, relpath):
    path = tree_root / relpath
    return path.read_text() if path.exists() else None


# ---------------------------------------------------------------------------
# Detectors -- implement seeded-truth-ledger.md's five "Detection recipe"
# sections literally, over a tree's own source text. Each returns:
#   True  -- the defect's seeded divergence is present.
#   False -- both required files exist but the divergence is absent (the
#            two sides agree, or the seeded literal isn't there).
#   None  -- not yet checkable (a required file doesn't exist in this tree).
# ---------------------------------------------------------------------------

_CONST_RE = {
    "TIMEOUT_SECONDS": re.compile(r"^TIMEOUT_SECONDS\s*=\s*(\d+)", re.M),
    "MIN_PRIORITY": re.compile(r"^MIN_PRIORITY\s*=\s*(\d+)", re.M),
}


def _module_constant(text, name):
    match = _CONST_RE[name].search(text)
    return int(match.group(1)) if match else None


def detect_defect_1_timeout_seconds_diverges(tree_root):
    notifier_text = _read(tree_root, "jobqueue/notifier.py")
    reporter_text = _read(tree_root, "jobqueue/reporter.py")
    if notifier_text is None or reporter_text is None:
        return None
    notifier_value = _module_constant(notifier_text, "TIMEOUT_SECONDS")
    reporter_value = _module_constant(reporter_text, "TIMEOUT_SECONDS")
    if notifier_value is None or reporter_value is None:
        return None
    return notifier_value != reporter_value


def detect_defect_2_retry_cap_naming_drift(tree_root):
    worker_text = _read(tree_root, "jobqueue/worker.py")
    scheduler_text = _read(tree_root, "jobqueue/scheduler.py")
    if worker_text is None or scheduler_text is None:
        return None
    has_retry_limit = bool(re.search(r"^RETRY_LIMIT\s*=\s*\d+", worker_text, re.M))
    has_max_retry_attempts = bool(re.search(r"^MAX_RETRY_ATTEMPTS\s*=\s*\d+", scheduler_text, re.M))
    return has_retry_limit and has_max_retry_attempts


_DEFECT3_WORKER_RE = re.compile(r'"job payload missing field \{[^}]*\}"')
_DEFECT3_API_RE = re.compile(r'"submission rejected: field \{[^}]*\} is required"')


def detect_defect_3_error_message_format_diverges(tree_root):
    worker_text = _read(tree_root, "jobqueue/worker.py")
    api_text = _read(tree_root, "jobqueue/api.py")
    if worker_text is None or api_text is None:
        return None
    worker_original = bool(_DEFECT3_WORKER_RE.search(worker_text))
    api_original = bool(_DEFECT3_API_RE.search(api_text))
    return worker_original and api_original


def detect_defect_4_retrying_status_unknown_elsewhere(tree_root):
    scheduler_text = _read(tree_root, "jobqueue/scheduler.py")
    notifier_text = _read(tree_root, "jobqueue/notifier.py")
    reporter_text = _read(tree_root, "jobqueue/reporter.py")
    if scheduler_text is None or notifier_text is None or reporter_text is None:
        return None
    scheduler_has_it = '"retrying"' in scheduler_text
    notifier_missing_it = '"retrying"' not in notifier_text
    reporter_missing_it = '"retrying"' not in reporter_text
    return scheduler_has_it and notifier_missing_it and reporter_missing_it


def detect_defect_5_min_priority_boundary_diverges(tree_root):
    worker_text = _read(tree_root, "jobqueue/worker.py")
    api_text = _read(tree_root, "jobqueue/api.py")
    if worker_text is None or api_text is None:
        return None
    worker_value = _module_constant(worker_text, "MIN_PRIORITY")
    api_value = _module_constant(api_text, "MIN_PRIORITY")
    if worker_value is None or api_value is None:
        return None
    return worker_value != api_value


DETECTORS = {
    "DEFECT-1": detect_defect_1_timeout_seconds_diverges,
    "DEFECT-2": detect_defect_2_retry_cap_naming_drift,
    "DEFECT-3": detect_defect_3_error_message_format_diverges,
    "DEFECT-4": detect_defect_4_retrying_status_unknown_elsewhere,
    "DEFECT-5": detect_defect_5_min_priority_boundary_diverges,
}


def run_pytest(tree_root):
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=tree_root,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0, result.stdout + result.stderr


def main(argv):
    verbose = "-v" in argv
    ok = True

    print(f"pre-state pytest ({SCENARIO_FIXTURES}):")
    pre_ok, pre_output = run_pytest(SCENARIO_FIXTURES)
    print(f"  {'PASS' if pre_ok else 'FAIL'}")
    if verbose or not pre_ok:
        print(pre_output)
    ok = ok and pre_ok

    print(f"post-state pytest ({COMPLETE}):")
    post_ok, post_output = run_pytest(COMPLETE)
    print(f"  {'PASS' if post_ok else 'FAIL'}")
    if verbose or not post_ok:
        print(post_output)
    ok = ok and post_ok

    print("seeded defects, pre-state (expect: not (falsely) detected):")
    for defect_id, detector in DETECTORS.items():
        result = detector(SCENARIO_FIXTURES)
        status = "not-checkable (expected)" if result is None else f"UNEXPECTED: {result}"
        print(f"  {defect_id}: {status}")
        if result is not None:
            ok = False

    print("seeded defects, post-state (expect: all True):")
    detected_count = 0
    for defect_id, detector in DETECTORS.items():
        result = detector(COMPLETE)
        print(f"  {defect_id}: {result}")
        if result is True:
            detected_count += 1
        else:
            ok = False

    print(f"\n{detected_count}/{len(DETECTORS)} seeded defects detected in post-state.")
    if detected_count < 5:
        ok = False

    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
