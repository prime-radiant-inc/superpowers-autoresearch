#!/usr/bin/env python3
"""E4 proportional-ceremony scorer (Task 11).

For each RUNDIR (a single quorum run's coding-agent directory, i.e. the
directory containing `home/.codex/sessions/**` and `verdict.json` -- one
level below a `results/cx-eff-<scenario>-<arm>-repN/` battery dir), this
walks the run's rollout tree TRANSITIVELY (root + descendants via
`extract_spawns()`/`child_links()`, the same convention `score_e2.py`
already uses) and computes a ceremony census: how much happens before the
FIRST real code change.

**"First non-doc patch"** = the chronologically earliest `patch_apply_end`
event (any rollout anywhere in the tree, via the new
`rollout_parser.patch_applies()`) with `success:true` whose changed paths
include at least one path that is neither under a `docs/` directory (any
path component literally named `docs`) nor a `*.md` file (case-insensitive
suffix) -- i.e. the earliest point any REAL code file changed, as opposed
to a plan/spec/report markdown artifact (which, under SDD, commonly lands
under `.superpowers/sdd/**/*.md` well before any code). The tree-wide
(not root-only) search matters: a controller that plans first and
dispatches an implementer child produces the actual code change in a
DIFFERENT rollout than the root's own.

Census fields, computed against that global timestamp T (see the module
docstring in `logs/2026-07-28-codex-efficiency.md`'s E4 pre-registration
entry for the full rationale of each field):

  - user_turns_before_first_non_doc_patch  -- `user_message` count in the
    ROOT rollout ONLY, before T. Deliberately root-only: this measures
    ceremony from the human/Gauntlet's side (the initial ask plus any
    clarifying-question round trips), not a spawned child's own internal
    dispatch message (which also arrives as a `user_message` in the
    child's own rollout, per E1's prior finding, but isn't a "turn" the
    human sat through).
  - docs_written_before_first_non_doc_patch -- count of DISTINCT doc paths
    (under `docs/` or `*.md`) added by any successful `patch_apply_end`
    anywhere in the tree, before T. If the run never produces a non-doc
    patch (T is None -- see below), this counts doc paths across the
    WHOLE tree instead (no cutoff), since there is no T to cut off at.
  - tool_calls_before_first_non_doc_patch -- count of
    `rollout_parser.TOOL_CALL_TYPES` response_items across every rollout
    in the tree, timestamped before T. This is the scorer's PRIMARY,
    discrimination-gated metric (see the pre-registration entry).
  - wall_clock_seconds_to_first_non_doc_patch -- T minus the root
    rollout's very first record timestamp (session start).

**A run may never produce a non-doc patch at all** (T is None) -- a real
possibility for the spike class specifically ("find out, quick and dirty
is fine" could resolve as pure investigation, no code). When T is None,
the three T-gated fields above are all None/N/A (reported honestly, not
imputed); `no_non_doc_patch` is True and callers must exclude that rep
from any T-gated mean, per the pre-registration.

`score_run()` also asserts the chronologically-earliest rollout (root) is
genuinely the session that received the fixed Gauntlet task text for its
scenario class (a known substring per class, matched case-insensitively
against ONLY the root's first `user_message` -- never printed raw, same
precedent as `score_e2.py`'s `_root_matches_review_request`) and raises
SystemExit if that assertion fails.

No message/instruction text is ever printed by this scorer -- only
booleans (marker match), counts, timestamps, and file paths (both process
artifacts: fixture-derived, safe to commit per this campaign's established
precedent).

Usage:
    score_e4.py RUNDIR...

Prints a markdown report (per-run census, then a per-class aggregate table
and the spike-vs-arch discrimination-gate verdict) to stdout, and writes a
JSON blob of the same data to campaigns/codex-efficiency/out/
e4-<label>.json (label convention identical to score_e1.py/score_e2.py).
Refuses to overwrite an existing output file unless env FORCE=1 is set.
Exits 0 on success, 1 on usage error or an existing-output-file collision
without FORCE.
"""
import datetime
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rollout_parser as rp

