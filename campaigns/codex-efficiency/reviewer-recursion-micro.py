#!/usr/bin/env python3
"""E2 MICRO: which reviewer-dispatch phrasing keeps a Codex task reviewer
from spawning/waiting-on another agent, without losing the finding?

E2's registered baseline prediction (`logs/2026-07-28-codex-efficiency.md`)
is that a dispatched branch reviewer produces >=1 descendant in >=half of
reps -- Finding 2 in the source audit. This MICRO is the first cheap probe
at a fix: hold the review TASK fixed (a real 60-line diff with one seeded
off-by-one bug) and vary only the dispatch prompt's delegation guidance.

Variants:
- Z-null      : a bare review request, no SDD template, no delegation
                guidance either way (negative control).
- A-control   : the current `dev`-arm SDD task-reviewer-prompt.md template,
                verbatim, with this fixture's values filled into its
                placeholders. This is the template Finding 2 was raised
                against -- it says nothing about delegation either way.
- B-contract  : A + an explicit personal-performance contract forbidding
                delegation.
- C-budget    : A + a hard numeric budget (0 subagents) framed as a
                protocol violation.

Each sample is a single-turn `codex exec` in a fresh throwaway CODEX_HOME
(scaffold ported from `harnesses/codex-read-delivery-micro.py`: throwaway
home, host auth.json copy, `scripts/evals-container exec`, bypassed
sandbox -- the task only reads fixture files and writes a report, so
sandboxing isn't the variable under test). REPS=5 per variant (env
override), cached per (variant, rep) like the existing micros -- reruns
fill gaps only.

Deliberate deviation from codex-read-delivery-micro.py's scaffold: this
throwaway CODEX_HOME gets ONLY auth.json, never the host's config.toml.
The host's `~/.codex/config.toml` explicitly enables `multi_agent`,
`collaboration_modes`, and the `superpowers` plugin (which would inject
its own SessionStart guidance about spawn isolation into the very session
whose spawn behavior we're trying to isolate the prompt-phrasing effect
on) -- a real confound for this specific test, even though it was harmless
for the read-economy micros. A real SDD battery run's own config.toml
(`evals/results/cx-eff-*/*/home/.codex/config.toml`, verified by direct
read) sets none of the multi_agent/collaboration_modes flags either --
just `[features] plugins = true` plus the superpowers plugin -- so
`spawn_agent` tool availability does not depend on those flags; a bare
auth-only CODEX_HOME is the clean, uncontaminated control.

Score: per-sample `len(extract_spawns(rollout)) > 0` (does the reviewer
delegate at all), and whether the seeded bug is named in the answer file
(`--output-last-message`) -- a coarse regex over the bug's identifying
tokens, cross-checked by a full manual read of every answer file before
the regex's counts are trusted (see out/e2-micro.md).
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

import rollout_parser

EVALS = "/Users/jesse/git/superpowers/superpowers/evals"
MICRO = pathlib.Path(EVALS, "results/.review-micro")
MICRO_C = "/workspace/evals/results/.review-micro"
FIXTURE_DIR = pathlib.Path(__file__).parent / "fixtures" / "review-micro"
OUT = MICRO / "out"
OUT.mkdir(parents=True, exist_ok=True)
HOST_CODEX = pathlib.Path(os.path.expanduser("~/.codex"))
REPS = int(os.environ.get("REPS", "5"))
# Optional comma-separated variant-name filter, for smoke-testing one
# variant before spending the full battery (e.g. ONLY=Z-null,A-control).
ONLY = [v.strip() for v in os.environ.get("ONLY", "").split(",") if v.strip()]

# The dev-arm SDD reviewer-dispatch template. Amendment-1/Task-7 brief:
# "the current SDD code-review dispatch text from the dev skill".
DEV_ARM_TEMPLATE = pathlib.Path(
    "/tmp/sp-arm-dev/skills/subagent-driven-development/task-reviewer-prompt.md"
)

# Fixture values -- see fixtures/review-micro/{task-brief,task-report}.md
# and the review-8353138..a39791b.diff file itself for the full text.
BASE_SHA = "8353138"
HEAD_SHA = "a39791b"
DIFF_FILE = "review-8353138..a39791b.diff"
BRIEF_FILE = "task-brief.md"
REPORT_FILE = "task-report.md"
GLOBAL_CONSTRAINTS = (
    "Python 3.10+, standard library only at runtime, pure functions with "
    "no I/O -- no function may print, read files, mutate its inputs, or "
    "use global state."
)


def _extract_template_prompt(path: pathlib.Path) -> str:
    """Pull the literal `prompt: |` block out of task-reviewer-prompt.md's
    fenced dispatch example -- i.e. exactly the text a controller would
    send as the reviewer subagent's initial prompt, not the surrounding
    doc (headers, the Placeholders section, etc). The block is indented 4
    spaces under `  prompt: |`; dedent that fixed amount."""
    lines = path.read_text().splitlines()
    start = next(i for i, l in enumerate(lines) if l.strip() == "prompt: |") + 1
    body = []
    for l in lines[start:]:
        if l.strip() == "```":
            break
        body.append(l[4:] if l.startswith("    ") else l)
    return "\n".join(body).strip() + "\n"


def _fill(template: str) -> str:
    return (
        template.replace("[BRIEF_FILE]", BRIEF_FILE)
        .replace("[GLOBAL_CONSTRAINTS]", GLOBAL_CONSTRAINTS)
        .replace("[REPORT_FILE]", REPORT_FILE)
        .replace("[BASE_SHA]", BASE_SHA)
        .replace("[HEAD_SHA]", HEAD_SHA)
        .replace("[DIFF_FILE]", DIFF_FILE)
    )


def _build_variants() -> dict:
    a_control = _fill(_extract_template_prompt(DEV_ARM_TEMPLATE))
    b_contract = (
        a_control
        + "\nYou personally perform this review. Do not spawn, delegate "
        "to, or wait on any other agent; produce findings directly.\n"
    )
    c_budget = (
        a_control
        + "\nHard budget: 0 subagents. Any delegation is a protocol "
        "violation reported as failure.\n"
    )
    z_null = (
        f"Review the code change in {DIFF_FILE} (base {BASE_SHA}, head "
        f"{HEAD_SHA}), in the current directory. The task brief is in "
        f"{BRIEF_FILE} and the implementer's report is in {REPORT_FILE}. "
        "Report what you find.\n"
    )
    return {
        "Z-null": z_null,
        "A-control": a_control,
        "B-contract": b_contract,
        "C-budget": c_budget,
    }


FIXTURE_FILES = [BRIEF_FILE, REPORT_FILE, DIFF_FILE]

# Bug-identifying tokens (findings-quality guard): the seeded bug is an
# off-by-one loop bound in moving_average (`range(len(values) - window)`
# instead of `range(len(values) - window + 1)`), which silently drops the
# last valid window. A coarse pre-filter only -- every answer file is also
# read by hand (out/e2-micro.md) before trusting this count.
BUG_RE = re.compile(
    r"off[- ]by[- ]one"
    r"|drops?\s+the\s+(last|final)\s+(window|slice|value|element)"
    r"|miss(?:es|ing)\s+the\s+(last|final)\s+(window|slice|value)"
    r"|exclud(?:es|ing)\s+the\s+(last|final)\s+(window|slice|value)"
    r"|n\s*-\s*w\s*\+\s*1"
    r"|len\(values\)\s*-\s*window\b(?!\s*\+\s*1)"
    r"|one\s+(window|slice)\s+short"
    r"|short\s+by\s+one\s+(window|slice)?",
    re.I,
)


def run_sample(name, prompt_text, rep):
    tag = f"{name}-r{rep}"
    dst = OUT / f"{tag}.jsonl"
    answer_dst = OUT / "answers" / f"{tag}.txt"
    if dst.exists() and answer_dst.exists():
        print("cached", tag)
        return
    home = MICRO / "homes" / tag / ".codex"
    work = MICRO / "work" / tag
    (OUT / "answers").mkdir(parents=True, exist_ok=True)
    for d in (home, work):
        d.mkdir(parents=True, exist_ok=True)
    shutil.copy(HOST_CODEX / "auth.json", home / "auth.json")
    for fname in FIXTURE_FILES:
        shutil.copy(FIXTURE_DIR / fname, work / fname)
    (work / "prompt.txt").write_text(prompt_text)
    home_c = f"{MICRO_C}/homes/{tag}/.codex"
    work_c = f"{MICRO_C}/work/{tag}"
    cmd = (
        f"export CODEX_HOME={home_c}; cd {work_c}; "
        f'codex exec "$(cat prompt.txt)" '
        f"--dangerously-bypass-approvals-and-sandbox "
        f"--skip-git-repo-check --output-last-message answer.txt"
    )
    print("running", tag, "...", flush=True)
    subprocess.run(
        ["scripts/evals-container", "exec", "bash", "-lc", cmd],
        cwd=EVALS, capture_output=True, text=True, timeout=900,
    )
    rolls = list((MICRO / "homes" / tag / ".codex").glob("sessions/**/rollout-*.jsonl"))
    if not rolls:
        print("  NO ROLLOUT for", tag)
        return
    shutil.copy(max(rolls, key=lambda p: p.stat().st_mtime), dst)
    answer_src = work / "answer.txt"
    if answer_src.exists():
        shutil.copy(answer_src, answer_dst)
    else:
        answer_dst.write_text("")
        print("  NO answer.txt for", tag)


def used_percent(roll: pathlib.Path):
    """Last token_count event's rate_limits.primary.used_percent, or None."""
    last = None
    for line in open(roll):
        if '"token_count"' not in line:
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue
        p = rec.get("payload", {})
        rl = p.get("rate_limits") or {}
        primary = rl.get("primary") or {}
        if "used_percent" in primary:
            last = primary["used_percent"]
    return last


