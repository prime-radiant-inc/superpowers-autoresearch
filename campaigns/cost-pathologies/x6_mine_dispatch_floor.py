#!/usr/bin/env python3
"""X6 MINE-tier dispatch-count/size distribution (queue-execution campaign,
2026-08-01, Task 7 / item 3 of reports/2026-08-cost-pathologies-campaign.md
§6's queue): "it also owes the MINE tier this campaign skipped -- a
mined-corpus dispatch-floor distribution -- so the fixture's dispatch
counts have a real baseline to sit against" (§6 item 3; the closeout's X6
row confirms the MINE tier this design doc's own "Tiers: MINE (dispatch-
floor distribution from the mined corpora)" line called for was never run).

This script closes that gap: given any corpus root on the command line, it
walks every `rollout-*.jsonl` file under it (`scorer_common.find_files()`,
dot-dir-safe -- unlike `glob.glob(..., recursive=True)`, which silently
skips hidden directories like `.codex`, see scorer_common.py's module
docstring), and for every rollout file that issues at least one resolvable
`spawn_agent` dispatch (a "dispatching session"), computes:

  - how many of that session's OWN spawn_agent calls resolve to a found
    child rollout (its dispatch COUNT);
  - each of those dispatches' `total_tokens` / `useful_output_tokens` /
    `floor_ratio`, computed exactly the way `score_x6_floor.dispatch_floor()`
    computes them (this script imports and reuses that scoring, rather than
    reimplementing it) -- just scoped per parent file here, so a dispatch
    count can be attributed to the session that issued it, which
    `dispatch_floor()`'s own flat return value does not preserve.

It then prints ONE JSON object: aggregate counts, percentiles (min/p25/
median/p75/max/mean), and a dispatch-count histogram. Nothing else.

PRIVACY IS ABSOLUTE. This script's output is AGGREGATE STATISTICS ONLY --
counts, percentiles, histogram buckets. It NEVER prints a task_name, a
rollout file path, a thread id, or any excerpt of session text, and it
takes the corpus root as its one required argument -- no real corpus path
is hardcoded anywhere in this file (the usage example below is a path
shape, not a default). Read-only; makes no writes; the corpus itself must
never be committed and no corpus-derived figure beyond an aggregate
count/percentile/histogram belongs in any committed file.

Usage (example path only, not a default):
    python3 x6_mine_dispatch_floor.py ~/.codex/sessions
"""
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "codex-efficiency"))
import rollout_parser as rp
from scorer_common import cumulative_total_tokens as _cumulative_total_tokens
from scorer_common import find_files as _find_files
from scorer_common import resolve_child_path as _resolve_child_path
from score_x6_floor import _useful_output_tokens as _useful_output_tokens


def _percentiles(values):
    """min/p25/median/p75/max/mean over VALUES (a list of numbers), with
    every key None if VALUES is empty. `statistics.quantiles` requires at
    least two data points, so a single-value list short-circuits to that
    one value for every percentile rather than calling it."""
    if not values:
        return {"n": 0, "min": None, "p25": None, "median": None,
                 "p75": None, "max": None, "mean": None}
    ordered = sorted(values)
    if len(ordered) > 1:
        quartiles = statistics.quantiles(ordered, n=4, method="inclusive")
        p25, p75 = quartiles[0], quartiles[2]
    else:
        p25 = p75 = ordered[0]
    return {
        "n": len(ordered),
        "min": ordered[0],
        "p25": p25,
        "median": statistics.median(ordered),
        "p75": p75,
        "max": ordered[-1],
        "mean": statistics.fmean(ordered),
    }


def _dispatch_count_histogram(counts, edges=(1, 2, 3, 4, 6, 11)):
    """COUNTS (a list of positive ints) bucketed by the half-open ranges
    EDGES implies -- e.g. the default (1, 2, 3, 4, 6, 11) buckets as
    "1", "2", "3", "4-5", "6-10", "11+". Every count lands in the bucket
    whose start is the LARGEST edge <= that count."""
    labels = []
    for i, start in enumerate(edges):
        end = edges[i + 1] - 1 if i + 1 < len(edges) else None
        if end is None:
            labels.append(f"{start}+")
        elif end == start:
            labels.append(f"{start}")
        else:
            labels.append(f"{start}-{end}")
    buckets = {label: 0 for label in labels}
    for c in counts:
        idx = 0
        for i, start in enumerate(edges):
            if c >= start:
                idx = i
        buckets[labels[idx]] += 1
    return buckets


def session_dispatch_counts_and_sizes(corpus_root):
    """For every rollout file under CORPUS_ROOT that issues at least one
    resolvable spawn_agent dispatch, that session's own dispatch count,
    plus every individual dispatch's total_tokens / useful_output_tokens /
    floor_ratio -- four flat lists of numbers:
    (dispatch_counts, total_tokens_values, useful_output_values,
    floor_ratio_values). Nothing identifying (no path, no task_name, no
    thread id) is retained past this function; only numbers leave it."""
    all_rollouts = _find_files(corpus_root, "rollout-*.jsonl")
    dispatch_counts = []
    total_tokens_values = []
    useful_output_values = []
    floor_ratio_values = []
    for parent_path in all_rollouts:
        spawns = rp.extract_spawns(parent_path)
        if not spawns:
            continue
        links = rp.child_links(parent_path)
        n_resolved = 0
        for s in spawns:
            thread_id = links.get(s.call_id)
            if not thread_id:
                continue
            child_path = _resolve_child_path(thread_id, all_rollouts)
            if not child_path:
                continue
            n_resolved += 1
            total_tokens = _cumulative_total_tokens(child_path)
            useful_output_tokens = _useful_output_tokens(child_path)
            if total_tokens is not None:
                total_tokens_values.append(total_tokens)
            useful_output_values.append(useful_output_tokens)
            if total_tokens is not None and useful_output_tokens:
                floor_ratio_values.append(total_tokens / useful_output_tokens)
        if n_resolved:
            dispatch_counts.append(n_resolved)
    return dispatch_counts, total_tokens_values, useful_output_values, floor_ratio_values


def aggregate(corpus_root):
    """The full aggregate-statistics-only report for CORPUS_ROOT."""
    dispatch_counts, total_tokens_values, useful_output_values, floor_ratio_values = \
        session_dispatch_counts_and_sizes(corpus_root)
    return {
        "n_dispatching_sessions": len(dispatch_counts),
        "n_dispatches_total": sum(dispatch_counts),
        "dispatch_count_distribution": _percentiles(dispatch_counts),
        "dispatch_count_histogram": _dispatch_count_histogram(dispatch_counts),
        "dispatch_total_tokens_distribution": _percentiles(total_tokens_values),
        "dispatch_useful_output_tokens_distribution": _percentiles(useful_output_values),
        "dispatch_floor_ratio_distribution": _percentiles(floor_ratio_values),
    }


def main(argv):
    if len(argv) != 2:
        print("usage: x6_mine_dispatch_floor.py CORPUS_ROOT", file=sys.stderr)
        return 1
    result = aggregate(argv[1])
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
