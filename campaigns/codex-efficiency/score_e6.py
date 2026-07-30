#!/usr/bin/env python3
"""E6 compaction-recovery scorer (Task 9).

For each RUNDIR (a single quorum run's coding-agent directory, i.e. the
directory containing `home/.codex/sessions/**` and `verdict.json` -- one
level below a `results/cx-eff-<scenario>-<arm>-repN/` battery dir), this
reuses score_e2.build_tree() (already-tested transitive spawn -> child
walk, gives depth/parent_rollout/is_root per session) and, PER SESSION,
partitions that session's own timeline at its FIRST
event_msg/context_compacted marker (rollout_parser.compaction_events()) to
answer E6's four pre-registered questions:

  a) Post-compaction skill re-reads: SKILL.md paths
     (rollout_parser.skill_reads()) read on BOTH sides of the first
     compaction, per session -- `re_read_skill_paths` / `has_compaction`.
  b) Bootstrap/routing retention: fork_turns/model-explicitness of
     extract_spawns() spawns before vs after the first compaction,
     compared by TIMESTAMP (per the task interface: "extract_spawns
     timestamps vs compaction timestamps") -- `pre_spawns`/`post_spawns`
     per session, `spawn_hygiene` aggregated pre/post across the run.
  c) Depth-2 spawns BY ROLE of the depth-1 spawner (implementer vs
     reviewer, via task_name assigned by that spawner's OWN parent --
     `classify_role_by_task_name`, same "review"-substring convention
     audit0729_adapter.py already established) -- `depth2_by_spawner_role`,
     `depth2_details`. Same-task duplicate reviews: a depth-1 implementer
     whose own depth-2 child is a reviewer (worker-initiated review) AND a
     SEPARATE depth-1 reviewer of the same task FAMILY spawned directly by
     root (controller-initiated duplicate) -- `duplicate_review_families`
     (the Amendment-3 "4th occurrence" pattern: implementer-spawned
     reviewer + controller-dispatched duplicate of the same task).
  d) Controller input growth: root session `lines`/`compactions` --
     `root_lines`/`root_compactions`, plus `total_compactions` across the
     whole tree (children compact independently, per
     docs/2026-07-29-codex-multiagent-v2-capabilities.md).

task_family() groups a task_name into its task-level family by stripping
trailing role suffixes (_implementer/_reviewer/_rereviewer/_fixer/_fix),
derived from the REAL task_name convention this campaign's own SDD fixture
produces (out/e1-cx-sdd-small-dev.json: task{N}_implementer/
task{N}_reviewer, final_fix/final_fix_reviewer/final_fixer/
final_rereviewer/final_reviewer) -- not a general-purpose parser.

Usage:
    score_e6.py RUNDIR...

Prints a markdown report (per-run session table + per-question summary,
then an aggregate across all given RUNDIRs) to stdout, and writes a JSON
blob to campaigns/codex-efficiency/out/e6-<label>.json (label convention
identical to score_e1.py/score_e2.py: arm_scenario plus the actual rep
range scored). Refuses to overwrite an existing output file unless env
FORCE=1 is set. Exits 0 on success, 1 on usage error, an existing-output-
file collision without FORCE, or a run with zero resolvable rollouts.
"""
import collections
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rollout_parser as rp
import score_e2 as e2

REP_DIR_RE = re.compile(r"^cx-eff-(?P<arm_scenario>.+)-rep(?P<rep>\d+)$")

# Mirrors audit0729_adapter.classify_role_by_task_name's convention (same
# "review" substring test, deliberately no \b -- task_names are
# underscore_separated, e.g. "rereview_widget"/"task1_reviewer", and \b does
# not break on "_"). Kept as a small self-contained copy here rather than a
# cross-scorer import, matching score_e1.py/score_e2.py's own precedent of
# each scorer module importing only rollout_parser.
TASK_NAME_REVIEW_RE = re.compile(r"review", re.I)


def classify_role_by_task_name(task_name):
    """GENERIC role label ("reviewer" | "implementer" | "unclassified")
    from the task_name a session's PARENT assigned when spawning it. Never
    returns, prints, or logs the task_name string itself beyond this
    bucket label."""
    if task_name in (None, rp.OMIT):
        return "unclassified"
    return "reviewer" if TASK_NAME_REVIEW_RE.search(task_name) else "implementer"