REP_DIR_RE = re.compile(r"^cx-eff-(?P<arm_scenario>.+)-rep(?P<rep>\d+)$")

# Known substring (lower-case) of each scenario class's fixed Gauntlet
# task text (scenarios/cx-ceremony-{spike,bounded,arch}/story.md), used
# ONLY to assert root identity -- the raw text itself is never printed.
TASK_MARKERS = {
    "spike": "port is already in use before binding",
    "bounded": "suppresses request logging",
    "arch": "reusable library + thin cli",
}


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


def _scenario_key(arm_scenario):
    for key in TASK_MARKERS:
        if f"ceremony-{key}" in arm_scenario:
            return key
    raise SystemExit(
        f"score_e4: cannot determine ceremony scenario class from "
        f"arm_scenario label {arm_scenario!r} (expected one of "
        f"{sorted(TASK_MARKERS)} in a 'ceremony-<class>' substring)")


def _first_user_message_text(path):
    """Read the first event_msg/user_message payload's `message` string.
    Used only by the root-identity check below -- the raw text this
    returns is never printed by score_run(), only whether a known marker
    substring is found in it."""
    for _ts, typ, p in rp.iter_records(path):
        if typ == "event_msg" and p.get("type") == "user_message":
            msg = p.get("message")
            return msg if isinstance(msg, str) else ""
    return ""


def _root_matches_task(root_path, scenario_key):
    marker = TASK_MARKERS[scenario_key]
    return marker.lower() in _first_user_message_text(root_path).lower()


def _resolve_child_path(thread_id, rollouts):
    for cand in rollouts:
        if thread_id in os.path.basename(cand):
            return cand
    return None


def build_tree(root, rollouts):
    """BFS from `root` via resolved spawn -> child links (identical
    convention to score_e2.py's build_tree). Returns a list of node dicts:
    rollout (path), depth, is_root."""
    nodes = []
    visited = set()
    frontier = [(root, 0)]
    while frontier:
        path, depth = frontier.pop(0)
        key = os.path.basename(path)
        if key in visited:
            continue
        visited.add(key)
        nodes.append({"path": path, "rollout": key, "depth": depth, "is_root": path == root})
        spawns = rp.extract_spawns(path)
        links = rp.child_links(path)
        for s in spawns:
            thread_id = links.get(s.call_id)
            if not thread_id:
                continue
            child_path = _resolve_child_path(thread_id, rollouts)
            if child_path and os.path.basename(child_path) not in visited:
                frontier.append((child_path, depth + 1))
    return nodes


def is_doc_path(path):
    """True iff `path` is a documentation artifact: any path component
    literally named `docs`, or a `.md` file (case-insensitive suffix)."""
    norm = path.replace("\\", "/")
    if norm.lower().endswith(".md"):
        return True
    parts = norm.split("/")
    return "docs" in parts[:-1]


def _patch_is_non_doc(patch):
    return patch.success and any(not is_doc_path(p) for p in patch.paths)


def _first_record_timestamp(path):
    for ts, _typ, _p in rp.iter_records(path):
        return ts
    return None


def _user_message_timestamps(path):
    return [ts for ts, typ, p in rp.iter_records(path)
            if typ == "event_msg" and p.get("type") == "user_message"]


def _tool_call_timestamps(path):
    return [ts for ts, typ, p in rp.iter_records(path)
            if typ == "response_item" and p.get("type") in rp.TOOL_CALL_TYPES]


def _parse_iso(ts):
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.datetime.fromisoformat(ts)


def _iso_delta_seconds(ts_start, ts_end):
    return (_parse_iso(ts_end) - _parse_iso(ts_start)).total_seconds()


