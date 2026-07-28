#!/usr/bin/env python3
"""MICRO: does DELIVERY POSITION (not wording) decide whether codex follows
read-economy guidance?

Holds the wording fixed (the proven imperative) and varies only WHERE the
guidance is delivered, to test the "why don't the rules fire" hypothesis:
- D0-control     : no guidance.
- D1-inprompt    : guidance at top of the task prompt (proven to work).
- D2-pointer     : guidance lives in a ./codex-tools.md file; prompt only POINTS
                   to it (replicates superpowers' real delivery — SKILL.md names
                   references/codex-tools.md but doesn't inject its content).
- D3-injected    : guidance wrapped in <EXTREMELY_IMPORTANT>…</EXTREMELY_IMPORTANT>
                   prepended to the prompt (mimics the session-start-codex hook's
                   additionalContext format).

Prediction: D1 and D3 fire (whole-file cat); D2 (pointer) does NOT — same as the
real superpowers run. If so, the core fix is to INJECT the guidance into the
high-salience channel (SKILL.md / session-start) rather than reference it.

BASE codex, single-turn `codex exec`, read-only, real 331-line fixture. n=REPS
(default 5), cached per (variant,rep). Score hand-verifiable from out/.
"""
import json, os, pathlib, shutil, subprocess, sys

EVALS = "/Users/jesse/git/superpowers/superpowers/evals"
MICRO = pathlib.Path(EVALS, "results/.read-micro")
MICRO_C = "/workspace/evals/results/.read-micro"
FIXTURE_SRC = MICRO / "fixture/economics.ts"
OUT = MICRO / "out-delivery"; OUT.mkdir(parents=True, exist_ok=True)
HOST_CODEX = pathlib.Path(os.path.expanduser("~/.codex"))
REPS = int(os.environ.get("REPS", "5"))

WORDING = (
    "To read a file, ALWAYS run `cat <file>` to load the entire file in ONE "
    "command. NEVER read a file using multiple `sed -n`/`head`/`tail` ranges. "
    "You have no file-reading tool; reads go through the shell and each is a "
    "separate model turn."
)
TASK = (
    "Read the file economics.ts in the current directory and write a concise "
    "one-line summary of what EACH exported function and interface does. You "
    "need the full contents of the file."
)

# (prompt_text, extra_workdir_file or None)
DELIVERIES = {
    "D0-control":  (TASK, None),
    "D1-inprompt": (WORDING + "\n\n" + TASK, None),
    "D2-pointer":  ("A tool reference for this environment is at "
                    "./codex-tools.md — consult it.\n\n" + TASK,
                    ("codex-tools.md", "# Codex tool reference\n\n" + WORDING + "\n")),
    "D3-injected": ("<EXTREMELY_IMPORTANT>\n" + WORDING + "\n</EXTREMELY_IMPORTANT>\n\n" + TASK, None),
    # Q: can a STRONG injected compulsion to read+obey the referenced guide beat
    # the weak pointer (D2)? This mimics strengthening the using-superpowers
    # SKILL.md pointer instead of injecting codex-tools.md's content.
    "D4-strong-pointer": (
        "<EXTREMELY_IMPORTANT>\nBefore you run ANY shell command in this session, "
        "you MUST first read ./codex-tools.md in full and then follow every rule "
        "in it exactly. Those rules are binding and apply to every command you "
        "run.\n</EXTREMELY_IMPORTANT>\n\n" + TASK,
        ("codex-tools.md", "# Codex tool reference\n\n" + WORDING + "\n")),
}


def run_sample(name, prompt, extra, rep):
    tag = f"{name}-r{rep}"
    dst = OUT / f"{tag}.jsonl"
    if dst.exists():
        print("cached", tag); return
    home = MICRO / "homes-d" / tag / ".codex"
    work = MICRO / "work-d" / tag
    for d in (home, work):
        d.mkdir(parents=True, exist_ok=True)
    shutil.copy(HOST_CODEX / "auth.json", home / "auth.json")
    if (HOST_CODEX / "config.toml").exists():
        shutil.copy(HOST_CODEX / "config.toml", home / "config.toml")
    shutil.copy(FIXTURE_SRC, work / "economics.ts")
    if extra:
        (work / extra[0]).write_text(extra[1])
    (work / "prompt.txt").write_text(prompt)
    home_c = f"{MICRO_C}/homes-d/{tag}/.codex"
    work_c = f"{MICRO_C}/work-d/{tag}"
    # NOTE: read-only sandbox uses bwrap, which fails ("No permissions to create
    # a new namespace") in some container instances. The task only reads files, so
    # bypass the sandbox to avoid that flakiness — read STYLE (cat vs sed) is
    # independent of sandbox enforcement.
    cmd = (f'export CODEX_HOME={home_c}; cd {work_c}; '
           f'codex exec "$(cat prompt.txt)" '
           f'--dangerously-bypass-approvals-and-sandbox '
           f'--skip-git-repo-check --output-last-message answer.txt')
    print("running", tag, "...", flush=True)
    subprocess.run(["scripts/evals-container", "exec", "bash", "-lc", cmd],
                   cwd=EVALS, capture_output=True, text=True, timeout=600)
    rolls = list((MICRO / "homes-d" / tag / ".codex").glob("sessions/**/rollout-*.jsonl"))
    if not rolls:
        print("  NO ROLLOUT for", tag); return
    shutil.copy(max(rolls, key=lambda p: p.stat().st_mtime), dst)


def commands(roll):
    for line in open(roll):
        if not any(k in line for k in ('"function_call"', '"local_shell_call"', '"custom_tool_call"')):
            continue
        try: r = json.loads(line)
        except Exception: continue
        p = r.get("payload") or r.get("item") or {}
        a = p.get("arguments")
        if isinstance(a, str):
            try: a = json.loads(a)
            except Exception: a = {}
        if isinstance(a, dict):
            c = a.get("cmd") or a.get("command")
            if isinstance(c, list): c = " ".join(map(str, c))
            if c: yield str(c)
        act = p.get("action") or {}
        if isinstance(act.get("command"), list):
            yield " ".join(map(str, act["command"]))


def score(roll):
    full_cat = chunk = 0
    for c in commands(roll):
        if "economics.ts" not in c: continue
        is_chunk = ("sed -n" in c) or ("head " in c) or ("tail " in c)
        if is_chunk: chunk += 1
        elif "cat " in c: full_cat += 1
    return full_cat, chunk


def main():
    for name, (prompt, extra) in DELIVERIES.items():
        for rep in range(REPS):
            run_sample(name, prompt, extra, rep)
    print("\n=== DELIVERY-POSITION SCORES (wording fixed; fixture economics.ts) ===")
    print(f"{'delivery':<14}{'reps':>5}{'chunk/run':>11}{'cat/run':>9}{'one-cat%':>10}")
    for name in DELIVERIES:
        rows = [score(OUT / f"{name}-r{r}.jsonl") for r in range(REPS)
                if (OUT / f"{name}-r{r}.jsonl").exists()]
        if not rows: print(f"{name:<14}  (no samples)"); continue
        n = len(rows)
        ch = sum(c for _, c in rows) / n
        ca = sum(f for f, _ in rows) / n
        onecat = sum(1 for f, c in rows if f >= 1 and c == 0) / n * 100
        print(f"{name:<14}{n:>5}{ch:>11.1f}{ca:>9.1f}{onecat:>9.0f}%")


if __name__ == "__main__":
    main()