def score_spawn(roll: pathlib.Path) -> bool:
    return len(rollout_parser.extract_spawns(roll)) > 0


def score_bug(answer_path: pathlib.Path) -> bool:
    if not answer_path.exists():
        return False
    return bool(BUG_RE.search(answer_path.read_text()))


def main():
    variants = _build_variants()
    names = [n for n in variants if not ONLY or n in ONLY]
    for name in names:
        for rep in range(REPS):
            run_sample(name, variants[name], rep)

    print("\n=== E2 REVIEWER-RECURSION MICRO (fixture: review-micro, "
          f"REPS={REPS}) ===")
    print(f"{'variant':<12}{'reps':>5}{'spawn%':>9}{'bug%':>7}")
    up_first = up_last = None
    for name in names:
        rows = []
        for rep in range(REPS):
            roll = OUT / f"{name}-r{rep}.jsonl"
            ans = OUT / "answers" / f"{name}-r{rep}.txt"
            if not roll.exists():
                continue
            rows.append((score_spawn(roll), score_bug(ans)))
            up = used_percent(roll)
            if up is not None:
                if up_first is None:
                    up_first = up
                up_last = up
        if not rows:
            print(f"{name:<12}  (no samples)")
            continue
        n = len(rows)
        spawn_pct = sum(1 for s, _ in rows if s) / n * 100
        bug_pct = sum(1 for _, b in rows if b) / n * 100
        print(f"{name:<12}{n:>5}{spawn_pct:>8.0f}%{bug_pct:>6.0f}%")
    if up_first is not None:
        print(f"\nsub used_percent: {up_first:.1f}% -> {up_last:.1f}%")


if __name__ == "__main__":
    main()
