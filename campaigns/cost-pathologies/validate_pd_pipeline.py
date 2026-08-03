#!/usr/bin/env python3
"""Validation for the pd-pipeline scenario (plan-decomposition campaign,
Task 1): an authoring+execution fixture whose `scenarios/pd-pipeline/
checks.sh` EMITS (never asserts) plan-shape, task-count,
settings-micro-edit-disposition, cross-module-coherence, and
simplest-thing observables for the campaign's P1/P2/P4 instruments
(see `scenarios/pd-pipeline/probe-design-notes.md`).

There is no single pre-written "the plan" here, unlike
`cp-x10-consistency` (a plan the session only executes) -- the session
authors its own plan from `SPEC.md`. So instead of one committed
answer-key tree, this constructs TWO plausible post-states a faithful
session might produce, each committed under
`fixtures/pd-pipeline-outcomes/`:

  - `monolithic-layered/`: a single plan file, tasks in per-module
    (layer) order, the three settings.py micro-edits folded into
    their module's own task (merged disposition), `MAX_LINE_ITEMS`
    coherent at 12 across validation/pricing/fulfillment, and simple
    (non-abstracted) pricing.
  - `directory-skeleton/`: a plan directory (manifest + constraints
    doc + one file per task), a walking-skeleton-style first task,
    the three settings.py micro-edits as three dedicated one-line
    tasks (over-decomposed disposition), `MAX_LINE_ITEMS` INCOHERENT
    (fulfillment diverges to 10), and overbuilt (currency-registry)
    pricing.

The detectors below reimplement `checks.sh`'s own bash/awk logic in
Python (mirroring `validate_x10_fixture.py`'s approach for its own
scenario), proving each observable fires correctly on both trees and
that the two trees differ exactly as designed.

**Fix round (2026-08-03 T4 correction).** Two emit-format defects escaped
this campaign's MICRO validation because everything above only ever
compared this file's own Python reimplementation against itself (or
against hand-formatted strings in `format_lines()`) -- never against
`checks.sh` actually running. The most consequential instance: `checks.sh`'s
original MAX_LINE_ITEMS extraction (bare-assignment-only) reported
"absent" for a real rep whose module wrote `MAX_LINE_ITEMS: int = 12` (a
type-annotated assignment), fabricating a requirement-loss finding later
withdrawn once the tree was hand-read. `run_checks_sh_instruments()` below
closes that gap: it actually EXECUTES `checks.sh`'s own
`_pd_emit_plan_instruments` (extracted out of `post()` specifically so it
can run outside a real quorum battery) against a tree, stubbing the one
harness primitive it depends on (`command-succeeds`), and returns the
REAL emitted lines -- see `test_pd_pipeline_fixture.py`'s
`TestChecksShInstrumentsRunForReal` and
`TestMaxLineItemsToleratesAnnotatedAndImportForms` for the validation
built on top of it.

Usage: python3 validate_pd_pipeline.py [-v]

Exits 0 if every property holds, 1 otherwise. Everything here is
synthetic; no real system, no real orders.
"""
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
SCENARIO_FIXTURES = HERE / "scenarios" / "pd-pipeline" / "fixtures"
CHECKS_SH = HERE / "scenarios" / "pd-pipeline" / "checks.sh"
OUTCOMES = HERE / "fixtures" / "pd-pipeline-outcomes"
MONOLITHIC_LAYERED = OUTCOMES / "monolithic-layered"
DIRECTORY_SKELETON = OUTCOMES / "directory-skeleton"

MODULE_FILES = (
    "orders/intake.py",
    "orders/validation.py",
    "orders/pricing.py",
    "orders/fulfillment.py",
    "orders/notifications.py",
    "orders/reporting.py",
    "orders/archiving.py",
)

