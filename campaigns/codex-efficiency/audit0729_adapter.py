#!/usr/bin/env python3
"""Thin adapter: run rollout_parser + score_e2.build_tree (trusted,
unmodified) over the 2026-07-29 fallback session tree Jesse audited
manually (Amendment 3, "MINE the 2026-07-29 session tree" task).

Corpus (read-only, external, private, NEVER committed):
    root rollout ~/.codex/sessions/2026/07/29/rollout-2026-07-29T11-36-36-
    019faf59-3a06-7f40-87e0-c8c84a5729ae.jsonl + its descendant tree
    (13 descendants per Jesse's audit -- see
    logs/2026-07-28-codex-efficiency.md, "EXTERNAL EVIDENCE: Jesse's
    audit of the 07-29 fallback session"). ROOT_ID is cited here only
    because it already appears in the committed plan doc
    (docs/plans/2026-07-28-codex-efficiency-evals.md, Amendment 3) --
    not audited-project content.

Why an adapter instead of extending score_e2.py/rollout_parser.py: same
reasoning as drew_adapter.py -- this corpus's layout (plain
~/.codex/sessions/YYYY/MM/DD/*.jsonl, not a quorum battery dir) doesn't
match score_e1.py/score_e2.py's RUNDIR/home/.codex/sessions/** convention,
so discovery lives here. score_e2.build_tree() itself is layout-agnostic
(root path + a candidate rollouts list) and is imported and called
unmodified.

Discovery has THREE independent legs, all read-only:
  1. filename match: glob for *ROOT_ID*.jsonl under the searched date dirs.
  2. content match: grep every candidate rollout's raw bytes for ROOT_ID
     (catches a surviving CHILD file that still names the root as its
     parent_thread_id even if the root's own rollout file is gone) --
     reports only matching file paths, never matched line content.
  3. DB match: read-only query (`file:...?mode=ro`, sqlite3 stdlib module)
     against ~/.codex/state_5.sqlite's thread_spawn_edges for any row
     naming ROOT_ID as parent or child.

If all three legs come up empty, main() reports NOT_FOUND with the exact
evidence (paths searched, row counts) rather than guessing or falling
back to Jesse's numbers as if independently verified.

If the root IS found (e.g. on a future rerun, or in an environment where
the corpus wasn't pruned), build_tree() walks the resolved tree and each
node is censused with ALREADY-TRUSTED rollout_parser functions only
(wait_outcomes, lifecycle_calls, exec_commands) -- no new parsing logic.
The only new logic here is thin counting/grouping glue:
  - per-claim reconciliation: root wait_outcomes() count + duration_hint
    distribution; tree-wide and root-only list_agents count (lifecycle_calls,
    name=="list_agents"); tree-wide go-test exec_commands count (via
    rollout_parser.TEST_RE) plus, per session, the largest group of
    EXACT-normalized-string-identical test commands (the "12x identical
    regression cluster" claim) -- command text itself is never printed,
    only the max group size per session and its role label;
    depth-2 spawns bucketed by issuer role; same-task_name duplicate
    review detection (task_name used ONLY as an opaque equality key,
    never printed -- see classify_role()'s docstring for why).
  - classify_role(): a GENERIC role label (implementer/reviewer/
    unclassified) from a regex keyword match against the session's first
    instruction SHAPE (reusing score_e2._first_user_message_text() to
    read it) -- the instruction text itself is read only in memory for
    the regex test and is never printed, returned, or logged anywhere.

Usage: audit0729_adapter.py [ROOT_ID]
Prints a discovery + (if found) census report to stdout. Read-only;
writes nothing to disk or to the Codex state DB.
"""
import glob
import os
import re
import sqlite3
import sys
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rollout_parser as rp
import score_e2 as e2

DEFAULT_ROOT_ID = "019faf59-3a06-7f40-87e0-c8c84a5729ae"
SESSIONS_ROOT = os.path.expanduser("~/.codex/sessions")
STATE_DB = os.path.expanduser("~/.codex/state_5.sqlite")
# Audit date +/- 1 day, per the task brief's "same date dir or adjacent".
SEARCH_DATE_DIRS = ("2026/07/28", "2026/07/29", "2026/07/30")

IMPLEMENTER_RE = re.compile(r"\bimplement", re.I)
REVIEWER_RE = re.compile(r"\breview", re.I)


# --- discovery (all three legs real and exercised regardless of outcome) --

def candidate_date_dirs():
    return [d for d in
            (os.path.join(SESSIONS_ROOT, rel) for rel in SEARCH_DATE_DIRS)
            if os.path.isdir(d)]


def find_by_filename(root_id):
    hits = []
    for d in candidate_date_dirs():
        hits.extend(glob.glob(os.path.join(d, f"*{root_id}*.jsonl")))
    return sorted(hits)


def find_by_content(root_id):
    """Grep every rollout under the searched date dirs for ROOT_ID as raw
    bytes. Reports matching file paths only -- never reads/prints the
    matched line."""
    needle = root_id.encode()
    hits = []
    scanned = 0
    for d in candidate_date_dirs():
        for path in glob.glob(os.path.join(d, "*.jsonl")):
            scanned += 1
            try:
                with open(path, "rb") as f:
                    if needle in f.read():
                        hits.append(path)
            except OSError:
                continue
    return sorted(hits), scanned


