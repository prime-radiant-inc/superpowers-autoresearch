#!/usr/bin/env python3
"""Plan-decomposition campaign (Task 2c): coherence wiring. Thin --
per this task's own brief ("reuse existing x10-consistency-scan.py"),
this module adds NO new detection logic for tree mode at all, and only
one small, deliberately narrow detector for plan-text mode.

**Tree mode (`tree_coherence_report`)** -- a rep's final merged tree,
scanned by the SAME `x10-consistency-scan.scan_repo()` the backlog
campaign already built and validated (>=5/5 seeded defects, <=5 false
positives on a clean tree -- `test_x10_consistency_scan.py`). Loaded by
path via `importlib` (same idiom `test_x10_consistency_scan.py` already
uses: `x10-consistency-scan.py` has a hyphen, not a valid Python module
name) -- imported, never forked.

**Plan-text mode (`plan_coherence_report`)** -- the design doc's P2 axis
("plan-time coherence gate ... the consistency scanner run against the
PLAN's own specified constants/interfaces before Task 1") needs the SAME
question asked of PLAN PROSE instead of code: does a named constant get
stated with two different values across two different task sections? Per
this task's own brief, this is scoped to ONLY that one class (value
divergence) -- x10's other two detectors (naming-drift, enum-asymmetry)
are AST-based over real Python syntax and have no obvious prose analogue
worth inventing here; if a future arm needs them, that is a new task, not
a silent scope-creep of this one.

`plan_constant_divergence()` is a regex scan, not an AST parse (plan text
is markdown/prose, not Python) -- it looks for `NAME = value`/`NAME:
value` assignments where NAME is ALL_CAPS (`[A-Z][A-Z0-9_]{2,}`, at least
3 characters so ordinary capitalized prose words like "Task" or "SPEC"
never qualify -- "Task" fails immediately since its own middle/trailing
letters are lowercase) and value is a quoted string or a bare number --
exactly the shape a plan states a constant in, e.g. the design doc's own
worked example, "`MAX_LINE_ITEMS=25` per task section." Findings reuse
`x10-consistency-scan.py`'s own `Finding` dataclass (same category-
confidence-sites shape, `category="plan-constant-divergence"` to
distinguish from tree mode's `"constant-divergence"`), so a caller
handling both modes' output never needs two different result shapes.

**Section splitting (`plan_sections`)** mirrors the SAME dual plan-shape
convention every other pd-pipeline instrument already established
(`checks.sh`'s `_pd_task_count`/`_pd_settings_disposition`,
`score_pd_planshape.py`'s `micro_edit_disposition`): a single (monolithic)
plan file is split at its own `#+ Task` headers, with any text before the
first header kept as its own `"preamble"` section (a Global Constraints
block CAN legitimately state the canonical value -- it must still
participate in divergence detection, just under its own label, not
silently dropped); a directory (one file per task) treats each FILE as
its own section.

Usage: `tree_coherence_report(tree_root)` / `plan_coherence_report
(plan_files)` for the pure computations, or run this file directly:
`python3 score_pd_coherence.py tree TREE_ROOT` or `python3
score_pd_coherence.py plan PLAN_FILE...`. Read-only; makes no writes.
"""
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(os.path.dirname(os.path.abspath(__file__)))


def _load_x10():
    spec = importlib.util.spec_from_file_location("x10_consistency_scan", HERE / "x10-consistency-scan.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


x10 = _load_x10()
Finding = x10.Finding

# ---------------------------------------------------------------------------
# Tree mode: thin wrapper, zero new logic.
# ---------------------------------------------------------------------------


def tree_coherence_report(tree_root, top=20, include_tests=False):
    """See module docstring -- exactly `x10.scan_repo()`, nothing added."""
    return x10.scan_repo(tree_root, top=top, include_tests=include_tests)


# ---------------------------------------------------------------------------
# Plan-text mode.
# ---------------------------------------------------------------------------

_TASK_HEADER_RE = re.compile(r"^#+\s*Task\s", re.M)

# NAME [=:] value, where NAME is ALL_CAPS (>=3 chars, so short prose
# fragments can never accidentally qualify) and value is a quoted string
# or a bare (optionally signed/decimal) number -- the shape a plan states
# a constant in, e.g. "`MAX_LINE_ITEMS = 12`" or "MAX_LINE_ITEMS: 12".
_CONST_ASSIGN_RE = re.compile(
    r'\b([A-Z][A-Z0-9_]{2,})\s*[:=]\s*'
    r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|-?\d+(?:\.\d+)?)'
)