_TASK_HEADER_RE = re.compile(r"^#+\s*Task\s", re.M)
_SETTINGS_REF_RE = re.compile(r"orders/settings\.py")
_ORDERS_FILE_RE = re.compile(r"orders/[a-zA-Z_]+\.py")
MAX_LINE_ITEMS_RE = re.compile(r"^MAX_LINE_ITEMS\s*=\s*(\d+)", re.M)
_OVERBUILD_RE = re.compile(
    r"class\s+[A-Za-z]*Currency|CurrencyRegistry|SUPPORTED_CURRENCIES"
    r"|abstractmethod|Protocol\[|CurrencyConverter",
    re.I,
)


# ---------------------------------------------------------------------------
# P1 instrument -- plan shape / file count / per-file line counts / task
# count. Mirrors checks.sh's _pd_plan_files / _pd_task_count.
# ---------------------------------------------------------------------------

def plan_files(tree_root):
    plans_dir = tree_root / "docs" / "superpowers" / "plans"
    if not plans_dir.exists():
        return []
    return sorted(p for p in plans_dir.rglob("*") if p.is_file())


def plan_shape(files):
    if len(files) == 0:
        return "none"
    if len(files) == 1:
        return "monolithic"
    return "directory"


def task_count(files):
    total = sum(len(_TASK_HEADER_RE.findall(f.read_text())) for f in files)
    if total > 0:
        return total
    named = sum(1 for f in files if "task" in f.name.lower())
    if named > 0:
        return named
    n = len(files)
    return n - 1 if n > 1 else n


# ---------------------------------------------------------------------------
# P4 instrument -- settings.py micro-edit disposition (dedicated one-line
# tasks vs folded into their module's own task). Mirrors checks.sh's
# _pd_settings_disposition awk program line for line: chunk boundaries are
# either a new file or a Task-header line, and a chunk counts as
# "dedicated" when settings.py is the only orders/*.py file it references.
#
# `have_task` gates every flush so that plan text preceding the first Task
# header -- a Global Constraints preamble in a monolithic file, or a
# manifest/constraints file sorted ahead of any task file in a directory
# -- is never itself counted as a task, even if it happens to mention
# orders/settings.py in passing.
# ---------------------------------------------------------------------------

def settings_disposition(files):
    total = 0
    dedicated = 0
    touched = False
    seen = set()
    have_task = False

    def flush():
        nonlocal total, dedicated
        if have_task and touched:
            total += 1
            if not seen:
                dedicated += 1

    for f in files:
        first_line = True
        for line in f.read_text().splitlines():
            if first_line:
                flush()
                touched, seen = False, set()
                first_line = False
            if _TASK_HEADER_RE.match(line):
                flush()
                touched, seen = False, set()
                have_task = True
            if _SETTINGS_REF_RE.search(line):
                touched = True
            for ref in _ORDERS_FILE_RE.findall(line):
                if ref != "orders/settings.py":
                    seen.add(ref)
    flush()
    return total, dedicated


# ---------------------------------------------------------------------------
# P2 instrument -- MAX_LINE_ITEMS coherence across the three consuming
# modules' FINAL CODE (not the plan text). Mirrors checks.sh's grep of
# orders/validation.py, orders/pricing.py, orders/fulfillment.py.
# ---------------------------------------------------------------------------

def module_constant(tree_root, relpath, pattern):
    """Read an integer module-level constant matching `pattern` out of
    `tree_root / relpath`. Public (no leading underscore) so sibling
    scenarios' validate_*.py scripts -- e.g. pd-overflow's, whose
    MAX_LINE_ITEMS coherence check spans a different, wider set of
    consuming modules -- can reuse this instead of reimplementing it."""
    path = tree_root / relpath
    if not path.exists():
        return None
    match = pattern.search(path.read_text())
    return int(match.group(1)) if match else None


def max_line_items_values(tree_root):
    return {
        "validation": module_constant(tree_root, "orders/validation.py", MAX_LINE_ITEMS_RE),
        "pricing": module_constant(tree_root, "orders/pricing.py", MAX_LINE_ITEMS_RE),
        "fulfillment": module_constant(tree_root, "orders/fulfillment.py", MAX_LINE_ITEMS_RE),
    }


