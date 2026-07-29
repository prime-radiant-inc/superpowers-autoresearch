#!/usr/bin/env python3
"""Thin adapter: run rollout_parser (trusted, unmodified) over Drew Ritter's
external SDD head-to-head corpus's Codex rollouts (Amendment 1, "Drew-corpus
cross-validation" task).

Corpus (read-only, external, NEVER committed --
/Users/jesse/git/superpowers/_tmp/drew-sdd-head-to-head-2026-07-27/sdd-testing-fresh):
- transcripts/codex-5_5/rollouts/  -- fractals run, GPT-5.5 controller
- transcripts/sol-5_6/rollouts/    -- fractals run, GPT-5.6-sol controller
- transcripts/stress-2703/rollouts/ -- 12.4h real interactive session, 68 files

Why an adapter instead of extending score_e1.py or rollout_parser.py:
score_e1.py's run-dir discovery expects a quorum battery layout
(RUNDIR/home/.codex/sessions/**/*.jsonl, one battery rep per RUNDIR). Drew's
corpus is just a flat rollouts/ directory per run -- a different discovery
problem, not a scoring-logic change -- so this script does its own discovery
and calls rollout_parser's extract_spawns/child_links/parse_session exactly
as they are.

Depth attribution: Codex Desktop's rollout format carries parent/depth
directly in each rollout's first line
(payload.source.subagent.thread_spawn.{parent_thread_id,depth} for
subagent threads; payload.thread_source == "user" => depth 0 for the root).
That's read directly here (own_thread_id/read_session_meta) rather than by
reconstructing depth from child_links -- simpler and authoritative for this
corpus, since every child rollout carries its own depth already.

Schema note (load-bearing for the reconciliation table -- see
out/drew-cross-validation.md): codex-5_5 uses spawn_agent's "multi_agent_v1"
namespace, whose arguments are {fork_context: bool, model, reasoning_effort,
message} -- NO "fork_turns" or "task_name" key. sol-5_6 and stress-2703 use
the "collaboration" namespace, whose arguments are {fork_turns: str,
task_name, model, reasoning_effort, message} -- matching what
rollout_parser.extract_spawns() was built to read (and matching our own
audit-corpus / eval-container schema). So for codex-5_5 ONLY,
extract_spawns()'s fork_turns/task_name fields read as "(omitted)" for
EVERY spawn -- not because the run's spawns lack isolation info, but because
that run's tool schema encodes it under a different key. This adapter also
does a narrow, adapter-level (not rollout_parser-level) raw peek at
fork_context values for codex-5_5, strictly for the reconciliation report --
it does not feed back into rollout_parser.py or score_e1.py.

Never extracts or prints message/instruction text -- extract_spawns()'s
Spawn tuple has no such field, and the adapter-level raw peek reads only the
fork_context key.

Usage: drew_adapter.py [CORPUS_ROOT]
Prints a report (per-run tables + aggregate) to stdout. Read-only; writes
nothing.
"""
import glob
import json
import os
import re
import sys
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rollout_parser as rp

DEFAULT_CORPUS_ROOT = (
    "/Users/jesse/git/superpowers/_tmp/drew-sdd-head-to-head-2026-07-27/"
    "sdd-testing-fresh"
)

RUNS = {
    "codex-5_5": "transcripts/codex-5_5/rollouts",
    "sol-5_6": "transcripts/sol-5_6/rollouts",
    "stress-2703": "transcripts/stress-2703/rollouts",
}

ROLLOUT_UUID_RE = re.compile(r"-([0-9a-f]{8}-[0-9a-f-]{27})\.jsonl$")


def own_thread_id(path):
    m = ROLLOUT_UUID_RE.search(os.path.basename(path))
    return m.group(1) if m else None


