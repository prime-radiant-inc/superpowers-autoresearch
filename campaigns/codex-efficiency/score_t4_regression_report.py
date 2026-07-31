#!/usr/bin/env python3
"""T4 layer-3 global regression battery aggregator/report (Task 11).

`score_t4_regression.py` (Task 10) is deliberately a library only --
`score_trajectory()`/`score_file()` compute one trajectory's ceremony
census and nothing else ("no CLI/report generation at this layer -- Task
11 aggregates census dicts across a battery and produces the report", per
its own module docstring). This script is that aggregator: it walks a set
of quorum `--out-root` RUNDIRs (one per rep, e.g.
`results/cx-eff-cc-ceremony-spike-fix-rep1`, each containing exactly one
run subdirectory with `verdict.json` + `trajectory.json`), groups them
into (arm, coding_agent, scenario_class) cells, and reports the
pre-registered T4 layer-3 criteria per cell.

Unlike score_e4.py/score_e1.py/etc (which parse codex's raw
`~/.codex/sessions/**/*.jsonl` rollout format), this reads quorum's own
`verdict.json` for the coding-agent identity, the Gauntlet-Agent verdict,
and cost -- and quorum's normalized `trajectory.json` for the ATIF
ceremony census via `score_t4_regression.score_file()`. This is what makes
it harness-neutral: the same code handles claude and gemini RUNDIRs
without a codex-specific rollout parser.

Each RUNDIR's parent directory name must match run-quorum.sh's own
`results/cx-eff-<SCENARIO>-<ARM>-repN` convention (`REP_DIR_RE` below,
identical regex to score_e1.py/score_e4.py/score_e6.py); ARM must be
exactly "dev" or "fix" (a trailing `-dev`/`-fix` suffix on the captured
`arm_scenario` group). SCENARIO must contain a `ceremony-{spike,bounded,
arch}` substring (`_scenario_key()`, same convention as score_e4.py's
`_scenario_key`).

Usage:
    score_t4_regression_report.py RUNDIR...

Prints a markdown report (per-run table, then a per-cell aggregate table)
to stdout, and writes a JSON blob of the same data to campaigns/
codex-efficiency/out/t4-layer3-<label>.json. Refuses to overwrite an
existing output file unless env FORCE=1 is set (same convention as
score_e1.py/score_e4.py/etc). Exits 0 on success, 1 on a usage error, a
malformed RUNDIR (missing/ambiguous run subdir, missing verdict.json), or
an existing-output-file collision without FORCE.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_t4_regression as scorer

REP_DIR_RE = re.compile(r"^cx-eff-(?P<arm_scenario>.+)-rep(?P<rep>\d+)$")

SCENARIO_CLASSES = ("spike", "bounded", "arch")


def _rundir_label(rundir):
    """Unlike score_e1.py/score_e4.py's `_parent_label` (which is handed
    the actual coding-agent run directory ONE LEVEL BELOW the
    `cx-eff-...-repN` battery dir, so it looks at ITS parent), this
    script's RUNDIR argument IS the `cx-eff-<scenario>-<arm>-repN`
    battery dir itself (the `--out-root` passed to `quorum run` by
    run-quorum.sh) -- the coding-agent run subdir lives inside it and is
    located separately by `_find_run_subdir()`. So match directly against
    this dir's own basename."""
    name = os.path.basename(os.path.abspath(rundir.rstrip("/")))
    m = REP_DIR_RE.match(name)
    if m:
        return m.group("arm_scenario"), int(m.group("rep"))
    raise SystemExit(
        f"score_t4_regression_report: RUNDIR basename {name!r} does not "
        f"match the expected 'cx-eff-<scenario>-<arm>-repN' convention")


def _scenario_key(arm_scenario):
    for key in SCENARIO_CLASSES:
        if f"ceremony-{key}" in arm_scenario:
            return key
    raise SystemExit(
        f"score_t4_regression_report: cannot determine ceremony scenario "
        f"class from arm_scenario label {arm_scenario!r} (expected one of "
        f"{SCENARIO_CLASSES} in a 'ceremony-<class>' substring)")