# Task-family grouping for same-task duplicate-review detection.
#
# PRIMARY rule: a leading "task<N>" (or "task_<N>") / "final" prefix, which
# is this campaign's own SDD fixture's stable task-identifying token
# regardless of how the ROLE portion after it is worded. Deliberately
# broader than any fixed role-word list: a real dev-battery run
# (cx-eff-cx-compaction-dev-rep1) named the controller's own duplicate
# review of task1 "task1_controller_review" -- a wording the original
# implementer/reviewer/fixer suffix alternation (below) didn't cover,
# which caused a real duplicate-review match to go undetected until this
# was caught by manual verification against the real rollout (never
# trust a rubric without eyeballing the match, per the campaign's
# standing discipline).
_TASK_FAMILY_PREFIX_RE = re.compile(r"^task_?(\d+)(?:_|$)|^(final)(?:_|$)", re.I)

# FALLBACK rule (only reached when the task<N>/final prefix rule above
# doesn't match): strips trailing role suffixes (repeatedly --
# "final_fix_reviewer" would need two passes: "_reviewer" then "_fix" --
# though in practice "final_..." now always matches the primary rule
# first). Kept for names that don't follow this campaign's task<N>/final
# convention at all.
_ROLE_SUFFIX_RE = re.compile(r"_(implementer|rereviewer|reviewer|fixer|fix)$", re.I)


def task_family(task_name):
    """Returns the task-level family a task_name belongs to, or None for a
    missing/omitted task_name (root spawns have no assigning parent)."""
    if task_name in (None, rp.OMIT):
        return None
    m = _TASK_FAMILY_PREFIX_RE.match(task_name)
    if m:
        return f"task{m.group(1)}" if m.group(1) else "final"
    fam = task_name
    while True:
        new = _ROLE_SUFFIX_RE.sub("", fam)
        if new == fam:
            return fam
        fam = new


def find_rollouts(rundir):
    pattern = os.path.join(rundir, "home", ".codex", "sessions", "**", "*.jsonl")
    return sorted(glob.glob(pattern, recursive=True))


def _parent_label(rundir):
    """Identical convention to score_e1.py/score_e2.py's helper of the
    same name."""
    parent = os.path.basename(os.path.dirname(os.path.abspath(rundir.rstrip("/"))))
    m = REP_DIR_RE.match(parent)
    if m:
        return m.group("arm_scenario"), int(m.group("rep"))
    return parent, None


def _task_name_by_rollout_basename(rollouts):
    """Maps each session's OWN rollout basename to the task_name its
    PARENT assigned when spawning it (parent's extract_spawns() call_id ->
    task_name, joined against the parent's child_links() call_id ->
    thread_id, resolved to a rollout basename via
    score_e2._resolve_child_path -- reused, not reimplemented, same
    convention score_e1.py/score_e2.py's own child resolution uses).
    Root has no entry (nothing spawned it)."""
    mapping = {}
    for p in rollouts:
        spawns_by_call_id = {s.call_id: s.task_name for s in rp.extract_spawns(p)}
        for call_id, thread_id in rp.child_links(p).items():
            if call_id not in spawns_by_call_id:
                continue
            child_path = e2._resolve_child_path(thread_id, rollouts)
            if child_path:
                mapping[os.path.basename(child_path)] = spawns_by_call_id[call_id]
    return mapping


def _spawn_summary(s):
    return {
        "call_id": s.call_id,
        "task_name": s.task_name,
        "fork_turns": s.fork_turns,
        "model": s.model,
        "reasoning_effort": s.reasoning_effort,
        "timestamp": s.timestamp,
    }


def _rate(spawns):
    n = len(spawns)
    if n == 0:
        return {"n": 0, "pct_isolated": None, "pct_explicit_model": None}
    isolated = sum(1 for s in spawns if s["fork_turns"] == "none")
    explicit = sum(1 for s in spawns if s["model"] != rp.OMIT)
    return {"n": n, "pct_isolated": isolated / n * 100, "pct_explicit_model": explicit / n * 100}


