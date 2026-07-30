#!/usr/bin/env python3
"""E2 reviewer-recursion scorer (Task 8, FULL branch-review baseline).

For each RUNDIR (a single quorum run's coding-agent directory, i.e. the
directory containing `home/.codex/sessions/**` and `verdict.json` -- one
level below a `results/cx-eff-<scenario>-<arm>-repN/` battery dir), this
walks the run's rollout tree TRANSITIVELY: starting from the root (the
chronologically-earliest rollout -- rollout filenames embed an ISO
timestamp, so sorting by filename sorts by creation time), it follows
every session's OWN `extract_spawns()`/`child_links()` output to discover
further descendants, not just the root's direct spawns. A reviewer that
itself spawns further reviewers is exactly the recursion this experiment
measures, so the walk cannot stop at depth 1 the way a shallower census
would.

Census fields produced per run (DESIGN.md's E2 package: "descendants, max
depth, thread-limit failures, sessions missing task_complete, wait-call
volume"):

  - total_sessions      -- size of the tree reachable from root (root
                            included), via resolved spawn -> child links.
  - max_depth           -- root = depth 0; a direct root spawn = depth 1;
                            a spawn issued BY that child = depth 2; etc.
  - spawns_by_nonroot   -- spawn_agent calls issued by any session in the
                            tree OTHER than the root. This is the
                            recursion signal: the root dispatching one
                            reviewer is the expected/intended shape
                            (spawns_by_nonroot counts nothing for that);
                            the reviewer child (or anything deeper) then
                            spawning MORE agents is what this counts.
  - missing_task_complete -- rollouts in the tree with zero task_complete
                            events (parse_session().task_complete == 0).
  - total_wait_calls / root_wait_calls -- parse_session().wait_calls
                            summed across the tree, and for the root
                            alone.
  - orphan_rollouts     -- rollout files present under the run's session
                            dir that never resolve into the tree (no
                            spawn anywhere in the tree links to them) --
                            same convention as score_e1.py's field of the
                            same name.

`extract_spawns()`/`child_links()`/`parse_session()` never surface
message/instruction text, so the tree walk itself reads no session
content. The one exception: `_root_matches_review_request()` reads the
ROOT session's first `event_msg/user_message` payload's `message` string
once, to assert the root picked by filename-chronology is genuinely the
session that received the Gauntlet's fixed review request (see
scenarios/cx-branch-review/story.md) -- this is our OWN fixed scenario
prompt, not corpus/client content, so checking it for a known substring
(and reporting only the boolean match, never the raw text) is safe per
this campaign's established precedent (Gauntlet-prompt text and
fixture/task_name labels have always been treated as citable process
text, never corpus content -- see score_e1.py's module docstring).

score_run() raises SystemExit if that assertion fails -- a false result
here means the "root == controller that received the review request"
assumption this entire census is built on is wrong for that rep, so
every other field would be meaningless; better to fail loudly per-rep
than silently score the wrong session as root.

Usage:
    score_e2.py RUNDIR...

Prints a markdown report (per-run census + a per-run node table, then an
aggregate summary across all given RUNDIRs) to stdout, and writes a JSON
blob of the same census records to
campaigns/codex-efficiency/out/e2-<label>.json (label derived exactly
like score_e1.py's -- arm_scenario plus the actual rep range scored, so a
REP_START-extended re-score of a different rep range doesn't collide with
an earlier score's output file). Refuses to overwrite an existing output
file unless env FORCE=1 is set. Exits 0 on success, 1 on usage error, an
existing-output-file collision without FORCE, or a run with zero
resolvable rollouts.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rollout_parser as rp

REP_DIR_RE = re.compile(r"^cx-eff-(?P<arm_scenario>.+)-rep(?P<rep>\d+)$")

# Substring the root session's first instruction must contain (case-
# insensitive) to confirm it's the session that received the Gauntlet's
# fixed review request (scenarios/cx-branch-review/story.md's exact typed
# message: "Please do a final review of the feature branch using your
# superpowers review skills before we merge.").
REVIEW_REQUEST_MARKER = "final review of the feature branch"


def find_rollouts(rundir):
    pattern = os.path.join(rundir, "home", ".codex", "sessions", "**", "*.jsonl")
    return sorted(glob.glob(pattern, recursive=True))


def _parent_label(rundir):
    """Derive (arm_scenario_label, rep_number) from the battery dir name one
    level above RUNDIR -- identical convention to score_e1.py's helper of
    the same name."""
    parent = os.path.basename(os.path.dirname(os.path.abspath(rundir.rstrip("/"))))
    m = REP_DIR_RE.match(parent)
    if m:
        return m.group("arm_scenario"), int(m.group("rep"))
    return parent, None


def _resolve_child_path(thread_id, rollouts):
    for cand in rollouts:
        if thread_id in os.path.basename(cand):
            return cand
    return None


def _first_user_message_text(path):
    """Read the first event_msg/user_message payload's `message` string off
    PATH. Used only by _root_matches_review_request's structural sanity
    check -- the raw text this returns is never printed by score_run(),
    only whether REVIEW_REQUEST_MARKER is found in it."""
    for _ts, typ, p in rp.iter_records(path):
        if typ == "event_msg" and p.get("type") == "user_message":
            msg = p.get("message")
            return msg if isinstance(msg, str) else ""
    return ""


def _root_matches_review_request(root_path):
    text = _first_user_message_text(root_path)
    return REVIEW_REQUEST_MARKER.lower() in text.lower()


def build_tree(root, rollouts):
    """BFS from `root`, following ONLY resolved spawn -> child links (an
    unresolved spawn, or a rollout no spawn anywhere in the tree links to,
    is not part of the tree -- same convention as score_e1.py's
    orphan_rollouts). Returns the list of node dicts, each: rollout
    (basename), depth, parent_rollout, is_root, spawn_count,
    task_complete, wait_calls."""
    nodes = []
    visited = set()
    frontier = [(root, 0, None)]
    while frontier:
        path, depth, parent_path = frontier.pop(0)
        key = os.path.basename(path)
        if key in visited:
            continue
        visited.add(key)
        spawns = rp.extract_spawns(path)
        links = rp.child_links(path)
        metrics = rp.parse_session(path)
        nodes.append({
            "rollout": key,
            "depth": depth,
            "parent_rollout": os.path.basename(parent_path) if parent_path else None,
            "is_root": path == root,
            "spawn_count": len(spawns),
            "task_complete": metrics.task_complete,
            "wait_calls": metrics.wait_calls,
        })
        for s in spawns:
            thread_id = links.get(s.call_id)
            if not thread_id:
                continue
            child_path = _resolve_child_path(thread_id, rollouts)
            if child_path and os.path.basename(child_path) not in visited:
                frontier.append((child_path, depth + 1, path))
    return nodes


def score_run(rundir):
    rundir = rundir.rstrip("/")
    arm_scenario, rep = _parent_label(rundir)
    rollouts = find_rollouts(rundir)
    if not rollouts:
        raise SystemExit(f"score_e2: no rollout files found under {rundir}/home/.codex/sessions/**")
    root = rollouts[0]

    root_matches_review_request = _root_matches_review_request(root)
    if not root_matches_review_request:
        raise SystemExit(
            f"score_e2: root-identity assertion FAILED for {rundir} -- the "
            f"chronologically-earliest rollout ({os.path.basename(root)}) "
            f"does not contain the review-request marker "
            f"({REVIEW_REQUEST_MARKER!r}) in its first instruction. Refusing "
            f"to score a tree built on the wrong root.")

    nodes = build_tree(root, rollouts)

    total_sessions = len(nodes)
    max_depth = max(n["depth"] for n in nodes)
    spawns_by_nonroot = sum(n["spawn_count"] for n in nodes if not n["is_root"])
    missing_task_complete = [n["rollout"] for n in nodes if n["task_complete"] < 1]
    total_wait_calls = sum(n["wait_calls"] for n in nodes)
    root_wait_calls = next(n["wait_calls"] for n in nodes if n["is_root"])

    tree_basenames = {n["rollout"] for n in nodes}
    orphan_rollouts = sorted(
        os.path.basename(p) for p in rollouts if os.path.basename(p) not in tree_basenames)

    return {
        "rundir": rundir,
        "arm_scenario": arm_scenario,
        "rep": rep,
        "root_rollout": os.path.basename(root),
        "root_matches_review_request": root_matches_review_request,
        "rollout_count_total": len(rollouts),
        "total_sessions": total_sessions,
        "max_depth": max_depth,
        "spawns_by_nonroot": spawns_by_nonroot,
        "missing_task_complete": missing_task_complete,
        "n_missing_task_complete": len(missing_task_complete),
        "total_wait_calls": total_wait_calls,
        "root_wait_calls": root_wait_calls,
        "orphan_rollouts": orphan_rollouts,
        "nodes": nodes,
    }


def print_run_table(run):
    label = f"{run['arm_scenario']} rep{run['rep']}" if run["rep"] is not None else run["arm_scenario"]
    print(f"### {label} -- `{run['rundir']}`")
    print()
    print(f"root rollout: `{run['root_rollout']}` (root-identity check: "
          f"{'PASS' if run['root_matches_review_request'] else 'FAIL'})")
    print(f"rollout files total: {run['rollout_count_total']}  "
          f"tree sessions: {run['total_sessions']}  max depth: {run['max_depth']}")
    if run["orphan_rollouts"]:
        print(f"orphan rollouts (not in the resolved tree): {run['orphan_rollouts']}")
    print()
    print("| rollout | depth | parent | spawns | task_complete | wait_calls |")
    print("|---|---|---|---|---|---|")
    for n in sorted(run["nodes"], key=lambda x: (x["depth"], x["rollout"])):
        marker = " (root)" if n["is_root"] else ""
        print(f"| {n['rollout']}{marker} | {n['depth']} | {n['parent_rollout']} | "
              f"{n['spawn_count']} | {n['task_complete']} | {n['wait_calls']} |")
    print()
    print(f"**spawns_by_nonroot={run['spawns_by_nonroot']}**  "
          f"missing_task_complete={run['n_missing_task_complete']} "
          f"{run['missing_task_complete'] or ''}  "
          f"total_wait_calls={run['total_wait_calls']} "
          f"(root alone: {run['root_wait_calls']})")
    print()


def _rep_range_suffix(runs):
    """Identical convention to score_e1.py's helper of the same name."""
    reps = sorted({r["rep"] for r in runs if r["rep"] is not None})
    if not reps:
        return "unknown-reps"
    if len(reps) == 1:
        return f"rep{reps[0]}"
    return f"rep{reps[0]}-{reps[-1]}"


