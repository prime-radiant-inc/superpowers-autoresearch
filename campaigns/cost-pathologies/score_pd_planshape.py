#!/usr/bin/env python3
"""Plan-decomposition campaign (Task 2a): plan-shape scorer. Two
independent read paths, both needed because a battery rep is inspected in
two different ways depending on what's available:

  1. **From a rep's `verdict.json`** (`observables_from_verdict`) --
     `scenarios/pd-pipeline/checks.sh` emits its plan-shape/task-count/
     micro-edit-disposition/coherence/overbuild findings as `true #
     label: value` command-succeeds entries (see that file's own
     docstring: "None of these are pass/fail gates" -- the finding rides
     in the recorded command TEXT, not the check's pass/fail bit).
     `parse_emit_lines` recovers that text with the exact same
     `_EMIT_LINE_RE` shape `test_pd_pipeline_fixture.py` already uses to
     assert against it; `observables_from_verdict` re-derives
     `validate_pd_pipeline.compute_observables()`'s typed dict FROM that
     text instead of from a checked-out tree, for the case where only
     `verdict.json` is on hand (a rep's coding-agent-workdir may not
     always be, e.g. a compacted battery archive).
  2. **From a rep's own workdir tree, directly** (`plan_shape_report`) --
     generalizes `checks.sh`'s own helpers (`_pd_plan_files`/
     `_pd_task_count`/`_pd_settings_disposition`), which are themselves
     already written generic ("Nothing in this fixture mandates a
     directory convention -- these helpers stay generic", per that
     file's own comment) plus a return-window-failure detector this
     campaign's design doc calls for explicitly ("observed return-window
     overflow failures" -- Jesse's directive) that `checks.sh` has no
     equivalent for at all (it inspects the FINAL tree only, never the
     authoring session's own write attempts).

**Why the micro-edit-disposition/overbuild functions take explicit
target/pattern arguments instead of hardcoding `orders/settings.py`/
`orders/pricing.py`:** those two concepts are inherently SPEC-specific
(which file is "the micro-edit target," what "overbuilt" looks like) --
`pd-pipeline` is this campaign's only fixture as of this task, but a
future P1-P4 battery fixture will need the SAME shape of question asked
about ITS OWN files. Parameterizing keeps this scorer honestly reusable
rather than baking in one fixture's vocabulary permanently; every test
against the real pd-pipeline fixture passes that fixture's own values
explicitly (`re.compile(r"orders/settings\\.py")`, etc.), never a
hardcoded default.

**Return-window failure detection (`return_window_failures`).** Per this
task's own brief: "a plan-write that was truncated/failed and retried --
look for repeated large write attempts to the same plan path in the
rollout command stream." A plan is authored via `apply_patch`-shaped
content (`*** Add File: <path>` / `*** Update File: <path>` headers,
embedded either as a custom_exec JS blob's raw text -- see
`score_pd_dupdiscovery.py`'s own module docstring for why every exec
command in this campaign's real corpus takes that shape -- or, for the
"exec_command" encoding, as the already-decoded shell/tool text). This
scorer does NOT gate on an arbitrary "large" byte-size threshold: no real
return-window-failure corpus exists yet to calibrate one (inventing a
magic number here would be exactly the kind of unverified technical
detail this project's standing rule forbids), so the signal is instead
the REPEAT itself -- writing the same plan path >=2 times in one
session's own command stream is not something a normal, un-truncated
authoring flow does (a plan file is written once, then edited via
narrower diffs referencing OTHER paths, not re-written whole again and
again). Each attempt's own text length is still reported (`size`) for a
human to eyeball, and corroborated against `rollout_parser.patch_applies()`
outcome events for the same path when available (`confirmed_failure`:
True if any matching patch_apply_end for that path recorded
`success=False`) -- but the flag itself never depends on that
corroboration being present, since a return-window overflow can also
surface as the SESSION choosing to retry pre-emptively (e.g. after
noticing a truncated file) without ever emitting a failed
patch_apply_end for it.

Usage: `plan_shape_report(tree_root, ...)` / `observables_from_verdict
(verdict_path)` for the pure computations, or run this file directly
against one or more rep directories (`python3 score_pd_planshape.py
REP_DIR...`) for a JSON report per rep combining both read paths.
Read-only; makes no writes.
"""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "codex-efficiency"))
import rollout_parser as rp
from scorer_common import find_files
from task9_extract_signals import find_verdict as _find_verdict  # reused, not re-derived

# ---------------------------------------------------------------------------
# 1. verdict.json "true # label: value" emit-line reading.
# ---------------------------------------------------------------------------

# Identical shape to test_pd_pipeline_fixture.py's own _EMIT_LINE_RE --
# every scorer reading these lines must parse them the same way that
# test already asserts checks.sh's own output against.
_EMIT_LINE_RE = re.compile(r"^true # ([a-zA-Z0-9_.\-/ ]+?): (.*)$")