def read_session_meta(path):
    """First-line session_meta only: session_id, thread_source, cli_version,
    originator, depth, parent_thread_id. depth/parent come straight from
    payload.source.subagent.thread_spawn for subagent threads (present
    directly in Codex Desktop's rollout format)."""
    with open(path, "rb") as f:
        first = f.readline()
    try:
        rec = json.loads(first)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}
    p = rec.get("payload", {}) or {}
    meta = {
        "session_id": p.get("session_id"),
        "thread_source": p.get("thread_source"),
        "cli_version": p.get("cli_version"),
        "originator": p.get("originator"),
        "depth": 0 if p.get("thread_source") == "user" else None,
        "parent_thread_id": None,
    }
    src = p.get("source")
    if isinstance(src, dict):
        spawn = (src.get("subagent") or {}).get("thread_spawn")
        if isinstance(spawn, dict):
            meta["depth"] = spawn.get("depth")
            meta["parent_thread_id"] = spawn.get("parent_thread_id")
    return meta


def raw_fork_context_values(path):
    """Adapter-level (NOT rollout_parser) peek at raw spawn_agent argument
    key sets -- reads only the boolean fork_context value per spawn, never
    message/instruction text. Used solely to characterize the
    multi_agent_v1-namespace runs (codex-5_5) where extract_spawns()'s
    fork_turns field can't see isolation info (see module docstring)."""
    out = []
    for ts, typ, p in rp.iter_records(path):
        if typ == "response_item" and p.get("type") == "function_call" \
           and p.get("name") == "spawn_agent":
            try:
                args = json.loads(p.get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            if "fork_context" in args:
                out.append(args["fork_context"])
    return out


def discover(run_dir):
    return sorted(glob.glob(os.path.join(run_dir, "*.jsonl")))


def analyze_run(label, run_dir):
    paths = discover(run_dir)
    if not paths:
        raise SystemExit(f"drew_adapter: no rollout files found under {run_dir}")

    metas = {}
    for p in paths:
        tid = own_thread_id(p)
        m = read_session_meta(p)
        m["path"] = p
        metas[tid] = m

    root_path = paths[0]
    root_tid = own_thread_id(root_path)
    if metas[root_tid]["depth"] != 0:
        print(f"WARNING: {label}: earliest-by-filename rollout is not "
              f"depth 0 (got {metas[root_tid]['depth']}) -- root "
              f"identification may be wrong", file=sys.stderr)

    all_spawns = []          # (issuer_tid, issuer_depth, Spawn)
    metrics_by_tid = {}      # tid -> SessionMetrics
    fork_context_raw = collections.Counter()
    spawn_calls_regex_total = 0

    for p in paths:
        tid = own_thread_id(p)
        depth = metas.get(tid, {}).get("depth")
        spawns = rp.extract_spawns(p)
        for s in spawns:
            all_spawns.append((tid, depth, s))
        sm = rp.parse_session(p)
        metrics_by_tid[tid] = sm
        spawn_calls_regex_total += sm.spawn_calls
        for fc in raw_fork_context_values(p):
            fork_context_raw[fc] += 1

    # Cross-check: extract_spawns() total vs parse_session's regex-classifier
    # spawn_calls total -- these are two independently-coded predicates in
    # rollout_parser.py (see its SPAWN_NAMES/SPAWN_RE comment); they should
    # agree exactly on Codex API rollouts.
    extract_total = len(all_spawns)

    # child_links-based resolution (root only, matching score_e1.py's own
    # convention) -- which spawns' children have a persisted rollout file.
    root_links = rp.child_links(root_path)
    basenames = {own_thread_id(p): p for p in paths}
    resolved_from_root = set()
    for call_id, thread_id in root_links.items():
        if thread_id in basenames:
            resolved_from_root.add(thread_id)
    non_root_tids = set(metas) - {root_tid}
    orphans = non_root_tids - resolved_from_root

    fork_turns_dist = collections.Counter(s.fork_turns for _, _, s in all_spawns)
    explicit_model = sum(1 for _, _, s in all_spawns if s.model != rp.OMIT)
    depth_dist = collections.Counter(depth for _, depth, _ in all_spawns)

    total_compactions = sum(m.compactions for m in metrics_by_tid.values())
    root_compactions = metrics_by_tid[root_tid].compactions
    child_compactions = total_compactions - root_compactions
    total_wait_calls = sum(m.wait_calls for m in metrics_by_tid.values())
    root_wait_calls = metrics_by_tid[root_tid].wait_calls
    files_with_task_complete = sum(
        1 for m in metrics_by_tid.values() if m.task_complete >= 1)

    return {
        "label": label,
        "run_dir": run_dir,
        "n_rollout_files": len(paths),
        "n_children_files": len(paths) - 1,
        "root_tid": root_tid,
        "extract_spawns_total": extract_total,
        "spawn_calls_regex_total": spawn_calls_regex_total,
        "fork_turns_dist": dict(fork_turns_dist),
        "explicit_model": explicit_model,
        "explicit_model_pct": (explicit_model / extract_total * 100) if extract_total else 0.0,
        "depth_dist": dict(depth_dist),
        "fork_context_raw_dist": dict(fork_context_raw),
        "root_child_links_count": len(root_links),
        "root_child_links_resolved_to_file": len(resolved_from_root),
        "orphan_non_root_files": sorted(orphans),
        "total_compactions": total_compactions,
        "root_compactions": root_compactions,
        "child_compactions": child_compactions,
        "total_wait_calls": total_wait_calls,
        "root_wait_calls": root_wait_calls,
        "files_with_task_complete": files_with_task_complete,
    }


def print_report(result):
    r = result
    print(f"## {r['label']} -- `{r['run_dir']}`")
    print()
    print(f"- rollout files: {r['n_rollout_files']} "
          f"(1 root + {r['n_children_files']} non-root)")
    print(f"- extract_spawns() total: {r['extract_spawns_total']}  "
          f"(parse_session regex-classifier spawn_calls total: "
          f"{r['spawn_calls_regex_total']} -- "
          f"{'MATCH' if r['extract_spawns_total'] == r['spawn_calls_regex_total'] else 'MISMATCH'})")
    print(f"- fork_turns distribution (extract_spawns, literal field): {r['fork_turns_dist']}")
    if r['fork_context_raw_dist']:
        print(f"- adapter-level raw fork_context peek (multi_agent_v1 runs only): "
              f"{r['fork_context_raw_dist']}")
    print(f"- explicit model: {r['explicit_model']}/{r['extract_spawns_total']} "
          f"({r['explicit_model_pct']:.1f}%)")
    print(f"- depth distribution of spawns by issuer depth: {r['depth_dist']}")
    print(f"- root child_links (call_id->thread_id) count: {r['root_child_links_count']}, "
          f"resolved to a persisted rollout file: {r['root_child_links_resolved_to_file']}")
    if r['orphan_non_root_files']:
        print(f"- non-root files NOT linked from root's child_links "
              f"(recursive/depth>=2 children): {r['orphan_non_root_files']}")
    print(f"- compactions: total={r['total_compactions']} "
          f"(root={r['root_compactions']}, children={r['child_compactions']})")
    print(f"- wait_calls: total={r['total_wait_calls']} (root={r['root_wait_calls']})")
    print(f"- rollout files with >=1 task_complete: {r['files_with_task_complete']}")
    print()


def main(argv):
    corpus_root = argv[1] if len(argv) > 1 else DEFAULT_CORPUS_ROOT
    print(f"# drew_adapter.py report (corpus root: {corpus_root})")
    print()
    results = {}
    for label, rel_dir in RUNS.items():
        run_dir = os.path.join(corpus_root, rel_dir)
        result = analyze_run(label, run_dir)
        results[label] = result
        print_report(result)

    print("## Aggregate across all three runs")
    print()
    total_spawns = sum(r["extract_spawns_total"] for r in results.values())
    total_explicit_model = sum(r["explicit_model"] for r in results.values())
    print(f"- total spawns (extract_spawns): {total_spawns}")
    print(f"- total explicit model: {total_explicit_model} "
          f"({total_explicit_model / total_spawns * 100:.1f}%)")
    print(f"- total rollout files: "
          f"{sum(r['n_rollout_files'] for r in results.values())}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