def score_run(rundir):
    rundir = rundir.rstrip("/")
    arm_scenario, rep = _parent_label(rundir)
    scenario_key = _scenario_key(arm_scenario)
    rollouts = find_rollouts(rundir)
    if not rollouts:
        raise SystemExit(f"score_e4: no rollout files found under {rundir}/home/.codex/sessions/**")
    root = rollouts[0]  # earliest by filename == chronological

    root_matches_task = _root_matches_task(root, scenario_key)
    if not root_matches_task:
        raise SystemExit(
            f"score_e4: root-identity assertion FAILED for {rundir} -- the "
            f"chronologically-earliest rollout ({os.path.basename(root)}) "
            f"does not contain the {scenario_key!r}-class task marker in "
            f"its first instruction. Refusing to score a tree built on the "
            f"wrong root.")

    nodes = build_tree(root, rollouts)
    tree_paths = {n["rollout"]: n["path"] for n in nodes}
    orphan_rollouts = sorted(
        os.path.basename(p) for p in rollouts if os.path.basename(p) not in tree_paths)

    # Every patch_apply_end across the whole tree, oldest first.
    all_patches = []
    for n in nodes:
        all_patches.extend(rp.patch_applies(n["path"]))
    all_patches.sort(key=lambda a: a.timestamp)

    first_non_doc = next((a for a in all_patches if _patch_is_non_doc(a)), None)
    T = first_non_doc.timestamp if first_non_doc else None

    session_start = _first_record_timestamp(root)

    doc_paths = set()
    for a in all_patches:
        if not a.success:
            continue
        if T is not None and a.timestamp >= T:
            continue
        for p in a.paths:
            if is_doc_path(p):
                doc_paths.add(p)

    if T is not None:
        user_turns = sum(1 for ts in _user_message_timestamps(root) if ts < T)
        tool_calls = sum(
            1 for n in nodes for ts in _tool_call_timestamps(n["path"]) if ts < T)
        wall_clock = _iso_delta_seconds(session_start, T) if session_start else None
    else:
        user_turns = None
        tool_calls = None
        wall_clock = None

    return {
        "rundir": rundir,
        "arm_scenario": arm_scenario,
        "rep": rep,
        "scenario_class": scenario_key,
        "root_rollout": os.path.basename(root),
        "root_matches_task": root_matches_task,
        "tree_size": len(nodes),
        "orphan_rollouts": orphan_rollouts,
        "no_non_doc_patch": T is None,
        "first_non_doc_patch_timestamp": T,
        "first_non_doc_patch_paths": first_non_doc.paths if first_non_doc else None,
        "user_turns_before_first_non_doc_patch": user_turns,
        "docs_written_before_first_non_doc_patch": len(doc_paths),
        "doc_paths_written_before_first_non_doc_patch": sorted(doc_paths),
        "tool_calls_before_first_non_doc_patch": tool_calls,
        "wall_clock_seconds_to_first_non_doc_patch": wall_clock,
    }


def _mean(values):
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    return sum(vals) / len(vals)


def summarize_class(runs):
    return {
        "n": len(runs),
        "n_no_non_doc_patch": sum(1 for r in runs if r["no_non_doc_patch"]),
        "mean_user_turns": _mean([r["user_turns_before_first_non_doc_patch"] for r in runs]),
        "mean_docs_written": _mean([r["docs_written_before_first_non_doc_patch"] for r in runs]),
        "mean_tool_calls": _mean([r["tool_calls_before_first_non_doc_patch"] for r in runs]),
        "mean_wall_clock_seconds": _mean([r["wall_clock_seconds_to_first_non_doc_patch"] for r in runs]),
    }


def discrimination_gate(spike_summary, arch_summary):
    """Primary, pre-registered gate: spike-class mean tool-calls-before-T
    within 25% of arch-class mean tool-calls-before-T (see the E4
    pre-registration log entry for why tool-calls was chosen as the
    gated metric over the other three census fields)."""
    spike_v = spike_summary["mean_tool_calls"]
    arch_v = arch_summary["mean_tool_calls"]
    if spike_v is None or arch_v is None or arch_v == 0:
        return {
            "verdict": "inconclusive-by-zero (no comparable tool-call mean on one or both classes)",
            "ratio": None, "within_25pct": None,
            "spike_mean_tool_calls": spike_v, "arch_mean_tool_calls": arch_v,
        }
    within_25pct = abs(spike_v - arch_v) <= 0.25 * arch_v
    verdict = (
        "ceremony NOT proportional to task complexity (predicted pathology CONFIRMED)"
        if within_25pct else
        "ceremony scales with task complexity (inconclusive-by-zero for the predicted pathology)"
    )
    return {
        "verdict": verdict,
        "ratio": spike_v / arch_v,
        "within_25pct": within_25pct,
        "spike_mean_tool_calls": spike_v,
        "arch_mean_tool_calls": arch_v,
    }


