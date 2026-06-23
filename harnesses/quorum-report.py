#!/usr/bin/env python3
"""Aggregate the quorum/gauntlet re-test matrix (results/matrix-<variant>-rep<r>/).

Reads each run's verdict.json (the FAITHFUL tmux/gauntlet verdict) and scans each
trajectory.json for plan-mode tool use (EnterPlanMode/ExitPlanMode) — the signal
the headless -p harness could not capture. Prints variant × scenario × model:
quorum pass-rate + plan-mode incidence. Read-only.

Usage: python3 harnesses/quorum-report.py
"""
import glob
import json
import os
import re
import sys
from collections import defaultdict

EVALS = "/Users/jesse/git/superpowers/superpowers/evals"
# Out-root prefix to aggregate: matrix-* (step-1 candidates) by default, or e.g.
# `abl` for the step-2 Q-variant ablation (results/abl-<variant>-rep<r>/).
PREFIX = sys.argv[1] if len(sys.argv) > 1 else "matrix"
MATRIX = glob.glob(os.path.join(EVALS, "results", f"{PREFIX}-*"))

SCEN_ORDER = [
    "superpowers-bootstrap",
    "brainstorming-resists-jump-to-implementation",
    "brainstorming-companion-just-in-time",
    "triggering-systematic-debugging",
    "triggering-dispatching-parallel-agents",
    "triggering-executing-plans",
    "triggering-finishing-a-development-branch",
    "triggering-requesting-code-review",
    "triggering-test-driven-development",
    "triggering-writing-plans",
    "mid-conversation-skill-invocation",
    "cost-checkbox-over-trigger",
    "subagent-dispatch-no-overtrigger",
]
# Preferred column order + display labels for the Claude matrices; any other
# coding-agent (codex, gemini, …) in the data is appended alphabetically and
# labeled by its own name. MODEL_ORDER is resolved against the data below so the
# same report renders both the Claude matrices and the cross-harness runs.
MODEL_PREF = ["claude", "claude-sonnet", "claude-haiku"]
MODEL_LABEL = {"claude": "opus", "claude-sonnet": "sonnet", "claude-haiku": "haiku"}


def variant_of(matrix_dir):
    # <prefix>-<variant>-rep<r>
    base = os.path.basename(matrix_dir)
    return re.sub(rf"^{re.escape(PREFIX)}-(.*)-rep\d+$", r"\1", base)


PLAN_TOOLS = {"EnterPlanMode", "ExitPlanMode"}


def _tool_use_names(obj):
    """Yield every tool_use block's name found anywhere in a transcript record."""
    if isinstance(obj, dict):
        if obj.get("type") == "tool_use" and isinstance(obj.get("name"), str):
            yield obj["name"]
        for v in obj.values():
            yield from _tool_use_names(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from _tool_use_names(item)


def plan_mode_in(run_dir):
    """True iff the coding-agent-under-test invoked a plan-mode tool.

    The authoritative, complete tool-call record is the coding agent's own
    session transcript (home/.claude/projects/<slug>/<uuid>.jsonl), NOT
    trajectory.json — whose steps don't carry structured tool names. Returns
    None when no transcript is present (so it's excluded, not counted as 0)."""
    transcripts = glob.glob(
        os.path.join(run_dir, "home", ".claude", "projects", "*", "*.jsonl")
    )
    if not transcripts:
        return None
    for tx in transcripts:
        try:
            with open(tx) as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if any(n in PLAN_TOOLS for n in _tool_use_names(rec)):
                        return True
        except OSError:
            continue
    return False


# (variant, scenario, model) -> {"pass":[], "plan":[]}
data = defaultdict(lambda: {"pass": [], "plan": []})
indeterminate = []
for mdir in MATRIX:
    variant = variant_of(mdir)
    for vj in glob.glob(os.path.join(mdir, "*", "verdict.json")):
        run_dir = os.path.dirname(vj)
        try:
            v = json.load(open(vj))
        except (OSError, json.JSONDecodeError):
            continue
        scen = v.get("scenario", "?")
        model = v.get("coding_agent", "?")
        final = v.get("final")
        key = (variant, scen, model)
        if final == "pass":
            data[key]["pass"].append(1)
        elif final == "fail":
            data[key]["pass"].append(0)
        else:
            indeterminate.append((variant, scen, model, final, v.get("final_reason", "")[:60]))
            data[key]["pass"].append(0)  # count indeterminate as non-pass but flag below
        pm = plan_mode_in(run_dir)
        if pm is not None:
            data[key]["plan"].append(1 if pm else 0)

variants = sorted({k[0] for k in data}, key=lambda n: (n != "baseline", n))
# Resolve the agent columns from the data: preferred Claude order first, then any
# other coding-agent (codex/gemini/…) alphabetically. Lets one report render both
# the Claude matrices and the cross-harness runs.
present_models = {k[2] for k in data}
MODEL_ORDER = [m for m in MODEL_PREF if m in present_models] + sorted(
    present_models - set(MODEL_PREF)
)
print("QUORUM/GAUNTLET RE-TEST MATRIX (faithful tmux) — pass-rate [plan-mode count]\n")
OVER_TRIGGER_NOTE = {
    "cost-checkbox-over-trigger": "  (over-trigger: pass = brainstorming NOT fired)",
    "subagent-dispatch-no-overtrigger": "  (Q4: pass = subagent dispatched AND did NOT over-trigger brainstorming)",
    "brainstorming-resists-jump-to-implementation": "  (HARD: pass = brainstorming FIRED on the design-worthy request)",
    "brainstorming-companion-just-in-time": "  (pass = brainstorming fired on the design request)",
}
# Only print scenarios that actually have data, so the table fits the run set.
present_scens = {k[1] for k in data}
for scen in [s for s in SCEN_ORDER if s in present_scens]:
    note = OVER_TRIGGER_NOTE.get(scen, "")
    print(f"### {scen}{note}")
    print("  " + f"{'variant':16s} " + " ".join(f"{MODEL_LABEL.get(m, m):>14s}" for m in MODEL_ORDER))
    for variant in variants:
        cells = []
        for m in MODEL_ORDER:
            d = data.get((variant, scen, m))
            if not d or not d["pass"]:
                cells.append("—")
            else:
                p = sum(d["pass"]); n = len(d["pass"]); pm = sum(d["plan"])
                cells.append(f"{p}/{n} [pm{pm}]")
        print("  " + f"{variant:16s} " + " ".join(f"{c:>14s}" for c in cells))
    print()

if indeterminate:
    print("INDETERMINATE runs (investigate):")
    for v, s, m, f, r in indeterminate[:20]:
        print(f"  {v} {s} {m}: {f} — {r}")

# overall plan-mode summary
total_plan = sum(sum(d["plan"]) for d in data.values())
total_runs = sum(len(d["plan"]) for d in data.values())
print(f"\nplan-mode tool use across all runs with trajectories: {total_plan}/{total_runs}")
