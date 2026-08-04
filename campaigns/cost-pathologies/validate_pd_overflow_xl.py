#!/usr/bin/env python3
"""Validation for the pd-overflow-xl scenario (plan-decomposition
campaign, overflow-probe expansion): the CERTIFIED return-window
overflow probe -- a wider variant of `pd-overflow`'s authoring+execution
fixture whose `scenarios/pd-overflow-xl/checks.sh` EMITS (never asserts)
the same plan-shape, task-count, settings-micro-edit-disposition,
cross-module-coherence, and simplest-thing observables as `pd-overflow`,
over a wider module list spanning THREE subsystems (32 tasks,
MAX_LINE_ITEMS across six modules instead of four, six settings.py
micro-edits instead of four) -- see `scenarios/pd-overflow-xl/
probe-design-notes.md` for what changed, why, and the size-model
arithmetic behind the wider spec (the model that certifies this spec's
faithful monolithic plan exceeds a single model write's output budget,
unlike `pd-overflow`'s own honest-but-inconclusive model).

Unlike `pd-pipeline`'s two full outcome trees, and matching
`pd-overflow`'s own single-tree approach, this constructs ONE plausible
post-state under `fixtures/pd-overflow-xl-outcomes/directory-tasks/` --
a plan directory (manifest + constraints doc + one file per task) with
the six settings.py micro-edits split so THREE fold into their module's
own task (merged: notify-max-retries, return-window-days,
audit-log-retention-days) and THREE are spun off as their own dedicated
one-line tasks (dedicated: default-report-timezone, archive-grace-days,
reconciliation-tolerance-cents) -- deliberately mixed across BOTH the
base pipeline and the new subsystems so a single tree exercises both
branches of `_pd_settings_disposition` without needing two full
32-module trees.

Reuses `validate_pd_pipeline.py`'s module-agnostic helpers (`plan_files`,
`plan_shape`, `task_count`, `settings_disposition`, `module_constant`,
`pricing_overbuild_hits`, `MAX_LINE_ITEMS_RE`,
`run_checks_sh_instruments`, `parse_emit_lines`) via import -- exactly
the way `validate_pd_overflow.py` does for its own four-module variant
-- and additionally imports `validate_pd_overflow` itself to reuse ITS
already-generalized `run_checks_sh_instruments` wrapper pattern, rather
than re-deriving it a second time. Only the P2 coherence check needed a
thin generalization to six module paths instead of four
(`max_line_items_values`/`max_line_items_coherent` below).

This follows `validate_pd_overflow.py`'s own POST-T4 approach from the
start (never the pre-T4, self-only-reimplementation approach that let
two emit-format defects escape validation): `run_checks_sh_instruments`
actually EXECUTES `scenarios/pd-overflow-xl/checks.sh`'s own
`_pd_emit_plan_instruments` against a tree via the stubbed-
`command-succeeds` harness, so the regression tests below assert on
`checks.sh` ITSELF, not a Python reimplementation of its bash/awk logic.

Usage: python3 validate_pd_overflow_xl.py [-v]

Exits 0 if every property holds, 1 otherwise. Everything here is
synthetic; no real system, no real orders.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import validate_pd_overflow as pd_overflow  # noqa: E402
import validate_pd_pipeline as pd_pipeline  # noqa: E402

SCENARIO_FIXTURES = HERE / "scenarios" / "pd-overflow-xl" / "fixtures"
CHECKS_SH = HERE / "scenarios" / "pd-overflow-xl" / "checks.sh"
OUTCOMES = HERE / "fixtures" / "pd-overflow-xl-outcomes"
DIRECTORY_TASKS = OUTCOMES / "directory-tasks"

parse_emit_lines = pd_pipeline.parse_emit_lines


def run_checks_sh_instruments(tree_root, checks_sh_path=CHECKS_SH):
    """Thin wrapper around `pd_overflow.run_checks_sh_instruments` (itself
    a thin wrapper around `pd_pipeline`'s tree/script-agnostic original)
    that defaults `checks_sh_path` to THIS scenario's own checks.sh
    (pd-overflow-xl)."""
    return pd_overflow.run_checks_sh_instruments(tree_root, checks_sh_path)


MODULE_FILES = (
    # Subsystem 1: order pipeline (unchanged from pd-overflow).
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
    # Subsystem 2: operations & administration (new).
    "orders/staff_roles.py",
    "orders/audit_log.py",
    "orders/inventory_adjustments.py",
    "orders/support_tickets.py",
    "orders/rate_limits.py",
    "orders/shift_coverage.py",
    "orders/manual_override.py",
    "orders/ops_dashboard.py",
    # Subsystem 3: import/export & reconciliation (new).
    "orders/csv_import.py",
    "orders/export_feed.py",
    "orders/reconciliation.py",
    "orders/ledger_sync.py",
    "orders/carrier_manifest.py",
    "orders/duplicate_detection.py",
    "orders/vendor_feed.py",
    "orders/vendor_lead_times.py",
)

# The six modules SPEC.md requires to agree on MAX_LINE_ITEMS -- two
# wider than pd-overflow's four: manual_override.py (operations) and
# csv_import.py (import/export) are new, one from each new subsystem,
# so the family now genuinely spans all three.
MAX_LINE_ITEMS_MODULES = (
    "orders/validation.py",
    "orders/pricing.py",
    "orders/fulfillment.py",
    "orders/allocation.py",
    "orders/manual_override.py",
    "orders/csv_import.py",
)

SETTINGS_CONSTANT_NAMES = (
    "DEFAULT_REPORT_TIMEZONE",
    "NOTIFY_MAX_RETRIES",
    "ARCHIVE_GRACE_DAYS",
    "RETURN_WINDOW_DAYS",
    "AUDIT_LOG_RETENTION_DAYS",
    "RECONCILIATION_TOLERANCE_CENTS",
)


# ---------------------------------------------------------------------------
# P2 instrument, generalized to six consuming modules -- reuses
# validate_pd_pipeline.module_constant and .MAX_LINE_ITEMS_RE directly
# rather than reimplementing the regex/file-read logic (the same pattern
# validate_pd_overflow.py uses for its own four-module variant).
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
# validate_pd_overflow.py's, widened to six MAX_LINE_ITEMS modules and six
# settings constants.
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
        lines.append(f"true # max-line-items-coherent: yes ({sample} across all six modules)")
    else:
        detail = " ".join(f"{Path(r).stem}={v if v is not None else 'absent'}" for r, v in mli.items())
        lines.append(f"true # max-line-items-coherent: no ({detail})")
    presence = observables["settings_constants_present"]
    lines.append(f"true # settings-default-report-timezone: {'present' if presence['DEFAULT_REPORT_TIMEZONE'] else 'absent'}")
    lines.append(f"true # settings-notify-max-retries: {'present' if presence['NOTIFY_MAX_RETRIES'] else 'absent'}")
    lines.append(f"true # settings-archive-grace-days: {'present' if presence['ARCHIVE_GRACE_DAYS'] else 'absent'}")
    lines.append(f"true # settings-return-window-days: {'present' if presence['RETURN_WINDOW_DAYS'] else 'absent'}")
    lines.append(f"true # settings-audit-log-retention-days: {'present' if presence['AUDIT_LOG_RETENTION_DAYS'] else 'absent'}")
    lines.append(f"true # settings-reconciliation-tolerance-cents: {'present' if presence['RECONCILIATION_TOLERANCE_CENTS'] else 'absent'}")
    if observables["pricing_simplest_thing_signal"] == "overbuilt":
        lines.append(f"true # pricing-simplest-thing-signal: overbuilt ({observables['pricing_overbuild_hits']} marker(s))")
    else:
        lines.append("true # pricing-simplest-thing-signal: simple (0 markers)")
    return lines


def run_pytest(tree_root):
    import subprocess
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

    # Actually RUN checks.sh's own emit logic against this tree (see
    # module docstring) -- the two blocks above only ever prove this
    # file's OWN Python reimplementation is internally consistent; this
    # proves checks.sh itself agrees.
    checks_sh_lines = run_checks_sh_instruments(DIRECTORY_TASKS)
    print("directory-tasks checks.sh real emitted lines:")
    for line in checks_sh_lines:
        print(f"  {line}")
    parsed = parse_emit_lines(checks_sh_lines)
    for relpath in MAX_LINE_ITEMS_MODULES:
        name = Path(relpath).stem
        values = parsed.get(f"max-line-items-{name}")
        mli_ok = bool(values) and values[0] != "absent"
        if not mli_ok:
            print(f"  FAIL: max-line-items-{name} missing or absent in checks.sh's real output")
        ok = ok and mli_ok

    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