def _arm(arm_scenario, scenario_key):
    # arm_scenario is e.g. "cc-ceremony-spike-fix" -- strip the
    # "ceremony-<class>-" stem, leaving the trailing arm token.
    stem = f"ceremony-{scenario_key}-"
    idx = arm_scenario.find(stem)
    tail = arm_scenario[idx + len(stem):]
    if tail not in ("dev", "fix"):
        raise SystemExit(
            f"score_t4_regression_report: arm_scenario {arm_scenario!r} "
            f"does not end in a known ARM token ('dev'/'fix'); got tail "
            f"{tail!r}")
    return tail


def _find_run_subdir(rundir):
    """The single quorum run subdirectory living directly under a
    --out-root RUNDIR (verdict.json marks it)."""
    candidates = [
        d for d in sorted(glob.glob(os.path.join(rundir, "*")))
        if os.path.isdir(d) and os.path.exists(os.path.join(d, "verdict.json"))
    ]
    if len(candidates) == 0:
        raise SystemExit(
            f"score_t4_regression_report: no run subdir with verdict.json "
            f"under {rundir} -- incomplete/crashed rep, not scorable")
    if len(candidates) > 1:
        raise SystemExit(
            f"score_t4_regression_report: {len(candidates)} run subdirs "
            f"with verdict.json under {rundir} (ambiguous) -- {candidates}")
    return candidates[0]


def score_run(rundir):
    rundir = rundir.rstrip("/")
    arm_scenario, rep = _rundir_label(rundir)
    scenario_key = _scenario_key(arm_scenario)
    arm = _arm(arm_scenario, scenario_key)

    run_dir = _find_run_subdir(rundir)
    with open(os.path.join(run_dir, "verdict.json")) as f:
        verdict = json.load(f)

    traj_path = os.path.join(run_dir, "trajectory.json")
    if os.path.exists(traj_path):
        census = scorer.score_file(traj_path)
    else:
        census = None

    gauntlet = verdict.get("gauntlet") or {}
    economics = verdict.get("economics") or {}

    return {
        "rundir": rundir,
        "run_dir": run_dir,
        "arm_scenario": arm_scenario,
        "arm": arm,
        "rep": rep,
        "scenario_class": scenario_key,
        "scenario": verdict.get("scenario"),
        "coding_agent": verdict.get("coding_agent"),
        "credential": verdict.get("credential"),
        "final": verdict.get("final"),
        "final_reason": verdict.get("final_reason"),
        "gauntlet_status": gauntlet.get("status"),
        "total_est_cost_usd": economics.get("total_est_cost_usd"),
        "partial": economics.get("partial"),
        "census": census,
    }


def _mean(values):
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    return sum(vals) / len(vals)


def cell_key(run):
    return (run["arm"], run["coding_agent"], run["scenario_class"])


def summarize_cell(runs):
    n = len(runs)
    gauntlet_pass = sum(1 for r in runs if r["gauntlet_status"] == "pass")
    final_pass = sum(1 for r in runs if r["final"] == "pass")
    censuses = [r["census"] for r in runs if r["census"] is not None]
    writing_plans = [c["writing_plans_invoked"] for c in censuses]
    return {
        "n": n,
        "n_scored": len(censuses),
        "gauntlet_pass": gauntlet_pass,
        "gauntlet_pass_rate": gauntlet_pass / n if n else None,
        "final_pass": final_pass,
        "final_pass_rate": final_pass / n if n else None,
        "mean_spec_docs_written": _mean([c["spec_docs_written"] for c in censuses]),
        "mean_plan_docs_written": _mean([c["plan_docs_written"] for c in censuses]),
        "mean_doc_writes_before_first_code": _mean(
            [c["doc_writes_before_first_code"] for c in censuses]),
        "writing_plans_invoked_count": sum(1 for w in writing_plans if w),
        "writing_plans_invoked_n": len(writing_plans),
        "mean_user_turns_before_first_code": _mean(
            [c["user_turns_before_first_code"] for c in censuses]),
        "total_est_cost_usd": sum(
            r["total_est_cost_usd"] for r in runs if r["total_est_cost_usd"] is not None),
    }