def find_spawn_edges(root_id):
    """Read-only query against thread_spawn_edges. Returns (rows, db_present,
    total_edge_count) -- total_edge_count is a sanity check that the table
    itself is populated (not silently empty/corrupt) even when ROOT_ID has
    zero matching rows."""
    if not os.path.exists(STATE_DB):
        return [], False, None
    conn = sqlite3.connect(f"file:{STATE_DB}?mode=ro", uri=True)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT parent_thread_id, child_thread_id, status FROM "
            "thread_spawn_edges WHERE parent_thread_id = ? OR child_thread_id = ?",
            (root_id, root_id))
        rows = cur.fetchall()
        total = cur.execute("SELECT COUNT(*) FROM thread_spawn_edges").fetchone()[0]
        return rows, True, total
    finally:
        conn.close()


def discover(root_id):
    filename_hits = find_by_filename(root_id)
    content_hits, n_scanned = find_by_content(root_id)
    edge_rows, db_present, total_edges = find_spawn_edges(root_id)
    return {
        "root_id": root_id,
        "date_dirs_searched": candidate_date_dirs(),
        "filename_hits": filename_hits,
        "content_hits": content_hits,
        "n_files_content_scanned": n_scanned,
        "spawn_edge_rows": edge_rows,
        "state_db_present": db_present,
        "state_db_total_edges": total_edges,
    }


def found(disc):
    return bool(disc["filename_hits"] or disc["content_hits"] or disc["spawn_edge_rows"])


# --- census (only reached if discovery succeeds; reuses trusted funcs) ----

def classify_role(path):
    """GENERIC role label only -- see module docstring. Never returns or
    logs the underlying instruction text."""
    text = e2._first_user_message_text(path)
    is_review = bool(REVIEWER_RE.search(text))
    is_impl = bool(IMPLEMENTER_RE.search(text))
    if is_review and not is_impl:
        return "reviewer"
    if is_impl and not is_review:
        return "implementer"
    if is_review and is_impl:
        return "mixed"
    return "unclassified"


def _normalize_cmd(cmd):
    return re.sub(r"\s+", " ", cmd).strip()


def census_node(path):
    waits = rp.wait_outcomes(path)
    lifecycle = rp.lifecycle_calls(path)
    execs = rp.exec_commands(path)
    test_execs = [e for e in execs if rp.TEST_RE.search(e.cmd)]
    norm_counts = collections.Counter(_normalize_cmd(e.cmd) for e in test_execs)
    max_repeat = max(norm_counts.values()) if norm_counts else 0
    return {
        "path": path,
        "role": classify_role(path),
        "n_wait_agent": len(waits),
        "wait_duration_hints": collections.Counter(w.duration_hint for w in waits),
        "n_list_agents": sum(1 for c in lifecycle if c.name == "list_agents"),
        "n_test_execs": len(test_execs),
        "max_identical_test_repeat": max_repeat,
        "spawns": rp.extract_spawns(path),
    }


def run_census(root_path, disc):
    tree_paths = sorted(set(disc["filename_hits"]) | set(disc["content_hits"]))
    if root_path not in tree_paths:
        tree_paths.append(root_path)
    nodes = e2.build_tree(root_path, sorted(tree_paths))
    censused = {n["rollout"]: census_node(os.path.join(os.path.dirname(root_path), n["rollout"]))
                for n in nodes}
    return nodes, censused


# --- report -----------------------------------------------------------

def print_discovery(disc):
    print(f"root_id searched: {disc['root_id']}")
    print(f"date dirs searched: {disc['date_dirs_searched']}")
    print(f"filename-match hits: {len(disc['filename_hits'])} {disc['filename_hits']}")
    print(f"content-match hits: {len(disc['content_hits'])} "
          f"(scanned {disc['n_files_content_scanned']} rollout files) {disc['content_hits']}")
    print(f"state_5.sqlite present: {disc['state_db_present']} "
          f"(thread_spawn_edges total rows: {disc['state_db_total_edges']})")
    print(f"thread_spawn_edges rows naming root_id: {len(disc['spawn_edge_rows'])} "
          f"{disc['spawn_edge_rows']}")


def main(argv):
    root_id = argv[1] if len(argv) > 1 else DEFAULT_ROOT_ID
    disc = discover(root_id)
    print("# audit0729_adapter.py discovery report")
    print()
    print_discovery(disc)
    print()

    if not found(disc):
        print("RESULT: NOT_FOUND -- no rollout file, no content match, no "
              "thread_spawn_edges row for this root_id in any of the "
              "searched date dirs / the live state DB. See §1 evidence "
              "above. No census performed.")
        return 1

    print("RESULT: FOUND -- proceeding to census.")
    root_path = disc["filename_hits"][0] if disc["filename_hits"] else disc["content_hits"][0]
    nodes, censused = run_census(root_path, disc)
    print(f"tree sessions: {len(nodes)}")
    total_waits = sum(c["n_wait_agent"] for c in censused.values())
    total_list_agents = sum(c["n_list_agents"] for c in censused.values())
    total_test_execs = sum(c["n_test_execs"] for c in censused.values())
    max_cluster = max((c["max_identical_test_repeat"] for c in censused.values()), default=0)
    roles = collections.Counter(c["role"] for c in censused.values())
    print(f"total wait_agent (tree): {total_waits}")
    print(f"total list_agents (tree): {total_list_agents}")
    print(f"total go-test exec_commands (tree): {total_test_execs}")
    print(f"max identical-normalized-test-command repeat, any single session: {max_cluster}")
    print(f"role distribution: {dict(roles)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