def _fmt(v, digits=1):
    return "N/A" if v is None else f"{v:.{digits}f}"


def print_run_table(runs):
    print("| class | rep | rundir | no-patch | user turns | docs written | tool calls | wall-clock (s) |")
    print("|---|---:|---|---|---:|---:|---:|---:|")
    for r in sorted(runs, key=lambda x: (x["scenario_class"], x["rep"] or 0)):
        print(
            f"| {r['scenario_class']} | {r['rep']} | `{r['rundir']}` | "
            f"{'YES' if r['no_non_doc_patch'] else 'no'} | "
            f"{_fmt(r['user_turns_before_first_non_doc_patch'], 0)} | "
            f"{r['docs_written_before_first_non_doc_patch']} | "
            f"{_fmt(r['tool_calls_before_first_non_doc_patch'], 0)} | "
            f"{_fmt(r['wall_clock_seconds_to_first_non_doc_patch'], 0)} |")
    print()


def print_class_summary_table(class_summaries):
    print("| class | n | no-patch reps | mean user turns | mean docs written | mean tool calls | mean wall-clock (s) |")
    print("|---|---:|---:|---:|---:|---:|---:|")
    for key in ("spike", "bounded", "arch"):
        if key not in class_summaries:
            continue
        s = class_summaries[key]
        print(
            f"| {key} | {s['n']} | {s['n_no_non_doc_patch']} | "
            f"{_fmt(s['mean_user_turns'])} | {_fmt(s['mean_docs_written'])} | "
            f"{_fmt(s['mean_tool_calls'])} | {_fmt(s['mean_wall_clock_seconds'])} |")
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


def write_output(runs, class_summaries, gate, out_dir, force=False):
    label = _out_label(runs)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"e4-{label}.json")
    if os.path.exists(out_path) and not force:
        print(f"score_e4: refusing to overwrite existing {out_path} "
              f"-- set env FORCE=1 to overwrite", file=sys.stderr)
        return out_path, False
    with open(out_path, "w") as f:
        json.dump({"label": label, "class_summaries": class_summaries,
                    "discrimination_gate": gate, "runs": runs}, f, indent=2)
    return out_path, True


def main(argv):
    if len(argv) < 2:
        print("usage: score_e4.py RUNDIR...", file=sys.stderr)
        return 1

    runs = [score_run(rd) for rd in argv[1:]]

    print(f"# E4 proportional-ceremony scorer output ({len(runs)} run(s))")
    print()
    print_run_table(runs)

    class_summaries = {}
    for key in ("spike", "bounded", "arch"):
        class_runs = [r for r in runs if r["scenario_class"] == key]
        if class_runs:
            class_summaries[key] = summarize_class(class_runs)

    print("## Per-class summary")
    print()
    print_class_summary_table(class_summaries)

    gate = None
    if "spike" in class_summaries and "arch" in class_summaries:
        gate = discrimination_gate(class_summaries["spike"], class_summaries["arch"])
        print("## Discrimination gate (spike vs. arch, mean tool calls before first non-doc patch)")
        print()
        print(f"spike mean={_fmt(gate['spike_mean_tool_calls'])}  "
              f"arch mean={_fmt(gate['arch_mean_tool_calls'])}  "
              f"ratio={_fmt(gate['ratio'], 2) if gate['ratio'] is not None else 'N/A'}  "
              f"within_25pct={gate['within_25pct']}")
        print()
        print(f"**Verdict: {gate['verdict']}**")
        print()

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    force = os.environ.get("FORCE") == "1"
    out_path, wrote = write_output(runs, class_summaries, gate, out_dir, force=force)
    if not wrote:
        return 1
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