def _fmt(v, digits=2):
    return "N/A" if v is None else f"{v:.{digits}f}"


def print_run_table(runs):
    print("| arm | agent | class | rep | gauntlet | final | spec docs | plan docs | "
          "docs-before-code | writing-plans | cost ($) |")
    print("|---|---|---|---:|---|---|---:|---:|---:|---|---:|")
    for r in sorted(runs, key=lambda x: (x["arm"], x["coding_agent"], x["scenario_class"], x["rep"] or 0)):
        c = r["census"] or {}
        print(
            f"| {r['arm']} | {r['coding_agent']} | {r['scenario_class']} | {r['rep']} | "
            f"{r['gauntlet_status']} | {r['final']} | "
            f"{c.get('spec_docs_written', 'N/A')} | {c.get('plan_docs_written', 'N/A')} | "
            f"{c.get('doc_writes_before_first_code', 'N/A')} | "
            f"{c.get('writing_plans_invoked', 'N/A')} | "
            f"{_fmt(r['total_est_cost_usd'])} |")
    print()


def print_cell_summary_table(cell_summaries):
    print("| arm | agent | class | n | gauntlet pass | spec docs (mean) | "
          "plan docs (mean) | writing-plans invoked | cost ($) |")
    print("|---|---|---|---:|---|---:|---:|---|---:|")
    for key in sorted(cell_summaries):
        arm, agent, cls = key
        s = cell_summaries[key]
        print(
            f"| {arm} | {agent} | {cls} | {s['n']} | "
            f"{s['gauntlet_pass']}/{s['n']} | "
            f"{_fmt(s['mean_spec_docs_written'])} | "
            f"{_fmt(s['mean_plan_docs_written'])} | "
            f"{s['writing_plans_invoked_count']}/{s['writing_plans_invoked_n']} | "
            f"{_fmt(s['total_est_cost_usd'])} |")
    print()


def _rep_range_suffix(runs):
    """Identical convention to score_e1.py/score_e4.py's helper of the
    same name."""
    reps = sorted({r["rep"] for r in runs if r["rep"] is not None})
    if not reps:
        return "unknown-reps"
    if len(reps) == 1:
        return f"rep{reps[0]}"
    return f"rep{reps[0]}-{reps[-1]}"


def _out_label(runs):
    arms = sorted({r["arm"] for r in runs})
    agents = sorted({r["coding_agent"] for r in runs})
    return f"{'-'.join(arms)}-{'-'.join(agents)}-{_rep_range_suffix(runs)}"


def write_output(runs, cell_summaries, out_dir, force=False):
    label = _out_label(runs)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"t4-layer3-{label}.json")
    if os.path.exists(out_path) and not force:
        print(f"score_t4_regression_report: refusing to overwrite existing "
              f"{out_path} -- set env FORCE=1 to overwrite", file=sys.stderr)
        return out_path, False
    serializable_cells = {
        "|".join(k): v for k, v in cell_summaries.items()
    }
    with open(out_path, "w") as f:
        json.dump({"label": label, "cell_summaries": serializable_cells,
                    "runs": runs}, f, indent=2)
    return out_path, True


def main(argv):
    if len(argv) < 2:
        print("usage: score_t4_regression_report.py RUNDIR...", file=sys.stderr)
        return 1

    runs = [score_run(rd) for rd in argv[1:]]

    print(f"# T4 layer-3 global regression battery report ({len(runs)} run(s))")
    print()
    print_run_table(runs)

    cells = {}
    for r in runs:
        cells.setdefault(cell_key(r), []).append(r)
    cell_summaries = {k: summarize_cell(v) for k, v in cells.items()}

    print_cell_summary_table(cell_summaries)

    total_cost = sum(r["total_est_cost_usd"] for r in runs if r["total_est_cost_usd"] is not None)
    print(f"Total measured cost: ${total_cost:.2f}")
    print()

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    force = os.environ.get("FORCE") == "1"
    out_path, wrote = write_output(runs, cell_summaries, out_dir, force=force)
    if wrote:
        print(f"Wrote {out_path}")
    else:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