def score_tree(root, rollouts, label=None):
    """Core, reusable scoring pass over an already-discovered (root,
    rollouts) pair -- the same reuse seam score_e2.build_tree() offers, so
    an external corpus with a different directory layout (e.g. Drew's flat
    transcripts/<run>/rollouts/) can call this directly without going
    through find_rollouts()'s quorum-battery-layout assumption."""
    nodes = e2.build_tree(root, rollouts)
    path_by_basename = {os.path.basename(p): p for p in rollouts}
    task_name_by_basename = _task_name_by_rollout_basename(rollouts)

    sessions = []
    for n in nodes:
        basename = n["rollout"]
        path = path_by_basename[basename]
        task_name = task_name_by_basename.get(basename)
        role = classify_role_by_task_name(task_name)

        compactions = rp.compaction_events(path)
        has_compaction = bool(compactions)
        first_ts = compactions[0].timestamp if has_compaction else None

        re_read_paths = []
        if has_compaction:
            reads = rp.skill_reads(path)
            pre_paths = {r.skill_path for r in reads if r.timestamp < first_ts}
            post_paths = {r.skill_path for r in reads if r.timestamp >= first_ts}
            re_read_paths = sorted(pre_paths & post_paths)

        pre_spawns, post_spawns = [], []
        if has_compaction:
            for s in rp.extract_spawns(path):
                (pre_spawns if s.timestamp < first_ts else post_spawns).append(_spawn_summary(s))

        metrics = rp.parse_session(path)

        sessions.append({
            "rollout": basename,
            "depth": n["depth"],
            "parent_rollout": n["parent_rollout"],
            "is_root": n["is_root"],
            "task_name": task_name,
            "role": role,
            "n_compactions": len(compactions),
            "has_compaction": has_compaction,
            "first_compaction_timestamp": first_ts,
            "re_read_skill_paths": re_read_paths,
            "pre_spawns": pre_spawns,
            "post_spawns": post_spawns,
            "lines": metrics.lines,
        })

    by_basename = {s["rollout"]: s for s in sessions}
    depth1 = [s for s in sessions if s["depth"] == 1]

    # (c) depth-2 spawns by the role of their depth-1 spawner.
    depth2_by_role = collections.Counter()
    depth2_details = []
    for s in sessions:
        if s["depth"] != 2:
            continue
        spawner = by_basename.get(s["parent_rollout"])
        spawner_role = spawner["role"] if spawner else "unclassified"
        depth2_by_role[spawner_role] += 1
        depth2_details.append({
            "child_rollout": s["rollout"],
            "child_task_name": s["task_name"],
            "spawner_rollout": s["parent_rollout"],
            "spawner_role": spawner_role,
            "spawner_task_name": spawner["task_name"] if spawner else None,
        })

    # same-task duplicate reviews: an implementer (depth 1) with its OWN
    # depth-2 reviewer child (worker-initiated) AND a separate depth-1
    # reviewer of the same task family (controller-initiated duplicate).
    duplicate_review_families = []
    for impl in (s for s in depth1 if s["role"] == "implementer"):
        fam = task_family(impl["task_name"])
        if fam is None:
            continue
        worker_reviewers = [
            s for s in sessions
            if s["depth"] == 2 and s["parent_rollout"] == impl["rollout"] and s["role"] == "reviewer"
        ]
        if not worker_reviewers:
            continue
        controller_reviewers = [
            s for s in depth1
            if s["role"] == "reviewer" and task_family(s["task_name"]) == fam
        ]
        if controller_reviewers:
            duplicate_review_families.append({
                "family": fam,
                "implementer_rollout": impl["rollout"],
                "worker_reviewer_rollouts": [s["rollout"] for s in worker_reviewers],
                "controller_reviewer_rollouts": [s["rollout"] for s in controller_reviewers],
            })

    root_record = by_basename[os.path.basename(root)]
    all_pre = [sp for s in sessions for sp in s["pre_spawns"]]
    all_post = [sp for s in sessions for sp in s["post_spawns"]]

    return {
        "label": label,
        "root_rollout": os.path.basename(root),
        "total_sessions": len(sessions),
        "max_depth": max((s["depth"] for s in sessions), default=0),
        "sessions_with_compaction": sum(1 for s in sessions if s["has_compaction"]),
        "total_compactions": sum(s["n_compactions"] for s in sessions),
        "root_compactions": root_record["n_compactions"],
        "root_lines": root_record["lines"],
        "sessions_with_reread": sum(1 for s in sessions if s["re_read_skill_paths"]),
        "total_reread_events": sum(len(s["re_read_skill_paths"]) for s in sessions),
        "spawn_hygiene": {"pre": _rate(all_pre), "post": _rate(all_post)},
        "depth2_by_spawner_role": dict(depth2_by_role),
        "depth2_details": depth2_details,
        "duplicate_review_families": duplicate_review_families,
        "sessions": sessions,
    }


