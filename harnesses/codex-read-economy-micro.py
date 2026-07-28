#!/usr/bin/env python3
"""MICRO: does guidance wording make codex read a whole file in one `cat`
instead of chunked `sed -n` ranges?

Runs BASE codex (no superpowers plugin — the only variable is the injected
guidance) via single-turn `codex exec` inside the evals container, on a
read-heavy task over a real ~330-line fixture file. Measures, per sample, how
codex read the fixture: one whole `cat` vs chunked `sed/head/tail` ranges.

Method tier: MICRO. ~$0.05-0.30 per codex exec (subscription auth). Control
(no guidance) always included. REPS reps per variant; cached per (variant,rep).

Env: REPS (default 5). Run from anywhere; paths are absolute.
Reads host codex auth from ~/.codex; orchestrates via scripts/evals-container.
"""
import json, os, pathlib, shutil, subprocess, sys, collections

EVALS = "/Users/jesse/git/superpowers/superpowers/evals"
MICRO = pathlib.Path(EVALS, "results/.read-micro")          # host path (container-mounted)
MICRO_C = "/workspace/evals/results/.read-micro"            # same dir inside container
FIXTURE_SRC = MICRO / "fixture/economics.ts"
OUT = MICRO / "out"; OUT.mkdir(parents=True, exist_ok=True)
HOST_CODEX = pathlib.Path(os.path.expanduser("~/.codex"))
REPS = int(os.environ.get("REPS", "5"))

TASK = (
    "Read the file economics.ts in the current directory and write a concise "
    "one-line summary of what EACH exported function and interface does. You "
    "need the full contents of the file to summarize every export accurately."
)

VARIANTS = {
    "V0-control": "",
    "V1-plain": (
        "Note: you have no file-reading tool; file reads go through the shell. "
        "Read a whole small file in one `cat <file>` rather than several "
        "`sed -n` ranges.\n\n"
    ),
    "V2-cost": (
        "IMPORTANT: every shell command is a separate, expensive model turn. "
        "Reading a file in N ranged `sed -n` calls costs N turns; one "
        "`cat <file>` costs one turn. Always read a whole file with a single "
        "`cat`.\n\n"
    ),
    "V3-imperative": (
        "Tool rule: to read a file, ALWAYS run `cat <file>` to load the entire "
        "file in ONE command. NEVER read a file using multiple "
        "`sed -n`/`head`/`tail` ranges.\n\n"
    ),
}


def run_sample(vname, prompt, rep):
    tag = f"{vname}-r{rep}"
    dst = OUT / f"{tag}.jsonl"
    if dst.exists():
        print("cached", tag); return
    home = MICRO / "homes" / tag / ".codex"
    work = MICRO / "work" / tag
    for d in (home, work):
        d.mkdir(parents=True, exist_ok=True)
    shutil.copy(HOST_CODEX / "auth.json", home / "auth.json")
    if (HOST_CODEX / "config.toml").exists():
        shutil.copy(HOST_CODEX / "config.toml", home / "config.toml")
    shutil.copy(FIXTURE_SRC, work / "economics.ts")
    (work / "prompt.txt").write_text(prompt + TASK)
    home_c = f"{MICRO_C}/homes/{tag}/.codex"
    work_c = f"{MICRO_C}/work/{tag}"
    cmd = (
        f'export CODEX_HOME={home_c}; cd {work_c}; '
        f'codex exec "$(cat prompt.txt)" --sandbox read-only '
        f'--skip-git-repo-check --output-last-message answer.txt'
    )
    print("running", tag, "...", flush=True)
    subprocess.run(["scripts/evals-container", "exec", "bash", "-lc", cmd],
                   cwd=EVALS, capture_output=True, text=True, timeout=600)
    rolls = list((MICRO / "homes" / tag / ".codex").glob("sessions/**/rollout-*.jsonl"))
    if not rolls:
        print("  NO ROLLOUT for", tag); return
    shutil.copy(max(rolls, key=lambda p: p.stat().st_mtime), dst)


def commands(roll):
    """Yield shell command strings from a codex rollout."""
    for line in open(roll):
        if '"function_call"' not in line and '"local_shell_call"' not in line and '"custom_tool_call"' not in line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        p = r.get("payload") or r.get("item") or {}
        args = p.get("arguments")
        if isinstance(args, str):
            try: args = json.loads(args)
            except Exception: args = {}
        if isinstance(args, dict):
            c = args.get("cmd") or args.get("command")
            if isinstance(c, list): c = " ".join(map(str, c))
            if c: yield str(c)
        act = p.get("action") or {}
        c2 = act.get("command")
        if isinstance(c2, list): yield " ".join(map(str, c2))


def score(roll):
    full_cat = chunk = total = 0
    for c in commands(roll):
        if "economics.ts" not in c: continue
        is_chunk = ("sed -n" in c) or ("head " in c) or ("tail " in c)
        is_cat = ("cat " in c) and not is_chunk
        if is_chunk: chunk += 1; total += 1
        elif is_cat: full_cat += 1; total += 1
        elif "wc -l" in c or "grep" in c: pass  # peeking, not a content read
    return dict(total=total, full_cat=full_cat, chunk=chunk)


def main():
    if not FIXTURE_SRC.exists():
        sys.exit(f"fixture missing: {FIXTURE_SRC}")
    for vname, g in VARIANTS.items():
        for rep in range(REPS):
            run_sample(vname, g, rep)
    print("\n=== READ-STYLE SCORES (fixture: economics.ts) ===")
    print(f"{'variant':<16}{'reps':>5}{'reads/run':>11}{'chunk/run':>11}{'cat/run':>9}{'one-cat%':>10}")
    for vname in VARIANTS:
        rows = [score(OUT / f"{vname}-r{r}.jsonl") for r in range(REPS)
                if (OUT / f"{vname}-r{r}.jsonl").exists()]
        if not rows: print(f"{vname:<16}  (no samples)"); continue
        n = len(rows)
        tot = sum(x["total"] for x in rows) / n
        ch = sum(x["chunk"] for x in rows) / n
        ca = sum(x["full_cat"] for x in rows) / n
        onecat = sum(1 for x in rows if x["full_cat"] >= 1 and x["chunk"] == 0) / n * 100
        print(f"{vname:<16}{n:>5}{tot:>11.1f}{ch:>11.1f}{ca:>9.1f}{onecat:>9.0f}%")


if __name__ == "__main__":
    main()