def max_line_items_coherent(values):
    present = [v for v in values.values() if v is not None]
    return len(present) == 3 and len(set(present)) == 1


# ---------------------------------------------------------------------------
# settings.py micro-edit presence (do the three constants exist at all).
# ---------------------------------------------------------------------------

def settings_constants_present(tree_root):
    path = tree_root / "orders" / "settings.py"
    text = path.read_text() if path.exists() else ""
    return {
        "DEFAULT_REPORT_TIMEZONE": bool(re.search(r"^DEFAULT_REPORT_TIMEZONE", text, re.M)),
        "NOTIFY_MAX_RETRIES": bool(re.search(r"^NOTIFY_MAX_RETRIES", text, re.M)),
        "ARCHIVE_GRACE_DAYS": bool(re.search(r"^ARCHIVE_GRACE_DAYS", text, re.M)),
    }


# ---------------------------------------------------------------------------
# P4/YAGNI instrument -- simplest-thing signal on orders/pricing.py.
# ---------------------------------------------------------------------------

def pricing_overbuild_hits(tree_root):
    path = tree_root / "orders" / "pricing.py"
    if not path.exists():
        return 0
    return len(_OVERBUILD_RE.findall(path.read_text()))


# ---------------------------------------------------------------------------
# Aggregate observables + emit-line rendering, matching checks.sh's exact
# "true # label: value" comment text so a scorer's line-parser (or this
# script's own tests) can exercise the identical format.
# ---------------------------------------------------------------------------

def compute_observables(tree_root):
    files = plan_files(tree_root)
    shape = plan_shape(files)
    tasks = task_count(files) if files else 0
    total, dedicated = settings_disposition(files) if files else (0, 0)
    merged = total - dedicated
    mli = max_line_items_values(tree_root)
    coherent = max_line_items_coherent(mli)
    presence = settings_constants_present(tree_root)
    overbuild = pricing_overbuild_hits(tree_root)
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
    for name in ("validation", "pricing", "fulfillment"):
        value = mli[name] if mli[name] is not None else "absent"
        lines.append(f"true # max-line-items-{name}: {value}")
    if observables["max_line_items_coherent"]:
        lines.append(f"true # max-line-items-coherent: yes ({mli['validation']} across all three modules)")
    else:
        lines.append(
            "true # max-line-items-coherent: no "
            f"(validation={mli['validation']} pricing={mli['pricing']} fulfillment={mli['fulfillment']})"
        )
    presence = observables["settings_constants_present"]
    lines.append(f"true # settings-default-report-timezone: {'present' if presence['DEFAULT_REPORT_TIMEZONE'] else 'absent'}")
    lines.append(f"true # settings-notify-max-retries: {'present' if presence['NOTIFY_MAX_RETRIES'] else 'absent'}")
    lines.append(f"true # settings-archive-grace-days: {'present' if presence['ARCHIVE_GRACE_DAYS'] else 'absent'}")
    if observables["pricing_simplest_thing_signal"] == "overbuilt":
        lines.append(f"true # pricing-simplest-thing-signal: overbuilt ({observables['pricing_overbuild_hits']} marker(s))")
    else:
        lines.append("true # pricing-simplest-thing-signal: simple (0 markers)")
    return lines


# ---------------------------------------------------------------------------
# Actually EXERCISING checks.sh (2026-08-03 T4 correction fix round). See
# module docstring for why this exists: everything above only ever
# compared this file's own Python port against itself, which let a real
# checks.sh regex defect (MAX_LINE_ITEMS extraction missing annotated/
# import-reference forms) escape validation entirely.
# ---------------------------------------------------------------------------

_EMIT_LINE_RE = re.compile(r"^true # ([a-zA-Z0-9_.\-/ ]+?): (.*)$")


