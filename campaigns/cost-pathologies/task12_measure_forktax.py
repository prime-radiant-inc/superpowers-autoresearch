#!/usr/bin/env python3
"""Task 12 -- X4 fork-tax field measurement over this campaign's own battery
trees (cp-* reps from Tasks 8-11, both container lanes). NOT a corpus-
validated campaign scorer itself -- a thin, disclosed invocation wrapper
around score_x4_forktax.fork_stats() (Task 2, unmodified), same "one-shot
triage helper" scope decision as task9_extract_signals.py / task10_extract_
signals.py.

WHY THIS WRAPPER EXISTS (disclosed instrumentation finding, not a scorer
fix): score_x4_forktax.find_rollouts() globs `session_dir/**/*.jsonl` with
Python's `glob.glob(..., recursive=True)`. Python's glob silently refuses
to descend a `**` wildcard segment into a hidden (dot-prefixed) directory
UNLESS that hidden segment is a LITERAL component of the pattern itself
(matched exactly, not via a wildcard). Every battery rep's real content
lives under `<rep>/<container>/home/.codex/sessions/...` -- `.codex` is
hidden. Calling `fork_stats(rep_dir)` directly on a rep's root therefore
silently returns ZERO children for every single rep (verified: 0 children,
matching the ~0.05s runtime of a walk that finds nothing) -- not an error,
just silent total data loss. Task 2's own corpus validation never hit this
because it always pointed `fork_stats()` directly at an already-resolved
path past `.codex` (e.g. `~/.codex/sessions/2026/07/26`), and this task's
mined-corpus sweep (see the log entry) does the same. The exact same class
of dot-directory glob-skip bug was already found and disclosed in Task 9's
`task9_extract_signals.py find_ledger()`; the fix pattern used there
(explicit literal `.codex` path component in the glob pattern, as
`task10_extract_signals.py`'s `root_rollout()` already does) is reused here
-- this script resolves each rep's real `.../home/.codex/sessions`
directory FIRST (literal-component glob), then calls the unmodified
`fork_stats()` on that resolved path. score_x4_forktax.py itself is not
edited -- consistent with this task's "no skill/scorer edits this
campaign" scope.

FOLLOW-UP (queue-execution campaign, Task 3, item 14): this wrapper's own
`resolve_session_dirs()` had the SAME residual defect one level higher up
-- the `**` segment BEFORE the literal `home` component still silently
skips a dot-prefixed directory between REP_DIR and `home` (e.g. a real
`<rep>/.worktrees/<name>/home/.codex/sessions` shape), confirmed by direct
`glob.glob` reproduction against a fixture tree (this later task's
report). Fixed with a plain `os.walk` scan (no glob at all) -- the
literal-component discipline this docstring describes was the right
IDEA, just not fully executed by a glob pattern that still had a
wildcard segment upstream of it. `score_x4_forktax.find_rollouts()` was
ALSO fixed directly in that same later task (it now uses the same
`os.walk`-based `scorer_common.find_files()` this wrapper's rationale
predates), so this wrapper's pre-resolution step is no longer strictly
required for correctness -- kept anyway, unchanged in shape, since its
per-rep session-dir warnings (`NO session dir resolved` /
`MULTIPLE session dirs`) are still-useful diagnostics this task's scope
did not ask for removed.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from score_x4_forktax import fork_stats
from scorer_common import path_ends_with_components as _path_ends_with_components

RESULT_ROOTS = [
    "/Users/jesse/git/superpowers/superpowers/evals/results",
    "/Users/jesse/git/superpowers/evals-lane-b/results",
]

# Task 6's pre-battery smoke landed under a doubled 'cp-cp-' prefix
# (disclosed minor, Task 6 log entry) -- not one of the pre-registered
# battery reps graded in Tasks 8-11; excluded by name.
EXCLUDE_PREFIXES = ("cp-cp-",)


def resolve_session_dirs(rep_dir):
    """Every `.../home/.codex/sessions` directory under rep_dir, found via
    `os.walk` (see module docstring's FOLLOW-UP note -- the prior
    glob-based version's leading `**` segment, BEFORE the literal `home`
    component, could still skip a dot-prefixed directory between rep_dir
    and `home`). Uses `scorer_common.path_ends_with_components` (ROUND-1
    REVIEW FIX) rather than `str.endswith`, which matched on characters
    and falsely accepted a directory named `somehome` as ending in
    `home`."""
    target_suffix = os.path.join("home", ".codex", "sessions")
    hits = []
    for dirpath, _dirnames, _filenames in os.walk(rep_dir):
        if _path_ends_with_components(dirpath, target_suffix):
            hits.append(dirpath)
    return sorted(hits)


def discover_reps():
    """(lane, scenario, arm, rep_n, rep_dir) for every cp-* rep directory
    across both result roots, excluding the Task 6 smoke stray."""
    reps = []
    for root in RESULT_ROOTS:
        lane = "lane-a" if "evals-lane-b" not in root else "lane-b"
        if not os.path.isdir(root):
            continue
        for name in sorted(os.listdir(root)):
            if not name.startswith("cp-"):
                continue
            if any(name.startswith(p) for p in EXCLUDE_PREFIXES):
                continue
            rep_dir = os.path.join(root, name)
            if not os.path.isdir(rep_dir):
                continue
            # name shape: cp-<scenario...>-<arm>-rep<N>
            if "-rep" not in name:
                continue
            base, _, repnum = name.rpartition("-rep")
            scenario_arm = base
            reps.append((lane, scenario_arm, repnum, rep_dir))
    return reps


def main():
    reps = discover_reps()
    all_children = []
    per_rep = []
    warnings = []
    for lane, scenario_arm, repnum, rep_dir in reps:
        sess_dirs = resolve_session_dirs(rep_dir)
        if len(sess_dirs) == 0:
            warnings.append(f"NO session dir resolved under {rep_dir}")
            continue
        if len(sess_dirs) > 1:
            warnings.append(f"MULTIPLE session dirs under {rep_dir}: {sess_dirs}")
        rep_children = []
        for sd in sess_dirs:
            r = fork_stats(sd)
            rep_children.extend(r["children"])
        for c in rep_children:
            c["lane"] = lane
            c["scenario_arm"] = scenario_arm
            c["rep"] = repnum
        all_children.extend(rep_children)
        per_rep.append({
            "lane": lane,
            "scenario_arm": scenario_arm,
            "rep": repnum,
            "n_children": len(rep_children),
            "mean_byte_ratio": (sum(c["byte_ratio"] for c in rep_children) / len(rep_children)) if rep_children else None,
            "mean_dup_ratio": (sum(c["inherited_prefix_duplicate_ratio"] for c in rep_children) / len(rep_children)) if rep_children else None,
        })

    out = {
        "n_reps_scanned": len(reps),
        "n_reps_with_children": sum(1 for r in per_rep if r["n_children"] > 0),
        "n_children_total": len(all_children),
        "warnings": warnings,
        "per_rep": per_rep,
        "children": all_children,
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
