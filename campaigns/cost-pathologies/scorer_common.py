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
"""
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
