#!/usr/bin/env python3
"""Shared helpers for campaigns/cost-pathologies scorers.

Factored out of score_x1_chains.py / score_x4_forktax.py / score_x6_floor.py
(Task 7) to close the Task 2 DRY deferral -- `_resolve_child_path` was
duplicated across all three, `_cumulative_total_tokens` across two of them
(see logs/2026-07-31-cost-pathologies.md's Task 2 entry and
.superpowers/sdd/2026-07-31-cost-pathologies-evals/progress.md's Task 2
deferral note: "Task 7's X5 scorer MUST import shared helpers, not add copy
#3"). score_x5_leases.py (Task 7) imports from here too, rather than adding
a fourth/third copy.

Both functions below are byte-identical ports of the versions the three
original scorers carried -- see their module docstrings (still present,
historical) for the corpus-derived rationale: `cumulative_total_tokens`'s
"read the LAST token_count event, never sum across a fork" convention
(validated against real rollouts during Task 2's corpus reconciliation --
`token_count` climbs monotonically WITHIN one rollout file, so its last
value is that session's own total spend, not a per-turn delta), and
`resolve_child_path`'s "thread_id is a substring of the child rollout's own
basename" resolution rule (the corpus's actual filename convention,
`rollout-<timestamp>-<thread-id>.jsonl`).

`find_files` (queue-execution campaign, Task 3, item 14) closes a THIRD
dry-up debt of the same shape: `glob.glob(pattern, recursive=True)`'s `**`
segment silently refuses to descend into a dot-prefixed directory
(`.worktrees`, `.superpowers`, `.codex`), a bug class first disclosed in
`task9_extract_signals.py find_ledger()` (fixed there with a direct
`os.walk`, `logs/2026-07-31-cost-pathologies.md`) and independently
re-hit by `score_x4_forktax.fork_stats()` over a battery rep root (same
log, Task 12 entry: silently 0 children, no exception). Both
`find_ledger()`-style ad hoc `os.walk` loops and the dedicated
`task12_measure_forktax.py` wrapper built to route around
`fork_stats()`'s defect are workarounds for the SAME underlying gap --
every scorer/helper in this campaign that needs to locate files by name
under a tree that might contain dot-prefixed directories should call
`find_files` instead of `glob.glob(..., recursive=True)`.

`path_contains_components`/`path_ends_with_components` (same task,
ROUND-1 REVIEW FIX): `find_files`'s original `path_contains` was a bare
`in` substring test, and `task12_measure_forktax.resolve_session_dirs()`
originally used `str.endswith` directly -- both match on CHARACTERS, not
path COMPONENTS, so a directory named `somehome` was falsely accepted as
matching a wanted `home` component (the string "home/.codex/sessions" is
a genuine substring of ".../somehome/.codex/sessions"), reintroducing
the exact "safe only by accident" failure mode this task exists to
eliminate. Both matchers below split on `os.sep` and compare whole
components.
"""
import fnmatch
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "codex-efficiency"))
import rollout_parser as rp


def cumulative_total_tokens(path):
    """The LAST event_msg/token_count event's info.total_token_usage.
    total_tokens in PATH, or None if no such event exists. See module
    docstring for why "last" (not "sum") is the correct cumulative
    reading for a single rollout file."""
    last = None
    for _ts, typ, p in rp.iter_records(path):
        if typ == "event_msg" and p.get("type") == "token_count":
            info = p.get("info") or {}
            usage = info.get("total_token_usage") or {}
            total = usage.get("total_tokens")
            if isinstance(total, (int, float)):
                last = total
    return last


def resolve_child_path(thread_id, rollout_paths):
    """The first entry of ROLLOUT_PATHS whose basename contains THREAD_ID,
    or None if none match -- the corpus's real filename convention
    (`rollout-<timestamp>-<thread-id>.jsonl`)."""
    for cand in rollout_paths:
        if thread_id in os.path.basename(cand):
            return cand
    return None


def _split_components(path):
    """PATH split into its individual os.sep components, dropping the
    empty strings a leading/trailing/doubled separator would produce."""
    return [p for p in path.split(os.sep) if p]


def path_contains_components(path, subsequence):
    """Whether SUBSEQUENCE (an os.sep-joined string, e.g.
    `"home/.codex/sessions"`) appears as a CONTIGUOUS run of WHOLE path
    components anywhere in PATH -- component-exact, unlike a bare
    substring test (`subsequence in path`), which would falsely match a
    component like `"somehome"` against a wanted `"home"` (see module
    docstring's ROUND-1 REVIEW FIX note)."""
    want = _split_components(subsequence)
    have = _split_components(path)
    n = len(want)
    if n == 0 or n > len(have):
        return n == 0
    return any(have[i:i + n] == want for i in range(len(have) - n + 1))


def path_ends_with_components(path, suffix):
    """Whether PATH's own trailing path components exactly equal SUFFIX
    (an os.sep-joined string) -- component-exact, unlike `str.endswith`,
    which would falsely accept a directory named `"somehome"` as ending
    in `"home"` (see module docstring's ROUND-1 REVIEW FIX note)."""
    want = _split_components(suffix)
    if not want:
        return True
    have = _split_components(path)
    return have[-len(want):] == want


def find_files(root, name_pattern, path_contains=None):
    """Every file under ROOT whose basename matches NAME_PATTERN (fnmatch
    glob syntax, e.g. `"rollout-*.jsonl"`), found via `os.walk` -- unlike
    `glob.glob(pattern, recursive=True)`, `os.walk` descends into
    dot-prefixed directories (see module docstring). PATH_CONTAINS, if
    given, restricts hits to full paths containing that CONTIGUOUS run of
    path COMPONENTS (e.g. `os.path.join("home", ".codex", "sessions")`)
    -- the same specificity a literal-component glob pattern would have
    had, without either the dot-directory blind spot in the WILDCARD
    segments around it, or a substring/component-boundary false match
    (`path_contains_components`)."""
    hits = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if not fnmatch.fnmatch(fn, name_pattern):
                continue
            full = os.path.join(dirpath, fn)
            if path_contains and not path_contains_components(full, path_contains):
                continue
            hits.append(full)
    return hits
