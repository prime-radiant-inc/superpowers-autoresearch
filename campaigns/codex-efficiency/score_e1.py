#!/usr/bin/env python3
"""E1 fork-hygiene scorer (Task 6).

For each RUNDIR (a single quorum run's coding-agent directory, i.e. the
directory containing `home/.codex/sessions/**` and `verdict.json` -- one
level below a `results/cx-eff-<scenario>-<arm>-repN/` battery dir), this
walks every rollout file in the run's session tree, extracts every
`spawn_agent` call from every rollout (a spawned child can itself spawn --
"controller" isn't necessarily only the root), and resolves each spawn's
child rollout via `child_links()` (event_id == spawn call_id -> child
thread id) matched against rollout filenames (`rollout-<ts>-<uuid>.jsonl`).

For each spawn tuple we record the raw fork-hygiene fields (fork_turns,
model, reasoning_effort, task_name -- task_name is fixture-derived, safe to
commit) plus, when the child rollout resolves, the child's byte size and
`parse_session()` metrics (first_instruction_line, skill_reads_strict,
task_complete). No message/instruction text is ever extracted or printed --
extract_spawns()'s Spawn tuple has no such field to begin with.

Usage:
    score_e1.py RUNDIR...

Prints a markdown report (per-run spawn-tuple table + summary, then an
aggregate summary across all given RUNDIRs) to stdout, and writes a JSON
blob of the same raw tuples to
campaigns/codex-efficiency/out/e1-<label>.json (label auto-derived from the
RUNDIRs' parent directory names PLUS the actual rep numbers scored, e.g.
"cx-sdd-small-dev-rep5-8" for results/cx-eff-cx-sdd-small-dev-rep{5..8}/<run>
-- the rep-range suffix exists so a REP_START-extended re-score of a
different rep range under the same arm_scenario lands in a different file
instead of silently colliding with an earlier score). Refuses to overwrite
an existing output file unless env FORCE=1 is set (prints an error naming
the collision and exits 1 instead). Exits 0 on success, 1 on usage error,
an existing-output-file collision without FORCE, or a run with zero
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


def find_rollouts(rundir):
    pattern = os.path.join(rundir, "home", ".codex", "sessions", "**", "*.jsonl")
    return sorted(glob.glob(pattern, recursive=True))


def _parent_label(rundir):
    """Derive (arm_scenario_label, rep_number) from the battery dir name one
    level above RUNDIR, e.g. .../cx-eff-cx-sdd-small-dev-rep2/<run> ->
    ("cx-sdd-small-dev", 2). Falls back to the raw parent name / None rep
    if the naming convention (run-quorum.sh's --out-root) isn't matched."""
    parent = os.path.basename(os.path.dirname(os.path.abspath(rundir.rstrip("/"))))
    m = REP_DIR_RE.match(parent)
    if m:
        return m.group("arm_scenario"), int(m.group("rep"))
    return parent, None


def score_run(rundir):
    rundir = rundir.rstrip("/")
    arm_scenario, rep = _parent_label(rundir)
    rollouts = find_rollouts(rundir)
    if not rollouts:
        raise SystemExit(f"score_e1: no rollout files found under {rundir}/home/.codex/sessions/**")
    root = rollouts[0]  # earliest by filename == chronological (rollout-<ts>-<uuid>.jsonl)
    rollout_basenames = [os.path.basename(p) for p in rollouts]

    spawns_out = []
    for path in rollouts:
        spawns = rp.extract_spawns(path)
        if not spawns:
            continue
        links = rp.child_links(path)
        for s in spawns:
            thread_id = links.get(s.call_id)
            child_path = None
            if thread_id:
                for cand in rollouts:
                    if thread_id in os.path.basename(cand):
                        child_path = cand
                        break
            rec = {
                "parent_rollout": os.path.basename(path),
                "call_id": s.call_id,
                "task_name": s.task_name,
                "fork_turns": s.fork_turns,
                "model": s.model,
                "reasoning_effort": s.reasoning_effort,
                "spawn_timestamp": s.timestamp,
                "child_thread_id": thread_id,
                "child_rollout": os.path.basename(child_path) if child_path else None,
                "child_bytes": None,
                "child_first_instruction_line": None,
                "child_skill_reads_strict": None,
                "child_task_complete": None,
            }
            if child_path:
                cm = rp.parse_session(child_path)
                rec["child_bytes"] = os.path.getsize(child_path)
                rec["child_first_instruction_line"] = cm.first_instruction_line
                rec["child_skill_reads_strict"] = cm.skill_reads_strict
                rec["child_task_complete"] = cm.task_complete
            spawns_out.append(rec)

    linked_children = {r["child_rollout"] for r in spawns_out if r["child_rollout"]}
    orphan_rollouts = [
        b for b in rollout_basenames if b != os.path.basename(root) and b not in linked_children
    ]

    return {
        "rundir": rundir,
        "arm_scenario": arm_scenario,
        "rep": rep,
        "root_rollout": os.path.basename(root),
        "rollout_count": len(rollouts),
        "orphan_rollouts": orphan_rollouts,
        "spawns": spawns_out,
    }


def _is_numeric_partial(fork_turns):
    return fork_turns.isdigit()


def summarize(spawns):
    n = len(spawns)
    if n == 0:
        return {
            "n_spawns": 0, "n_isolated": 0, "pct_isolated": 0.0,
            "n_explicit_model": 0, "pct_explicit_model": 0.0,
            "n_model_omitted": 0, "pct_model_omitted": 0.0,
            "n_fork_all": 0, "pct_fork_all": 0.0,
            "n_fork_all_or_partial": 0, "pct_fork_all_or_partial": 0.0,
            "n_child_resolved": 0, "pct_child_resolved": 0.0,
            "n_child_task_complete": 0, "pct_child_task_complete": 0.0,
        }
    isolated = sum(1 for s in spawns if s["fork_turns"] == "none")
    explicit_model = sum(1 for s in spawns if s["model"] != rp.OMIT)
    fork_all = sum(1 for s in spawns if s["fork_turns"] == "all")
    fork_all_or_partial = sum(
        1 for s in spawns if s["fork_turns"] == "all" or _is_numeric_partial(s["fork_turns"]))
    child_resolved = sum(1 for s in spawns if s["child_rollout"])
    child_task_complete = sum(
        1 for s in spawns if s["child_rollout"] and (s["child_task_complete"] or 0) >= 1)
    return {
        "n_spawns": n,
        "n_isolated": isolated, "pct_isolated": isolated / n * 100,
        "n_explicit_model": explicit_model, "pct_explicit_model": explicit_model / n * 100,
        "n_model_omitted": n - explicit_model, "pct_model_omitted": (n - explicit_model) / n * 100,
        "n_fork_all": fork_all, "pct_fork_all": fork_all / n * 100,
        "n_fork_all_or_partial": fork_all_or_partial, "pct_fork_all_or_partial": fork_all_or_partial / n * 100,
        "n_child_resolved": child_resolved, "pct_child_resolved": child_resolved / n * 100,
        "n_child_task_complete": child_task_complete,
        "pct_child_task_complete": (child_task_complete / child_resolved * 100) if child_resolved else 0.0,
    }


def _fmt_pct(v):
    return f"{v:.1f}%"


def print_run_table(run):
    label = f"{run['arm_scenario']} rep{run['rep']}" if run["rep"] is not None else run["arm_scenario"]
    print(f"### {label} -- `{run['rundir']}`")
    print()
    print(f"root rollout: `{run['root_rollout']}` ({run['rollout_count']} rollout files total)")
    if run["orphan_rollouts"]:
        print(f"orphan rollouts (not root, not linked as any spawn's child): {run['orphan_rollouts']}")
    print()
    print("| call_id | task_name | fork_turns | model | reasoning_effort | child_bytes | child_first_instruction_line | child_skill_reads_strict | child_task_complete |")
    print("|---|---|---|---|---|---|---|---|---|")
    for s in run["spawns"]:
        print(
            f"| {s['call_id']} | {s['task_name']} | {s['fork_turns']} | {s['model']} | "
            f"{s['reasoning_effort']} | {s['child_bytes']} | {s['child_first_instruction_line']} | "
            f"{s['child_skill_reads_strict']} | {s['child_task_complete']} |")
    print()
    summ = summarize(run["spawns"])
    print(
        f"spawns={summ['n_spawns']}  isolated(fork_turns==none)={summ['n_isolated']} "
        f"({_fmt_pct(summ['pct_isolated'])})  explicit_model={summ['n_explicit_model']} "
        f"({_fmt_pct(summ['pct_explicit_model'])})  fork_all={summ['n_fork_all']} "
        f"({_fmt_pct(summ['pct_fork_all'])})  fork_all_or_partial={summ['n_fork_all_or_partial']} "
        f"({_fmt_pct(summ['pct_fork_all_or_partial'])})  model_omitted={summ['n_model_omitted']} "
        f"({_fmt_pct(summ['pct_model_omitted'])})")
    print(
        f"child rollouts resolved={summ['n_child_resolved']} ({_fmt_pct(summ['pct_child_resolved'])} of spawns)  "
        f"child task_complete present={summ['n_child_task_complete']} "
        f"({_fmt_pct(summ['pct_child_task_complete'])} of resolved children)")
    print()
    return summ


def _rep_range_suffix(runs):
    """Derive a rep-range suffix ('rep5-8', or 'rep5' for a single rep)
    from the reps actually scored -- so a REP_START-extended re-score of a
    different rep range under the same arm_scenario doesn't collide with
    an earlier score's output file. Falls back to 'unknown-reps' if no run
    in the batch matched the rep-dir naming convention (rep is None)."""
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


def write_output(runs, agg, out_dir, force=False):
    """Write the aggregate JSON blob for `runs` to out_dir/e1-<label>.json,
    where <label> encodes both the arm_scenario and the actual rep range
    scored (see _out_label). Refuses to overwrite an existing file unless
    `force` is set, printing an error naming the collision instead.
    Returns (out_path, wrote: bool)."""
    label = _out_label(runs)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"e1-{label}.json")
    if os.path.exists(out_path) and not force:
        print(f"score_e1: refusing to overwrite existing {out_path} "
              f"-- set env FORCE=1 to overwrite", file=sys.stderr)
        return out_path, False
    with open(out_path, "w") as f:
        json.dump({"label": label, "aggregate": agg, "runs": runs}, f, indent=2)
    return out_path, True


def main(argv):
    if len(argv) < 2:
        print("usage: score_e1.py RUNDIR...", file=sys.stderr)
        return 1

    runs = [score_run(rd) for rd in argv[1:]]

    print(f"# E1 fork-hygiene scorer output ({len(runs)} run(s))")
    print()
    all_spawns = []
    for run in runs:
        print_run_table(run)
        all_spawns.extend(run["spawns"])

    print("## Aggregate across all given RUNDIRs")
    print()
    agg = summarize(all_spawns)
    print(
        f"total spawns={agg['n_spawns']}  isolated={agg['n_isolated']} ({_fmt_pct(agg['pct_isolated'])})  "
        f"explicit_model={agg['n_explicit_model']} ({_fmt_pct(agg['pct_explicit_model'])})  "
        f"fork_all={agg['n_fork_all']} ({_fmt_pct(agg['pct_fork_all'])})  "
        f"fork_all_or_partial={agg['n_fork_all_or_partial']} ({_fmt_pct(agg['pct_fork_all_or_partial'])})  "
        f"model_omitted={agg['n_model_omitted']} ({_fmt_pct(agg['pct_model_omitted'])})")
    print(
        f"child rollouts resolved={agg['n_child_resolved']} ({_fmt_pct(agg['pct_child_resolved'])})  "
        f"child task_complete present={agg['n_child_task_complete']} "
        f"({_fmt_pct(agg['pct_child_task_complete'])} of resolved children)")
    print()

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    force = os.environ.get("FORCE") == "1"
    out_path, wrote = write_output(runs, agg, out_dir, force=force)
    if not wrote:
        return 1
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