def _normalize_value(raw_value):
    """Strips a quoted string's own quotes; a bare number is returned
    unchanged (still a string -- comparison is by exact text, matching
    x10's own `_module_level_constants`/`detect_constant_divergence`
    convention of comparing literal values, not coerced types)."""
    if raw_value[:1] in ("'", '"') and raw_value[-1:] == raw_value[:1]:
        return raw_value[1:-1]
    return raw_value


def plan_constants(text):
    """[(name, normalized_value, lineno), ...] for every _CONST_ASSIGN_RE
    match in TEXT, in line order."""
    out = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for m in _CONST_ASSIGN_RE.finditer(line):
            name, raw_value = m.groups()
            out.append((name, _normalize_value(raw_value), lineno))
    return out


def _split_monolithic_sections(text):
    """See module docstring's Section splitting note. A file with no Task
    header at all (e.g. a pure constraints/manifest doc) is returned as
    one `"<whole-file>"` section rather than an empty list, so its own
    constants still participate in divergence detection."""
    matches = list(_TASK_HEADER_RE.finditer(text))
    if not matches:
        return [("<whole-file>", text)]
    sections = []
    preamble = text[:matches[0].start()]
    if preamble.strip():
        sections.append(("preamble", preamble))
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        newline = text.find("\n", m.start())
        header_line = text[m.start():newline] if newline != -1 else text[m.start():]
        label = header_line.lstrip("#").strip() or f"task-at-line-{text.count(chr(10), 0, m.start()) + 1}"
        sections.append((label, text[start:end]))
    return sections


def plan_sections(files):
    """[(label, text), ...] -- one monolithic FILE is split by its own
    Task headers (see `_split_monolithic_sections`); multiple files (a
    plan directory) are each their own section, labeled by filename."""
    files = list(files)
    if len(files) == 1:
        return _split_monolithic_sections(Path(files[0]).read_text())
    return [(Path(f).name, Path(f).read_text()) for f in files]


def plan_constant_divergence(sections):
    """Every ALL_CAPS constant NAME stated with >=2 different values
    across >=2 different SECTIONS -- the plan-text analogue of
    `x10.detect_constant_divergence`. Same-section repeats of the
    identical name/value (e.g. restated in both a task's own body and its
    Verification line) are not divergence; only occurrences that
    disagree, in DIFFERENT sections, count."""
    by_name = {}
    for label, text in sections:
        for name, value, lineno in plan_constants(text):
            by_name.setdefault(name, []).append((label, value, lineno))

    findings = []
    for name, occurrences in sorted(by_name.items()):
        values = {v for _, v, _ in occurrences}
        labels = {lbl for lbl, _, _ in occurrences}
        if len(values) < 2 or len(labels) < 2:
            continue
        sites = [(label, lineno, f"{name} = {value!r}") for label, value, lineno in occurrences]
        findings.append(Finding(
            category="plan-constant-divergence",
            description=(
                f"{name!r} stated with {len(values)} different values "
                f"across {len(labels)} task section(s)"
            ),
            confidence=0.9,
            sites=sites,
        ))
    return findings


def plan_coherence_report(files, top=20):
    """{"findings": [...], "total_before_cap": n, "suppressed": n} --
    same result shape as `x10.scan_repo()`'s tree-mode report, so a
    caller handling both modes never branches on shape, only on
    `category`."""
    sections = plan_sections(files)
    findings = plan_constant_divergence(sections)
    findings.sort(key=lambda f: f.confidence, reverse=True)
    total = len(findings)
    capped = findings[:top]
    return {"findings": capped, "total_before_cap": total, "suppressed": total - len(capped)}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _findings_to_json(result):
    return {
        "total_before_cap": result["total_before_cap"],
        "suppressed": result["suppressed"],
        "findings": [
            {
                "category": f.category,
                "description": f.description,
                "confidence": f.confidence,
                "sites": [{"label_or_file": s[0], "line": s[1], "label": s[2]} for s in f.sites],
            }
            for f in result["findings"]
        ],
    }


def main(argv):
    if len(argv) < 3:
        print("usage: score_pd_coherence.py tree TREE_ROOT | "
              "score_pd_coherence.py plan PLAN_FILE...", file=sys.stderr)
        return 1
    mode = argv[1]
    if mode == "tree":
        result = tree_coherence_report(argv[2])
    elif mode == "plan":
        result = plan_coherence_report(argv[2:])
    else:
        print(f"unknown mode: {mode!r} (expected 'tree' or 'plan')", file=sys.stderr)
        return 1
    print(json.dumps(_findings_to_json(result), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
