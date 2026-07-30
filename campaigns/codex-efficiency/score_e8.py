#!/usr/bin/env python3
"""E8 close_agent hygiene census (Amendment 1, Tasks E7-E9 -- MINE tier, no
new run spend). Pre-registered prediction:
`logs/2026-07-28-codex-efficiency.md`, "E8 PRE-REGISTRATION" entry.

Scores the same three corpora E7 used, with the same discovery/selection
code (deliberately reused rather than re-derived, so the audit's "direct
human gpt-5.6-sol" proxy population can't silently drift between the two
scorers):

  (a) Drew Ritter's external SDD head-to-head corpus (read-only, never
      committed -- reuses drew_adapter.py's RUNS/discover() for layout,
      exactly as score_e7.py does).
  (b) The 2026-07-28 audit corpus: E7's known 1,058-wait Remux root plus
      E7's documented proxy sample for "direct human gpt-5.6-sol task"
      roots -- reuses score_e7.py's own `_load_manifest`,
      `_resolve_manifest_path`, `_direct_human_sol_candidates`,
      `HIGH_WAIT_ROOT_ID` directly (imported, not copied) rather than
      re-deriving the same selection logic a second time.
  (c) Our own `cx-eff-cx-sdd-small-{dev,spinout}-rep*` battery runs (Tasks
      6/6b) -- reuses score_e1.py's find_rollouts(), exactly as
      score_e7.py does.

Per session: spawn count (`rollout_parser.extract_spawns()`), close_agent
count (`rollout_parser.lifecycle_calls()`, filtered to name=="close_agent"),
closure rate (close/spawn -- our own scorer's raw within-session call-count
convention, chosen to match Drew's own sessions.json `tool_calls` semantics
exactly, so the two are directly comparable), plus
interrupt_agent/followup_task/resume_agent/list_agents counts for context.
A session counts as a "controller" iff it has >=1 spawn (extract_spawns()).

No message/instruction/report text is ever read or printed by this script.
This matters more here than it did for E7: a close_agent
`function_call_output` carries `{"previous_status": {"completed": "<the
child's full final message/report>"}}` -- verified directly against a real
audit rollout during this task's build -- so unlike E7's wait_agent outputs
(a short, content-free status envelope), close_agent's outputs are NOT safe
to read or print. This script never calls the parser's output-reading code
path for close_agent at all; the manual-inspection section below lists only
each call's call_id/name/timestamp/args_task_name (all sourced from
lifecycle_calls(), which reads arguments, never outputs).

Usage: score_e8.py [--force]
Prints a markdown report to stdout. Writes aggregates-only JSON blobs to
campaigns/codex-efficiency/out/e8-<corpus>.json (refuses to overwrite an
existing file unless --force or env FORCE=1 is set, matching score_e1.py's
convention). Read-only otherwise.
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rollout_parser as rp
import drew_adapter as da
import score_e1 as e1
import score_e7 as e7

AUDIT_DIR = os.environ.get("AUDIT_DIR", e7.AUDIT_DIR)
EVALS_RESULTS = os.environ.get("EVALS_RESULTS", e7.EVALS_RESULTS)

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


# --- per-session census -----------------------------------------------

def census_session(path, label=""):
    spawns = rp.extract_spawns(path)
    lifecycle = rp.lifecycle_calls(path)
    n_spawns = len(spawns)
    is_controller = n_spawns > 0

    by_name = {name: [c for c in lifecycle if c.name == name]
               for name in sorted(rp.LIFECYCLE_NAMES)}
    n_close = len(by_name["close_agent"])
    closure_rate = (n_close / n_spawns) if n_spawns else None

    return {
        "path": path,
        "label": label,
        "n_spawns": n_spawns,
        "is_controller": is_controller,
        "n_close_agent": n_close,
        "closure_rate": closure_rate,
        "n_interrupt_agent": len(by_name["interrupt_agent"]),
        "n_followup_task": len(by_name["followup_task"]),
        "n_resume_agent": len(by_name["resume_agent"]),
        "n_list_agents": len(by_name["list_agents"]),
        # kept for the manual-inspection sampler; stripped before JSON dump
        "close_calls": by_name["close_agent"],
    }


def aggregate(sessions):
    controllers = [s for s in sessions if s["is_controller"]]
    total_spawns = sum(s["n_spawns"] for s in controllers)
    total_close = sum(s["n_close_agent"] for s in controllers)
    n_controllers_any_close = sum(1 for s in controllers if s["n_close_agent"] > 0)
    n_controllers_fully_closed = sum(
        1 for s in controllers if s["n_close_agent"] >= s["n_spawns"])
    # close_agent/interrupt_agent/etc. issued by a NON-controller session
    # (n_spawns == 0) would be unusual but not impossible (e.g. closing a
    # sibling/grandchild agent id) -- report separately rather than assume
    # it can't happen.
    non_controller_close = sum(
        s["n_close_agent"] for s in sessions if not s["is_controller"])
    return {
        "n_sessions": len(sessions),
        "n_controllers": len(controllers),
        "total_spawns": total_spawns,
        "total_close_agent": total_close,
        "closure_rate": (total_close / total_spawns) if total_spawns else None,
        "n_controllers_with_any_close": n_controllers_any_close,
        "n_controllers_fully_closed": n_controllers_fully_closed,
        "non_controller_close_agent_calls": non_controller_close,
        "total_interrupt_agent": sum(s["n_interrupt_agent"] for s in sessions),
        "total_followup_task": sum(s["n_followup_task"] for s in sessions),
        "total_resume_agent": sum(s["n_resume_agent"] for s in sessions),
        "total_list_agents": sum(s["n_list_agents"] for s in sessions),
    }


def _strip_for_json(sessions):
    return [{k: v for k, v in s.items() if k != "close_calls"} for s in sessions]


# --- corpus (a): Drew's external head-to-head corpus --------------------

def score_drew(corpus_root=None):
    corpus_root = corpus_root or da.DEFAULT_CORPUS_ROOT
    groups = {}
    for label, rel_dir in da.RUNS.items():
        run_dir = os.path.join(corpus_root, rel_dir)
        paths = da.discover(run_dir)
        if not paths:
            continue
        sessions = [census_session(p, label=label) for p in paths]
        groups[label] = sessions
    return groups


# --- corpus (b): audit corpus -- reuses score_e7's own selection code ---

def score_audit():
    manifest = e7._load_manifest()
    high_wait_path = e7._resolve_manifest_path(e7.HIGH_WAIT_ROOT_ID, manifest)
    if not high_wait_path or not os.path.exists(high_wait_path):
        raise SystemExit(f"score_e8: could not resolve high-wait root "
                          f"{e7.HIGH_WAIT_ROOT_ID} via session-manifest.json")
    high_wait_session = census_session(high_wait_path, label="audit-high-wait-root")

    candidates, pool_size = e7._direct_human_sol_candidates(
        AUDIT_DIR, {e7.HIGH_WAIT_ROOT_ID})
    direct_sessions = [
        census_session(c["rollout_path"], label="audit-direct-human-sol")
        for c in candidates
    ]
    return {
        "high_wait_root": [high_wait_session],
        "direct_human_sol_sample": direct_sessions,
        "direct_human_sol_pool_size": pool_size,
    }


# --- corpus (c): our own battery runs -----------------------------------

def score_battery(results_dir=None):
    results_dir = results_dir or EVALS_RESULTS
    groups = {}
    for arm in ("dev", "spinout"):
        rep_dirs = sorted(glob.glob(os.path.join(results_dir, f"cx-eff-cx-sdd-small-{arm}-rep*")))
        sessions = []
        for rep_dir in rep_dirs:
            rundirs = sorted(glob.glob(os.path.join(rep_dir, "*")))
            for rundir in rundirs:
                if not os.path.isdir(rundir):
                    continue
                rollouts = e1.find_rollouts(rundir)
                for path in rollouts:
                    sessions.append(census_session(path, label=f"battery-{arm}"))
        groups[arm] = sessions
    return groups


# --- manual-inspection listing -------------------------------------------

def list_all_close_calls(all_sessions):
    """Every close_agent call found across every scored session --
    call_id/name/timestamp/args_task_name only (all sourced from
    lifecycle_calls(), which reads only `arguments`, never
    `function_call_output` -- see module docstring for why close_agent's
    outputs specifically must never be read here)."""
    out = []
    for s in all_sessions:
        for c in s["close_calls"]:
            out.append({
                "label": s["label"],
                "call_id": c.call_id,
                "timestamp": c.timestamp,
                "args_task_name": c.args_task_name,
            })
    return out


# --- report printing ------------------------------------------------------

def _fmt_pct(v):
    return f"{v * 100:.1f}%" if v is not None else "n/a"


def print_group_line(name, sessions):
    agg = aggregate(sessions)
    print(f"- **{name}**: {agg['n_sessions']} session(s) scored, "
          f"{agg['n_controllers']} controller(s) (>=1 spawn). "
          f"spawns={agg['total_spawns']} close_agent={agg['total_close_agent']} "
          f"(closure_rate={_fmt_pct(agg['closure_rate'])}). "
          f"controllers with >=1 close={agg['n_controllers_with_any_close']}/{agg['n_controllers']}, "
          f"fully-closed controllers={agg['n_controllers_fully_closed']}/{agg['n_controllers']}. "
          f"non-controller close_agent calls={agg['non_controller_close_agent_calls']}. "
          f"context: interrupt_agent={agg['total_interrupt_agent']} "
          f"followup_task={agg['total_followup_task']} "
          f"resume_agent={agg['total_resume_agent']} "
          f"list_agents={agg['total_list_agents']}")
    return agg


def print_controller_table(name, sessions):
    controllers = [s for s in sessions if s["is_controller"]]
    if not controllers:
        return
    print(f"  controllers in {name}:")
    print("  | session | spawns | close_agent | closure_rate | interrupt | followup | resume | list |")
    print("  |---|---|---|---|---|---|---|---|")
    for s in controllers:
        print(f"  | {os.path.basename(s['path'])} | {s['n_spawns']} | "
              f"{s['n_close_agent']} | {_fmt_pct(s['closure_rate'])} | "
              f"{s['n_interrupt_agent']} | {s['n_followup_task']} | "
              f"{s['n_resume_agent']} | {s['n_list_agents']} |")
    print()


def main(argv):
    force = "--force" in argv or os.environ.get("FORCE") == "1"

    print("# E8 close_agent hygiene census (Amendment 1, MINE tier)")
    print()

    all_sessions = []

    print("## Corpus (a): Drew Ritter's external SDD head-to-head corpus")
    print()
    drew_groups = score_drew()
    for label, sessions in drew_groups.items():
        print_group_line(label, sessions)
        print_controller_table(label, sessions)
        all_sessions.extend(sessions)
    print()

    print("## Corpus (b): 2026-07-28 audit corpus")
    print()
    audit = score_audit()
    print_group_line("high-wait Remux root (E7's Finding 7 root)", audit["high_wait_root"])
    print_controller_table("high-wait root", audit["high_wait_root"])
    all_sessions.extend(audit["high_wait_root"])
    print(f"- direct-human-gpt-5.6-sol proxy pool: {audit['direct_human_sol_pool_size']} "
          f"candidate roots (depth 0, thread_source=user, model=gpt-5.6-sol, "
          f"root-family size <= 20; same selection as E7's "
          f"`_direct_human_sol_candidates()`, reused directly), of which "
          f"{len(audit['direct_human_sol_sample'])} have any wait_agent "
          f"activity (E7's own wait-activity pre-filter)")
    if audit["direct_human_sol_sample"]:
        print_group_line("direct-human-sol sample (wait-active subset)", audit["direct_human_sol_sample"])
        print_controller_table("direct-human-sol sample", audit["direct_human_sol_sample"])
        all_sessions.extend(audit["direct_human_sol_sample"])
    print()

    print("## Corpus (c): our own cx-eff-cx-sdd-small battery runs (Tasks 6/6b)")
    print()
    battery = score_battery()
    for arm, sessions in battery.items():
        print_group_line(f"battery-{arm}", sessions)
        print_controller_table(f"battery-{arm}", sessions)
        all_sessions.extend(sessions)
    print()

    close_calls = list_all_close_calls(all_sessions)
    print(f"## Manual inspection: every close_agent call found (n={len(close_calls)}, "
          f"call_id/timestamp/args_task_name only -- see module docstring for "
          f"why close_agent's function_call_output is never read here)")
    print()
    if not close_calls:
        print("(none found in any scored corpus)")
    for i, c in enumerate(close_calls, 1):
        print(f"{i}. [{c['label']}] call_id={c['call_id']} "
              f"timestamp={c['timestamp']} args_task_name={c['args_task_name']!r}")
    print()

    os.makedirs(OUT_DIR, exist_ok=True)
    wrote_all = True
    for corpus_name, groups in (
        ("drew", drew_groups),
        ("audit-high-wait-root", {"high_wait_root": audit["high_wait_root"]}),
        ("audit-direct-sol", {"direct_human_sol_sample": audit["direct_human_sol_sample"]}),
        ("battery", battery),
    ):
        blob = {name: {"aggregate": aggregate(sessions), "sessions": _strip_for_json(sessions)}
                for name, sessions in groups.items()}
        out_path = os.path.join(OUT_DIR, f"e8-{corpus_name}.json")
        if os.path.exists(out_path) and not force:
            print(f"score_e8: refusing to overwrite existing {out_path} "
                  f"-- set env FORCE=1 or pass --force to overwrite", file=sys.stderr)
            wrote_all = False
            continue
        with open(out_path, "w") as f:
            json.dump(blob, f, indent=2)
        print(f"wrote {out_path}", file=sys.stderr)

    return 0 if wrote_all else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
