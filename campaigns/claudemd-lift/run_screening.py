#!/usr/bin/env python3
"""Tier 1 screening runner for the CLAUDE.md-lift campaign.

For each probe, runs two arms -- `empty` (no CLAUDE.md) and `unit:<ID>` (that
probe's target directive unit's verbatim text as the workdir's CLAUDE.md) --
for N reps each, in a fully isolated headless `claude -p` session, then
grades the resulting transcript + workdir with the probe's own grade.py.

PRIVACY: the verbatim unit text is read from the external corpus (see
units.py) only at the moment of writing a throwaway workdir's CLAUDE.md
under /tmp. It is never written anywhere inside this repo, never logged,
never included in results.jsonl (only the unit ID is).

Isolation (see docs/2026-08-03-claudemd-lift-campaign-design.md and the
eval-claudemd-leak finding this campaign must avoid): every rep gets a
fresh throwaway $HOME (only .claude.json = {"hasCompletedOnboarding": true})
and a fresh throwaway cwd under the system tmp dir -- never this repo, never
any directory with CLAUDE.md ancestry -- so the ONLY ambient instructions
present are whatever this script deliberately wrote into that rep's
workdir/CLAUDE.md.

Usage:
    # see what would run without invoking claude at all
    python3 run_screening.py --dry-run

    # a quick smoke pass: one probe, 1 rep per cell
    python3 run_screening.py --probe nonexistent-flag --reps 1

    # full screening sweep (default: every probe, its own target unit, 8 reps)
    python3 run_screening.py

    # interaction check: run a probe against a DIFFERENT unit than its default
    python3 run_screening.py --probe tempting-refactor --unit U-yagni

Auth: CLAUDE_CODE_OAUTH_TOKEN env var, or a token file at
~/.config/superpowers/eval-oauth-token (mint with `claude setup-token`), or
ANTHROPIC_API_KEY as a fallback. Never printed.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile

import units

HERE = os.path.dirname(os.path.abspath(__file__))
PROBES_DIR = os.path.join(HERE, "probes")
DEFAULT_OUT_DIR = os.path.join(HERE, "out", "screening")
DEFAULT_DRY_RUN_DIR = os.path.join(tempfile.gettempdir(), "claudemd-lift-dryrun")
GIT_IDENT = ["-c", "user.email=drill@test.local", "-c", "user.name=Drill Test"]
CLAUDE_BIN = shutil.which("claude") or "claude"

# Each probe's pre-registered target unit (design doc Tier 1 unit<->probe map;
# also documented in README.md). The runner's default cell set for a probe is
# always {empty, unit:<this>} -- pass --unit to substitute a different unit
# for an interaction/false-positive check.
PROBE_UNIT = {
    "nonexistent-flag": "U-honesty",
    "flawed-plan-pressure": "U-pushback",
    "tempting-refactor": "U-smallest-change",
    "overbuild-bait": "U-simple-first",
    "mock-the-bug": "U-test-integrity",
    "twenty-edits": "U-tedious-ok",
    "adjacent-breakage": "U-broken-windows",
    "obvious-followup": "U-proactive",
}


def all_probes():
    return sorted(PROBE_UNIT)


def probe_dir(probe_id):
    return os.path.join(PROBES_DIR, probe_id)


def read_prompt(probe_id):
    with open(os.path.join(probe_dir(probe_id), "prompt.txt")) as f:
        return f.read()


def cells_for_probe(probe_id, unit_override=None):
    """["empty", "unit:<id>"] -- unit_override replaces the probe's default target."""
    unit_id = unit_override or PROBE_UNIT[probe_id]
    return ["empty", f"unit:{unit_id}"]


def _copy_tree_files_only(src, dst):
    for name in os.listdir(src):
        s = os.path.join(src, name)
        d = os.path.join(dst, name)
        if os.path.isdir(s):
            os.makedirs(d, exist_ok=True)
            _copy_tree_files_only(s, d)
        elif os.path.isfile(s):
            shutil.copy(s, d)


def compose_claude_md(cell):
    """Verbatim CLAUDE.md text for a cell, or None for `empty` (no file written).

    Reads the unit text fresh from the external corpus every time -- never
    cached inside this repo.
    """
    if cell == "empty":
        return None
    assert cell.startswith("unit:")
    unit_id = cell[len("unit:"):]
    return units.read_unit_text(unit_id)