def parse_emit_lines(verdict_path):
    """{label: [value, ...]} for every `true # label: value`
    command-succeeds entry in VERDICT_PATH's `checks` array, in file
    order. A label can legitimately repeat (one `plan-file: ...` line per
    plan file) -- every occurrence is kept, never overwritten."""
    verdict = json.loads(Path(verdict_path).read_text())
    parsed = {}
    for check in verdict.get("checks", []):
        if check.get("check") != "command-succeeds":
            continue
        args = check.get("args") or []
        if not args:
            continue
        m = _EMIT_LINE_RE.match(args[0])
        if not m:
            continue
        label, value = m.groups()
        parsed.setdefault(label, []).append(value)
    return parsed


# Value-parsing helpers for the pd-pipeline scenario's own known emit
# vocabulary (scenarios/pd-pipeline/checks.sh). See module docstring for
# why this interpreter is scenario-specific while parse_emit_lines()
# above is not.
_SHAPE_RE = re.compile(r"^(\w+) \((\d+) file\(s\)\)$")
_PLAN_FILE_RE = re.compile(r"^(.+) \((\d+) lines\)$")
_OVERBUILD_RE = re.compile(r"^(overbuilt|simple) \((\d+) marker\(s\)\)$")


def observables_from_verdict(verdict_path):
    """The pd-pipeline scenario's own typed observable dict, re-derived
    from VERDICT_PATH's emitted `true #` lines -- see module docstring.
    Mirrors `validate_pd_pipeline.compute_observables()`'s field names
    exactly (a DIFFERENT source for the SAME numbers: that module reads a
    checked-out tree directly; this one reads the composer's recorded
    check text), so a caller comparing the two never has to translate
    between two field-naming schemes."""
    lines = parse_emit_lines(verdict_path)

    def _one(label, default=None):
        vals = lines.get(label)
        return vals[0] if vals else default

    shape_m = _SHAPE_RE.match(_one("plan-shape", "none (0 file(s))"))
    shape, file_count = shape_m.group(1), int(shape_m.group(2))

    plan_files_out = []
    for entry in lines.get("plan-file", []):
        m = _PLAN_FILE_RE.match(entry)
        if m:
            plan_files_out.append((m.group(1), int(m.group(2))))

    def _int(label, default=0):
        # checks.sh's own "no plan artifact found" branch appends a
        # trailing annotation after the number (e.g. "0 (no plan
        # artifact found)") -- only the LEADING integer is the value.
        v = _one(label)
        if v is None:
            return default
        m = re.match(r"-?\d+", v)
        return int(m.group(0)) if m else default

    def _mli(label):
        v = _one(f"max-line-items-{label}", "absent")
        return int(v) if v != "absent" else None

    mli = {name: _mli(name) for name in ("validation", "pricing", "fulfillment")}
    coherent_text = _one("max-line-items-coherent", "")
    coherent = coherent_text.startswith("yes")

    def _presence(label):
        return _one(label) == "present"

    overbuild_m = _OVERBUILD_RE.match(_one("pricing-simplest-thing-signal", "simple (0 marker(s))"))
    overbuild_signal, overbuild_hits = overbuild_m.group(1), int(overbuild_m.group(2))

    return {
        "plan_shape": shape,
        "plan_file_count": file_count,
        "plan_files": plan_files_out,
        "plan_task_count": _int("plan-task-count"),
        "settings_touching_tasks": _int("settings-micro-edits-touching-tasks"),
        "settings_dedicated_tasks": _int("settings-micro-edits-dedicated-tasks"),
        "settings_merged_tasks": _int("settings-micro-edits-merged-tasks"),
        "max_line_items": mli,
        "max_line_items_coherent": coherent,
        "settings_constants_present": {
            "DEFAULT_REPORT_TIMEZONE": _presence("settings-default-report-timezone"),
            "NOTIFY_MAX_RETRIES": _presence("settings-notify-max-retries"),
            "ARCHIVE_GRACE_DAYS": _presence("settings-archive-grace-days"),
        },
        "pricing_overbuild_hits": overbuild_hits,
        "pricing_simplest_thing_signal": overbuild_signal,
    }


# ---------------------------------------------------------------------------
# 2. Direct workdir/tree inspection -- generic plan-shape/task-count, plus
# generalized (parameterized) micro-edit-disposition/overbuild helpers.
# Mirrors validate_pd_pipeline.py's own functions, which this task's brief
# names directly as the logic to reuse/generalize.
# ---------------------------------------------------------------------------

_TASK_HEADER_RE = re.compile(r"^#+\s*Task\s", re.M)