def score_run(rundir):
    rundir = rundir.rstrip("/")
    arm_scenario, rep = _parent_label(rundir)
    rollouts = find_rollouts(rundir)
    if not rollouts:
        raise SystemExit(f"score_e6: no rollout files found under {rundir}/home/.codex/sessions/**")
    root = rollouts[0]
    result = score_tree(root, rollouts, label=f"{arm_scenario}-rep{rep}" if rep is not None else arm_scenario)
    result["rundir"] = rundir
    result["arm_scenario"] = arm_scenario
    result["rep"] = rep
    return result


def print_run_report(run):
    label = f"{run['arm_scenario']} rep{run['rep']}" if run["rep"] is not None else run["arm_scenario"]
    print(f"### {label} -- `{run['rundir']}`")
    print()
    print(f"root rollout: `{run['root_rollout']}`  total_sessions={run['total_sessions']}  "
          f"max_depth={run['max_depth']}")
    print(f"sessions_with_compaction={run['sessions_with_compaction']}  "
          f"total_compactions={run['total_compactions']}  "
          f"root_compactions={run['root_compactions']}  root_lines={run['root_lines']}")
    print()
    print("(a) skill re-reads:")
    print(f"  sessions_with_reread={run['sessions_with_reread']}  "
          f"total_reread_events={run['total_reread_events']}")
    for s in run["sessions"]:
        if s["re_read_skill_paths"]:
            print(f"    {s['rollout']}: {s['re_read_skill_paths']}")
    print()
    print("(b) spawn hygiene pre/post first compaction (all sessions with a compaction):")
    h = run["spawn_hygiene"]
    print(f"  pre:  n={h['pre']['n']}  isolated={h['pre']['pct_isolated']}  "
          f"explicit_model={h['pre']['pct_explicit_model']}")
    print(f"  post: n={h['post']['n']}  isolated={h['post']['pct_isolated']}  "
          f"explicit_model={h['post']['pct_explicit_model']}")
    print()
    print(f"(c) depth-2 spawns by spawner role: {run['depth2_by_spawner_role']}")
    for d in run["depth2_details"]:
        print(f"    {d['spawner_rollout']} ({d['spawner_role']}, task={d['spawner_task_name']}) "
              f"-> {d['child_rollout']} (task={d['child_task_name']})")
    if run["duplicate_review_families"]:
        print(f"  same-task duplicate reviews: {len(run['duplicate_review_families'])}")
        for f in run["duplicate_review_families"]:
            print(f"    family={f['family']}  implementer={f['implementer_rollout']}  "
                  f"worker_review={f['worker_reviewer_rollouts']}  "
                  f"controller_review={f['controller_reviewer_rollouts']}")
    print()


def _rep_range_suffix(runs):
    """Identical convention to score_e1.py/score_e2.py's helper of the
    same name."""
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
    out_path = os.path.join(out_dir, f"e6-{label}.json")
    if os.path.exists(out_path) and not force:
        print(f"score_e6: refusing to overwrite existing {out_path} "
              f"-- set env FORCE=1 to overwrite", file=sys.stderr)
        return out_path, False
    with open(out_path, "w") as f:
        json.dump({"label": label, "runs": runs}, f, indent=2)
    return out_path, True


def main(argv):
    if len(argv) < 2:
        print("usage: score_e6.py RUNDIR...", file=sys.stderr)
        return 1

    runs = [score_run(rd) for rd in argv[1:]]

    print(f"# E6 compaction-recovery scorer output ({len(runs)} run(s))")
    print()
    for run in runs:
        print_run_report(run)

    print("## Aggregate across all given RUNDIRs")
    print()
    n_runs = len(runs)
    n_with_compaction = sum(1 for r in runs if r["sessions_with_compaction"] > 0)
    n_with_reread = sum(1 for r in runs if r["sessions_with_reread"] > 0)
    n_with_dup_review = sum(1 for r in runs if r["duplicate_review_families"])
    agg_depth2 = collections.Counter()
    for r in runs:
        agg_depth2.update(r["depth2_by_spawner_role"])
    print(f"reps scored={n_runs}  reps with >=1 compaction={n_with_compaction}/{n_runs}  "
          f"reps with >=1 skill re-read={n_with_reread}/{n_with_compaction or n_runs}  "
          f"reps with >=1 same-task duplicate review={n_with_dup_review}/{n_runs}")
    print(f"depth-2 spawns by spawner role, summed across reps: {dict(agg_depth2)}")
    print(f"total compactions across all reps: {sum(r['total_compactions'] for r in runs)} "
          f"(root-only: {sum(r['root_compactions'] for r in runs)})")
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