def parse_emit_lines(lines):
    """{label: [value, ...]} for every `true # label: value` entry in
    LINES, in order -- identical shape/regex to
    `score_pd_planshape.parse_emit_lines` (verdict.json-sourced) and
    `test_pd_pipeline_fixture._parse_lines`, so a caller of any of the
    three never has to translate between formats. Non-matching lines are
    silently skipped (LINES here comes from `run_checks_sh_instruments`,
    which only ever emits this shape, but a defensive caller should still
    survive a stray line)."""
    parsed = {}
    for line in lines:
        m = _EMIT_LINE_RE.match(line)
        if not m:
            continue
        label, value = m.groups()
        parsed.setdefault(label, []).append(value)
    return parsed


def run_checks_sh_instruments(tree_root, checks_sh_path=CHECKS_SH):
    """Actually RUNS `checks_sh_path`'s own `_pd_emit_plan_instruments`
    function (the P1/P2/P4 plan-decomposition instrument block, extracted
    out of `post()` in both scenarios' checks.sh specifically so it can be
    exercised like this) against TREE_ROOT, and returns the real emitted
    `true # label: value` lines in call order -- instead of recomputing
    the same numbers independently in Python (`compute_observables()`
    above) and formatting matching strings by hand (`format_lines()`
    above). See module docstring for why this distinction matters: it's
    the fix for the exact defect that escaped this campaign's MICRO
    validation.

    Stubs the ONE harness primitive `_pd_emit_plan_instruments` depends on
    (`command-succeeds`) as a shell function that appends its first
    argument to a temp file, one line per call -- the same text a real
    quorum run records as that check's own `args[0]` in verdict.json (see
    `score_pd_planshape.parse_emit_lines`). No other harness primitive
    (`file-exists`, `git-repo`, `check-transcript`, ...) is needed because
    `_pd_emit_plan_instruments` doesn't call any of them.

    Raises RuntimeError if checks.sh itself errors out (a real defect in
    the script, not a case to swallow silently)."""
    with tempfile.TemporaryDirectory() as tmp:
        record_path = Path(tmp) / "emitted.txt"
        script = f"""
set -euo pipefail
command-succeeds() {{ printf '%s\\n' "$1" >> {shlex.quote(str(record_path))}; }}
cd {shlex.quote(str(tree_root))}
source {shlex.quote(str(checks_sh_path))}
_pd_emit_plan_instruments
"""
        result = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"checks.sh instrument block failed (exit {result.returncode}): "
                f"{result.stdout}{result.stderr}"
            )
        return record_path.read_text().splitlines() if record_path.exists() else []


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

    for label, tree in (("monolithic-layered", MONOLITHIC_LAYERED), ("directory-skeleton", DIRECTORY_SKELETON)):
        print(f"{label} pytest ({tree}):")
        tree_ok, tree_output = run_pytest(tree)
        print(f"  {'PASS' if tree_ok else 'FAIL'}")
        if verbose or not tree_ok:
            print(tree_output)
        ok = ok and tree_ok

        observables = compute_observables(tree)
        print(f"{label} observables:")
        for line in format_lines(observables):
            print(f"  {line}")
        ok = ok and (observables["plan_file_count"] > 0)

        # Actually RUN checks.sh's own emit logic against this tree (see
        # module docstring / T4 correction) -- the two lines above only
        # ever prove this file's OWN Python reimplementation is internally
        # consistent; this proves checks.sh itself agrees, catching the
        # exact class of defect (a checks.sh regex too narrow to see a
        # real shape) that a self-only comparison cannot.
        checks_sh_lines = run_checks_sh_instruments(tree)
        print(f"{label} checks.sh real emitted lines:")
        for line in checks_sh_lines:
            print(f"  {line}")
        parsed = parse_emit_lines(checks_sh_lines)
        for name in ("validation", "pricing", "fulfillment"):
            values = parsed.get(f"max-line-items-{name}")
            mli_ok = bool(values) and values[0] != "absent"
            if not mli_ok:
                print(f"  FAIL: max-line-items-{name} missing or absent in checks.sh's real output")
            ok = ok and mli_ok

    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