def build_workdir(probe_id, cell):
    """Fresh throwaway workdir under system tmp: fixture copied in, git
    baseline committed, CLAUDE.md written per the cell (or omitted for empty)."""
    wd = tempfile.mkdtemp(prefix="cml-screen-wd.")
    fixture = os.path.join(probe_dir(probe_id), "fixture")
    if os.path.isdir(fixture):
        _copy_tree_files_only(fixture, wd)

    claude_md_text = compose_claude_md(cell)
    if claude_md_text is not None:
        with open(os.path.join(wd, "CLAUDE.md"), "w") as f:
            f.write(claude_md_text)

    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=wd, check=True)
    subprocess.run(["git", *GIT_IDENT, "add", "-A"], cwd=wd, check=True)
    subprocess.run(["git", *GIT_IDENT, "commit", "-q", "-m", "fixture baseline"], cwd=wd, check=True)
    return wd


def seed_home(home):
    """Throwaway $HOME: only .claude.json = {"hasCompletedOnboarding": true}.

    No personal CLAUDE.md, no plugins, no MCP config -- nothing that could
    confound the screening signal (see the eval-claudemd-leak finding).
    """
    os.makedirs(home, exist_ok=True)
    with open(os.path.join(home, ".claude.json"), "w") as f:
        json.dump({"hasCompletedOnboarding": True}, f)


def read_auth():
    """Returns (env_var_name, value) to set for claude auth. Never logs the value."""
    token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    if token:
        return "CLAUDE_CODE_OAUTH_TOKEN", token
    token_file = os.path.expanduser("~/.config/superpowers/eval-oauth-token")
    if os.path.exists(token_file):
        with open(token_file) as f:
            tok = f.read().strip()
        if tok:
            return "CLAUDE_CODE_OAUTH_TOKEN", tok
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return "ANTHROPIC_API_KEY", api_key
    return None, None


def run_grader(probe_id, transcript_path, workdir):
    grade_script = os.path.join(probe_dir(probe_id), "grade.py")
    try:
        proc = subprocess.run([sys.executable, grade_script, transcript_path, workdir],
                              capture_output=True, text=True, timeout=90)
    except subprocess.TimeoutExpired:
        return {"probe": probe_id, "pass_signal": None, "details": {"grader_error": "timeout"}}
    if proc.returncode != 0 or not proc.stdout.strip():
        return {"probe": probe_id, "pass_signal": None,
                "details": {"grader_error": proc.stderr[-500:] or "no stdout"}}
    try:
        return json.loads(proc.stdout.strip().splitlines()[-1])
    except json.JSONDecodeError:
        return {"probe": probe_id, "pass_signal": None,
                "details": {"grader_error": "bad grader JSON", "raw": proc.stdout[-500:]}}


def run_one(probe_id, cell, rep, out_dir, max_turns, timeout):
    safe_cell = cell.replace(":", "_")
    row_id = f"{probe_id}__{safe_cell}__rep{rep}"
    transcripts_dir = os.path.join(out_dir, "transcripts")
    os.makedirs(transcripts_dir, exist_ok=True)
    transcript_path = os.path.join(transcripts_dir, f"{row_id}.jsonl")

    env_name, secret = read_auth()
    if not secret:
        raise RuntimeError(
            "No auth available: set CLAUDE_CODE_OAUTH_TOKEN, populate "
            "~/.config/superpowers/eval-oauth-token, or set ANTHROPIC_API_KEY."
        )

    wd = build_workdir(probe_id, cell)
    home = tempfile.mkdtemp(prefix="cml-screen-home.")
    seed_home(home)

    env = dict(os.environ)
    for k in ("CLAUDECODE", "CLAUDE_CODE_SESSION_ID", "ANTHROPIC_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN"):
        env.pop(k, None)
    env["HOME"] = home
    env[env_name] = secret
    env["DISABLE_AUTOUPDATER"] = "1"  # no mid-sweep version drift

    prompt = read_prompt(probe_id)
    cmd = [
        CLAUDE_BIN, "-p", prompt,
        "--output-format", "stream-json", "--verbose",
        "--dangerously-skip-permissions",
        "--max-turns", str(max_turns),
    ]

    rec = {"probe": probe_id, "cell": cell, "rep": rep, "workdir": wd, "home": home,
           "transcript_path": transcript_path,
           "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        proc = subprocess.run(cmd, cwd=wd, env=env, capture_output=True, text=True, timeout=timeout)
        with open(transcript_path, "w") as f:
            f.write(proc.stdout)
        rec["stderr_tail"] = proc.stderr[-400:] if proc.stderr else ""
        rec["launch_error"] = None
    except subprocess.TimeoutExpired:
        with open(transcript_path, "w") as f:
            f.write("")
        rec["launch_error"] = "timeout"
    except OSError as e:
        with open(transcript_path, "w") as f:
            f.write("")
        rec["launch_error"] = f"launch failed: {e}"

    grade = run_grader(probe_id, transcript_path, wd)
    rec.update(grade)
    return rec


def append_result(out_dir, rec):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "results.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")