def _out_label(runs):
    arm_scenarios = sorted({r["arm_scenario"] for r in runs})
    base = arm_scenarios[0] if len(arm_scenarios) == 1 else "mixed-" + "-".join(arm_scenarios)
    return f"{base}-{_rep_range_suffix(runs)}"


def write_output(runs, out_dir, force=False):
    label = _out_label(runs)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"e2-{label}.json")
    if os.path.exists(out_path) and not force:
        print(f"score_e2: refusing to overwrite existing {out_path} "
              f"-- set env FORCE=1 to overwrite", file=sys.stderr)
        return out_path, False
    with open(out_path, "w") as f:
        json.dump({"label": label, "runs": runs}, f, indent=2)
    return out_path, True


def main(argv):
    if len(argv) < 2:
        print("usage: score_e2.py RUNDIR...", file=sys.stderr)
        return 1

    runs = [score_run(rd) for rd in argv[1:]]

    print(f"# E2 reviewer-recursion scorer output ({len(runs)} run(s))")
    print()
    for run in runs:
        print_run_table(run)

    print("## Aggregate across all given RUNDIRs")
    print()
    n_runs = len(runs)
    n_with_descendants = sum(1 for r in runs if r["total_sessions"] > 1)
    n_with_nonroot_spawns = sum(1 for r in runs if r["spawns_by_nonroot"] > 0)
    print(f"reps scored={n_runs}  reps with >=1 descendant={n_with_descendants} "
          f"({n_with_descendants}/{n_runs})  "
          f"reps with >=1 nonroot spawn (recursion)={n_with_nonroot_spawns} "
          f"({n_with_nonroot_spawns}/{n_runs})")
    print(f"max_depth across all reps: {max((r['max_depth'] for r in runs), default=0)}")
    print(f"total sessions across all reps: {sum(r['total_sessions'] for r in runs)}")
    print()

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    force = os.environ.get("FORCE") == "1"
    out_path, wrote = write_output(runs, out_dir, force=force)
    if not wrote:
        return 1
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
