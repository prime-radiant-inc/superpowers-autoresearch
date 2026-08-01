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


def find_files(root, name_pattern, path_contains=None):
    """Every file under ROOT whose basename matches NAME_PATTERN (fnmatch
    glob syntax, e.g. `"rollout-*.jsonl"`), found via `os.walk` -- unlike
    `glob.glob(pattern, recursive=True)`, `os.walk` descends into
    dot-prefixed directories (see module docstring). PATH_CONTAINS, if
    given, restricts hits to full paths containing that substring (e.g.
    `os.path.join("home", ".codex", "sessions")`) -- the same specificity
    a literal-component glob pattern would have had, without the
    dot-directory blind spot in the WILDCARD segments around it."""
    hits = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if not fnmatch.fnmatch(fn, name_pattern):
                continue
            full = os.path.join(dirpath, fn)
            if path_contains and path_contains not in full:
                continue
            hits.append(full)
    return hits