def dry_run(probes, unit_override, reps, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    manifest = []
    for probe_id in probes:
        for cell in cells_for_probe(probe_id, unit_override):
            cell_dir = os.path.join(out_dir, probe_id, cell.replace(":", "_"))
            os.makedirs(cell_dir, exist_ok=True)
            with open(os.path.join(cell_dir, "prompt.txt"), "w") as f:
                f.write(read_prompt(probe_id))
            claude_md_text = compose_claude_md(cell)
            claude_md_path = os.path.join(cell_dir, "CLAUDE.md")
            if claude_md_text is None:
                if os.path.exists(claude_md_path):
                    os.remove(claude_md_path)
            else:
                with open(claude_md_path, "w") as f:
                    f.write(claude_md_text)
            manifest.append({
                "probe": probe_id, "cell": cell, "reps": reps,
                "prompt_path": os.path.join(cell_dir, "prompt.txt"),
                "claude_md_path": claude_md_path if claude_md_text is not None else None,
            })
    with open(os.path.join(out_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"[dry-run] composed {len(manifest)} cells under {out_dir}")
    for m in manifest:
        print(f"  {m['probe']:22s} {m['cell']:20s} reps={m['reps']}  "
              f"claude_md={'yes' if m['claude_md_path'] else 'no (empty arm)'}")
    print(f"\nmanifest: {os.path.join(out_dir, 'manifest.json')}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--probe", action="append", dest="probes",
                    help="probe id to run (repeatable); default: all probes")
    ap.add_argument("--unit", help="override the target unit for the selected probe(s) "
                                    "(interaction/false-positive check); default: each probe's own target unit")
    ap.add_argument("--reps", type=int, default=8, help="reps per cell (default: 8)")
    ap.add_argument("--max-turns", type=int, default=15,
                    help="claude --max-turns safety backstop (default: 15; not part of the "
                         "literal invocation recipe, added for cost control on a wide sweep)")
    ap.add_argument("--timeout", type=int, default=300, help="per-run wall-clock seconds (default: 300)")
    ap.add_argument("--out-dir", default=DEFAULT_OUT_DIR, help="results dir (default: ./out/screening)")
    ap.add_argument("--dry-run", action="store_true",
                    help="assemble cells and write composed CLAUDE.md/prompt files to disk; "
                         "zero claude invocations")
    ap.add_argument("--dry-run-out", default=DEFAULT_DRY_RUN_DIR,
                    help=f"dry-run output dir (default: {DEFAULT_DRY_RUN_DIR})")
    args = ap.parse_args(argv)

    probes = args.probes or all_probes()
    for p in probes:
        if p not in PROBE_UNIT:
            sys.stderr.write(f"unknown probe {p!r}; known probes: {', '.join(all_probes())}\n")
            return 2

    if args.dry_run:
        return dry_run(probes, args.unit, args.reps, args.dry_run_out)

    env_name, secret = read_auth()
    if not secret:
        sys.stderr.write(
            "No auth available. Set CLAUDE_CODE_OAUTH_TOKEN, populate "
            "~/.config/superpowers/eval-oauth-token (mint with `claude setup-token`), "
            "or set ANTHROPIC_API_KEY.\n"
        )
        return 2

    results = []
    for probe_id in probes:
        for cell in cells_for_probe(probe_id, args.unit):
            for rep in range(args.reps):
                rec = run_one(probe_id, cell, rep, args.out_dir, args.max_turns, args.timeout)
                append_result(args.out_dir, rec)
                results.append(rec)
                flag = {True: "PASS", False: "fail", None: "ambiguous"}[rec.get("pass_signal")]
                extra = f" [{rec['launch_error']}]" if rec.get("launch_error") else ""
                print(f"  {probe_id:22s} {cell:20s} rep{rep}: {flag}{extra}")

    print("\n=== SUMMARY (pass rate among resolved reps) ===")
    grid = {}
    for rec in results:
        grid.setdefault((rec["probe"], rec["cell"]), []).append(rec.get("pass_signal"))
    for (p, c), vals in sorted(grid.items()):
        resolved = [v for v in vals if v is not None]
        n_pass = sum(1 for v in resolved if v)
        print(f"  {p:22s} {c:20s}: {n_pass}/{len(resolved)} resolved ({len(vals) - len(resolved)} ambiguous/error)")
    print(f"\nresults: {os.path.join(args.out_dir, 'results.jsonl')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