def plan_files(tree_root):
    """Every file under TREE_ROOT/docs/superpowers/plans, sorted --
    identical convention to checks.sh's `_pd_plan_files`/
    `validate_pd_pipeline.plan_files`: no plan directory at all yields
    `[]`, not an error (today's writing-plans default is a single file;
    nothing here mandates a directory convention)."""
    plans_dir = Path(tree_root) / "docs" / "superpowers" / "plans"
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
    """Count of `# Task`/`## Task`/... headers across FILES, falling back
    to filename-based counting and finally file-count-minus-one -- see
    checks.sh's own `_pd_task_count` docstring for the full fallback
    rationale this ports."""
    total = sum(len(_TASK_HEADER_RE.findall(f.read_text())) for f in files)
    if total > 0:
        return total
    named = sum(1 for f in files if "task" in f.name.lower())
    if named > 0:
        return named
    n = len(files)
    return n - 1 if n > 1 else n


def micro_edit_disposition(files, target_re, sibling_re):
    """Generalizes checks.sh's `_pd_settings_disposition`: for each
    Task-header chunk (a monolithic file) or each whole file (a directory
    convention, one task per file), does that chunk reference TARGET_RE
    at all, and if so, is it the ONLY match of SIBLING_RE found in that
    chunk (a "dedicated" micro-edit task) or does it share the chunk with
    >=1 other SIBLING_RE match (a "merged" task)? Returns (total,
    dedicated) -- merged = total - dedicated.

    TARGET_RE (e.g. `re.compile(r"orders/settings\\.py")`) identifies the
    micro-edit target itself; SIBLING_RE (e.g.
    `re.compile(r"orders/[a-zA-Z_]+\\.py")`) is the broader "a real module
    file was also touched here" pattern that TARGET_RE's own match is
    excluded from when counting siblings. Plan text BEFORE the first Task
    header (a Global Constraints preamble, or a manifest/constraints file
    sorted ahead of any task file) is never itself counted as a task, even
    if it mentions TARGET_RE in passing -- same `have_task` gate as
    checks.sh's own awk implementation."""
    total = 0
    dedicated = 0
    have_task = False

    def _chunks():
        for f in files:
            first = True
            for line in f.read_text().splitlines():
                yield line, first
                first = False

    touched = False
    siblings = set()

    def flush():
        nonlocal total, dedicated
        if have_task and touched:
            total += 1
            if not siblings:
                dedicated += 1

    for line, is_first_line_of_file in _chunks():
        if is_first_line_of_file:
            flush()
            touched, siblings = False, set()
        if _TASK_HEADER_RE.match(line):
            flush()
            touched, siblings = False, set()
            have_task = True
        if target_re.search(line):
            touched = True
        for ref in sibling_re.findall(line):
            if target_re.fullmatch(ref):
                continue  # the target's own match, not a sibling module
            siblings.add(ref)
    flush()
    return total, dedicated


def overbuild_hits(tree_root, relpath, marker_re):
    """Count of MARKER_RE matches in TREE_ROOT/RELPATH, or 0 if the file
    does not exist -- generalizes checks.sh's pricing-simplest-thing-
    signal check to any (file, marker pattern) pair."""
    path = Path(tree_root) / relpath
    if not path.exists():
        return 0
    return len(marker_re.findall(path.read_text()))


def plan_shape_report(tree_root, micro_edit_target=None, micro_edit_siblings=None,
                       overbuild_relpath=None, overbuild_marker_re=None):
    """The generic plan-shape/task-count report, plus the two
    parameterized instruments when their arguments are supplied (omitted
    -- None -- fields are simply left out of the returned dict, since
    those questions are meaningless without a target to ask them about)."""
    files = plan_files(tree_root)
    report = {
        "plan_shape": plan_shape(files),
        "plan_file_count": len(files),
        "plan_files": [(str(f.relative_to(tree_root)), len(f.read_text().splitlines())) for f in files],
        "plan_task_count": task_count(files) if files else 0,
    }
    if micro_edit_target is not None and micro_edit_siblings is not None and files:
        total, dedicated = micro_edit_disposition(files, micro_edit_target, micro_edit_siblings)
        report["micro_edit_touching_tasks"] = total
        report["micro_edit_dedicated_tasks"] = dedicated
        report["micro_edit_merged_tasks"] = total - dedicated
    if overbuild_relpath is not None and overbuild_marker_re is not None:
        report["overbuild_hits"] = overbuild_hits(tree_root, overbuild_relpath, overbuild_marker_re)
    return report


# ---------------------------------------------------------------------------
# Return-window failure detection: repeated large write attempts to the
# same plan path in a rollout's own command stream. See module docstring.
# ---------------------------------------------------------------------------

_PATCH_HEADER_RE = re.compile(r"\*\*\* (?:Add|Update) File: (\S+)")
_PLAN_PATH_RE = re.compile(r"(docs/superpowers/plans/\S+)")


