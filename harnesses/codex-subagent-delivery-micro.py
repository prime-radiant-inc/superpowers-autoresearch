#!/usr/bin/env python3
"""MICRO: how do we get codex SUBAGENTS to follow read-economy guidance?

Subagents get no SessionStart injection — their whole context is the spawn prompt
(the implementer/reviewer template). In the sdd-tiny scenario, a read-economy note
placed MID-prompt in implementer-prompt.md did NOT reduce subagent chunking. The
delivery micro showed top-of-prompt guidance works (D1=100%). So the question is
SALIENCE-WITHIN-THE-SPAWN-PROMPT: does the guidance need to be at the TOP?

This proxies a spawned subagent with a single-turn `codex exec` whose prompt IS a
realistic long subagent prompt (the spawn prompt is exactly the subagent's initial
context). Vary only WHERE the read guidance sits:
- SUB0-control : long subagent prompt, no read guidance.
- SUB1-buried  : guidance mid-prompt (≈ the implementer-prompt.md note that failed).
- SUB2-top     : guidance as the first line of the prompt.
- SUB3-wrap    : guidance in <EXTREMELY_IMPORTANT> at the very top.

Caveat: real subagents run on gpt-5.4-mini/gpt-5.3-codex-spark; this micro runs
whatever the subscription serves (gpt-5.5). It tests the salience mechanism, not
the exact subagent model. n=REPS (default 5), bypass-sandbox, hand-verifiable.
"""
import json, os, pathlib, shutil, subprocess, sys

EVALS = "/Users/jesse/git/superpowers/superpowers/evals"
MICRO = pathlib.Path(EVALS, "results/.read-micro")
MICRO_C = "/workspace/evals/results/.read-micro"
FIXTURE_SRC = MICRO / "fixture/economics.ts"
HOST_CODEX = pathlib.Path(os.path.expanduser("~/.codex"))
REPS = int(os.environ.get("REPS", "5"))
# Run on the ACTUAL subagent model (real subagents use gpt-5.4-mini /
# gpt-5.3-codex-spark, not the gpt-5.5 orchestrator). codex exec -m honors it.
MODEL = os.environ.get("MODEL", "gpt-5.5")
OUT = MICRO / f"out-subagent-{MODEL}"; OUT.mkdir(parents=True, exist_ok=True)

GUIDANCE = (
    "Read a whole file in ONE `cat <file>` rather than several `sed -n` ranges; "
    "you have no file-reading tool, so each shell read is a model turn."
)

# Realistic implementer/reviewer-style subagent scaffolding around a read-heavy
# job. {GUIDE_TOP} / {GUIDE_MID} are placeholders the variants fill.
def prompt(top, mid):
    return f"""{top}You are an implementer subagent working on Task 3 of a larger plan. Another
subagent will build on your output, so be accurate.

## Task brief

Read the task brief: summarize the public API of economics.ts so the next task
can consume it without re-reading the source.
{mid}
## Context

This is part of a multi-task subagent-driven build. Work from the current
directory. Dependencies from earlier tasks are already in place.

## Before you begin

If the requirements or approach are unclear, ask before starting. Otherwise
proceed.

## Your job

1. Read economics.ts — you need the FULL file (every exported function and
   interface).
2. Produce a one-line summary of what each export does.
3. Report your findings concisely.

## Code organization

Keep your work focused and follow existing patterns; don't restructure code
outside your task.

## When you're in over your head

It is always OK to stop and escalate with BLOCKED/NEEDS_CONTEXT rather than guess.

## Report format

Report one line per export. Keep it tight.
"""

VARIANTS = {
    "SUB0-control": prompt("", ""),
    "SUB1-buried":  prompt("", f"\n**Reading files efficiently:** {GUIDANCE}\n"),
    "SUB2-top":     prompt(f"**Reading files efficiently:** {GUIDANCE}\n\n", ""),
    "SUB3-wrap":    prompt(f"<EXTREMELY_IMPORTANT>\n{GUIDANCE}\n</EXTREMELY_IMPORTANT>\n\n", ""),
}


def run_sample(name, prompt_text, rep):
    tag = f"{name}-r{rep}"
    dst = OUT / f"{tag}.jsonl"
    if dst.exists():
        print("cached", tag); return
    home = MICRO / "homes-s" / MODEL / tag / ".codex"
    work = MICRO / "work-s" / MODEL / tag
    for d in (home, work):
        d.mkdir(parents=True, exist_ok=True)
    shutil.copy(HOST_CODEX / "auth.json", home / "auth.json")
    if (HOST_CODEX / "config.toml").exists():
        shutil.copy(HOST_CODEX / "config.toml", home / "config.toml")
    shutil.copy(FIXTURE_SRC, work / "economics.ts")
    (work / "prompt.txt").write_text(prompt_text)
    cmd = (f'export CODEX_HOME={MICRO_C}/homes-s/{MODEL}/{tag}/.codex; '
           f'cd {MICRO_C}/work-s/{MODEL}/{tag}; '
           f'codex exec -m {MODEL} "$(cat prompt.txt)" '
           f'--dangerously-bypass-approvals-and-sandbox '
           f'--skip-git-repo-check --output-last-message answer.txt')
    print("running", tag, "...", flush=True)
    subprocess.run(["scripts/evals-container", "exec", "bash", "-lc", cmd],
                   cwd=EVALS, capture_output=True, text=True, timeout=600)
    rolls = list((MICRO / "homes-s" / MODEL / tag / ".codex").glob("sessions/**/rollout-*.jsonl"))
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
        if ("sed -n" in c) or ("head " in c) or ("tail " in c): chunk += 1
        elif "cat " in c: full_cat += 1
    return full_cat, chunk


def main():
    for name, p in VARIANTS.items():
        for rep in range(REPS):
            run_sample(name, p, rep)
    print("\n=== SUBAGENT-PROMPT SALIENCE SCORES (fixture economics.ts) ===")
    print(f"{'variant':<14}{'reps':>5}{'chunk/run':>11}{'cat/run':>9}{'one-cat%':>10}")
    for name in VARIANTS:
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
