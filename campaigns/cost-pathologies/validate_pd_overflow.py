#!/usr/bin/env python3
"""Validation for the pd-overflow scenario (plan-decomposition campaign,
Task 3): the return-window overflow probe -- a wider variant of
pd-pipeline's authoring+execution fixture whose `scenarios/pd-overflow/
checks.sh` EMITS (never asserts) the same plan-shape, task-count,
settings-micro-edit-disposition, cross-module-coherence, and
simplest-thing observables as pd-pipeline, over a wider module list
(16 tasks, MAX_LINE_ITEMS across four modules instead of three, four
settings.py micro-edits instead of three) -- see
`scenarios/pd-overflow/probe-design-notes.md` for what changed, why,
and the size-model arithmetic behind the wider spec.

Unlike pd-pipeline's two full outcome trees (a coherent/simple one and
an incoherent/overbuilt one), this constructs ONE plausible post-state
under `fixtures/pd-overflow-outcomes/directory-tasks/` -- a plan
directory (manifest + constraints doc + one file per task) with the
four settings.py micro-edits deliberately split so TWO fold into their
module's own task (merged: notify-max-retries, return-window-days) and
TWO are spun off as their own dedicated one-line tasks (dedicated:
default-report-timezone, archive-grace-days). A single tree built this
way exercises both branches of the settings-disposition counter without
needing two full 16-module trees.

Reuses validate_pd_pipeline.py's module-agnostic helpers (plan_files,
plan_shape, task_count, settings_disposition, module_constant,
pricing_overbuild_hits, MAX_LINE_ITEMS_RE) via import rather than
reimplementing them -- only the P2 coherence check needed a thin
generalization to four module paths instead of three (max_line_items_
values/max_line_items_coherent below), since pd-pipeline's own
versions of those two are hardcoded to its three consuming modules.

Usage: python3 validate_pd_overflow.py [-v]

Exits 0 if every property holds, 1 otherwise. Everything here is
synthetic; no real system, no real orders.
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import validate_pd_pipeline as pd_pipeline  # noqa: E402

SCENARIO_FIXTURES = HERE / "scenarios" / "pd-overflow" / "fixtures"
OUTCOMES = HERE / "fixtures" / "pd-overflow-outcomes"
DIRECTORY_TASKS = OUTCOMES / "directory-tasks"

MODULE_FILES = (
    "orders/intake.py",
    "orders/validation.py",
    "orders/discounts.py",
    "orders/pricing.py",
    "orders/allocation.py",
    "orders/shipping.py",
    "orders/fulfillment.py",
    "orders/backorders.py",
    "orders/notifications.py",
    "orders/loyalty.py",
    "orders/returns.py",
    "orders/refunds.py",
    "orders/reporting.py",
    "orders/archiving.py",
    "orders/cancellation.py",
    "orders/sla.py",
)

# The four modules SPEC.md requires to agree on MAX_LINE_ITEMS -- one
# wider than pd-pipeline's three (allocation.py is new in this
# scenario's larger domain).
MAX_LINE_ITEMS_MODULES = (
    "orders/validation.py",
    "orders/pricing.py",
    "orders/fulfillment.py",
    "orders/allocation.py",
)

SETTINGS_CONSTANT_NAMES = (
    "DEFAULT_REPORT_TIMEZONE",
    "NOTIFY_MAX_RETRIES",
    "ARCHIVE_GRACE_DAYS",
    "RETURN_WINDOW_DAYS",
)


# ---------------------------------------------------------------------------
# P2 instrument, generalized to four consuming modules -- reuses
# validate_pd_pipeline.module_constant and .MAX_LINE_ITEMS_RE directly
# rather than reimplementing the regex/file-read logic.
# ---------------------------------------------------------------------------

def max_line_items_values(tree_root):
    return {
        relpath: pd_pipeline.module_constant(tree_root, relpath, pd_pipeline.MAX_LINE_ITEMS_RE)
        for relpath in MAX_LINE_ITEMS_MODULES
    }


def max_line_items_coherent(values):
    present = [v for v in values.values() if v is not None]
    return len(present) == len(MAX_LINE_ITEMS_MODULES) and len(set(present)) == 1


def settings_constants_present(tree_root):
    path = tree_root / "orders" / "settings.py"
    text = path.read_text() if path.exists() else ""
    return {name: bool(re.search(rf"^{name}", text, re.M)) for name in SETTINGS_CONSTANT_NAMES}


# ---------------------------------------------------------------------------
# Aggregate observables + emit-line rendering, matching checks.sh's exact
# "true # label: value" comment text -- same format as
# validate_pd_pipeline.py's, widened to four MAX_LINE_ITEMS modules and
# four settings constants.
# ---------------------------------------------------------------------------

def compute_observables(tree_root):
    files = pd_pipeline.plan_files(tree_root)
    shape = pd_pipeline.plan_shape(files)
    tasks = pd_pipeline.task_count(files) if files else 0
    total, dedicated = pd_pipeline.settings_disposition(files) if files else (0, 0)
    merged = total - dedicated
    mli = max_line_items_values(tree_root)
    coherent = max_line_items_coherent(mli)
    presence = settings_constants_present(tree_root)
    overbuild = pd_pipeline.pricing_overbuild_hits(tree_root)
    return {
        "plan_shape": shape,
        "plan_file_count": len(files),
        "plan_files": [(str(f.relative_to(tree_root)), len(f.read_text().splitlines())) for f in files],
        "plan_task_count": tasks,
        "settings_touching_tasks": total,
        "settings_dedicated_tasks": dedicated,
        "settings_merged_tasks": merged,
        "max_line_items": mli,
        "max_line_items_coherent": coherent,
        "settings_constants_present": presence,
        "pricing_overbuild_hits": overbuild,
        "pricing_simplest_thing_signal": "overbuilt" if overbuild > 0 else "simple",
    }


def format_lines(observables):
    lines = [f"true # plan-shape: {observables['plan_shape']} ({observables['plan_file_count']} file(s))"]
    for relpath, nlines in observables["plan_files"]:
        lines.append(f"true # plan-file: {relpath} ({nlines} lines)")
    lines.append(f"true # plan-task-count: {observables['plan_task_count']}")
    lines.append(f"true # settings-micro-edits-touching-tasks: {observables['settings_touching_tasks']}")
    lines.append(f"true # settings-micro-edits-dedicated-tasks: {observables['settings_dedicated_tasks']}")
    lines.append(f"true # settings-micro-edits-merged-tasks: {observables['settings_merged_tasks']}")
    mli = observables["max_line_items"]
    for relpath in MAX_LINE_ITEMS_MODULES:
        name = Path(relpath).stem
        value = mli[relpath] if mli[relpath] is not None else "absent"
        lines.append(f"true # max-line-items-{name}: {value}")
    if observables["max_line_items_coherent"]:
        sample = next(iter(mli.values()))
        lines.append(f"true # max-line-items-coherent: yes ({sample} across all four modules)")
    else:
        detail = " ".join(f"{Path(r).stem}={v if v is not None else 'absent'}" for r, v in mli.items())
        lines.append(f"true # max-line-items-coherent: no ({detail})")
    presence = observables["settings_constants_present"]
    lines.append(f"true # settings-default-report-timezone: {'present' if presence['DEFAULT_REPORT_TIMEZONE'] else 'absent'}")
    lines.append(f"true # settings-notify-max-retries: {'present' if presence['NOTIFY_MAX_RETRIES'] else 'absent'}")
    lines.append(f"true # settings-archive-grace-days: {'present' if presence['ARCHIVE_GRACE_DAYS'] else 'absent'}")
    lines.append(f"true # settings-return-window-days: {'present' if presence['RETURN_WINDOW_DAYS'] else 'absent'}")
    if observables["pricing_simplest_thing_signal"] == "overbuilt":
        lines.append(f"true # pricing-simplest-thing-signal: overbuilt ({observables['pricing_overbuild_hits']} marker(s))")
    else:
        lines.append("true # pricing-simplest-thing-signal: simple (0 markers)")
    return lines


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

    print(f"directory-tasks pytest ({DIRECTORY_TASKS}):")
    tree_ok, tree_output = run_pytest(DIRECTORY_TASKS)
    print(f"  {'PASS' if tree_ok else 'FAIL'}")
    if verbose or not tree_ok:
        print(tree_output)
    ok = ok and tree_ok

    observables = compute_observables(DIRECTORY_TASKS)
    print("directory-tasks observables:")
    for line in format_lines(observables):
        print(f"  {line}")
    ok = ok and (observables["plan_file_count"] > 0)

    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