def _plan_relpath(raw_path):
    """The docs/superpowers/plans/... suffix of RAW_PATH (which may carry
    a rep-specific absolute prefix, e.g.
    `/workspace/evals/results/<rep>/.../coding-agent-workdir/docs/
    superpowers/plans/foo.md`), or None if RAW_PATH doesn't reference a
    plan path at all."""
    m = _PLAN_PATH_RE.search(raw_path)
    return m.group(1) if m else None


def patch_write_attempts(rollout_paths):
    """Every apply_patch-shaped Add/Update File header targeting a
    docs/superpowers/plans/... path, found in ANY exec command's own text
    (both exec_commands() encodings, de-escaped) across ROLLOUT_PATHS.
    Each attempt: {"plan_path": str, "rollout": basename, "timestamp":
    str, "size": int} -- `size` is that ONE exec command's own de-escaped
    text length (a rough proxy for "how much content this write attempt
    carried"; see module docstring for why this is reported but never
    gated on)."""
    out = []
    for path in sorted(rollout_paths):
        basename = os.path.basename(path)
        for ec in rp.exec_commands(path):
            cmd = rp.deescape_custom_exec(ec.cmd, ec.encoding)
            for raw_path in _PATCH_HEADER_RE.findall(cmd):
                plan_path = _plan_relpath(raw_path)
                if plan_path is None:
                    continue
                out.append({"plan_path": plan_path, "rollout": basename,
                            "timestamp": ec.timestamp, "size": len(cmd)})
    out.sort(key=lambda a: a["timestamp"])
    return out


def return_window_failures(rollout_paths):
    """Every docs/superpowers/plans/... path written >=2 times across
    ROLLOUT_PATHS's own patch_write_attempts() -- the return-window-
    overflow candidate signal. Each entry: {"plan_path": str, "attempts":
    n, "sizes": [int, ...], "confirmed_failure": bool} --
    `confirmed_failure` is True iff any `rollout_parser.patch_applies()`
    event for that exact path, anywhere in ROLLOUT_PATHS, recorded
    `success=False` (corroborating evidence, never required for the
    entry to appear at all -- see module docstring)."""
    attempts = patch_write_attempts(rollout_paths)
    by_path = {}
    for a in attempts:
        by_path.setdefault(a["plan_path"], []).append(a)

    failed_paths = set()
    for path in rollout_paths:
        for pa in rp.patch_applies(path):
            if pa.success:
                continue
            for changed in pa.paths:
                plan_path = _plan_relpath(changed)
                if plan_path is not None:
                    failed_paths.add(plan_path)

    out = []
    for plan_path, entries in sorted(by_path.items()):
        if len(entries) < 2:
            continue
        out.append({
            "plan_path": plan_path,
            "attempts": len(entries),
            "sizes": [e["size"] for e in entries],
            "confirmed_failure": plan_path in failed_paths,
        })
    return out


# ---------------------------------------------------------------------------
# CLI: combine both read paths for a rep directory.
# ---------------------------------------------------------------------------

def find_workdir(rep_dir):
    """The rep's own coding-agent-workdir (the checked-out tree a real
    battery run leaves behind), or None if this rep dir doesn't carry
    one (e.g. an archived/compacted rep). `coding-agent-workdir` is
    itself a DIRECTORY, so this walks dirnames directly rather than
    reusing `scorer_common.find_files` (which only matches file
    basenames)."""
    for dirpath, dirnames, _filenames in os.walk(rep_dir):
        if "coding-agent-workdir" in dirnames:
            return os.path.join(dirpath, "coding-agent-workdir")
    return None


def _rollouts_for_rep(rep_dir):
    return sorted(find_files(rep_dir, "rollout-*.jsonl",
                              path_contains=os.path.join("home", ".codex", "sessions")))


def main(argv):
    if len(argv) < 2:
        print("usage: score_pd_planshape.py REP_DIR...", file=sys.stderr)
        return 1
    reports = {}
    for rep_dir in argv[1:]:
        rep_report = {}
        verdict_path = _find_verdict(rep_dir)
        if verdict_path:
            try:
                rep_report["from_verdict"] = observables_from_verdict(verdict_path)
            except (json.JSONDecodeError, OSError):
                pass
        workdir = find_workdir(rep_dir)
        if workdir:
            rep_report["from_workdir"] = plan_shape_report(workdir)
        rollouts = _rollouts_for_rep(rep_dir)
        if rollouts:
            rep_report["return_window_failures"] = return_window_failures(rollouts)
        reports[os.path.basename(rep_dir.rstrip("/"))] = rep_report
    if len(argv) == 2 and reports:
        print(json.dumps(next(iter(reports.values())), indent=2))
    else:
        print(json.dumps(reports, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
