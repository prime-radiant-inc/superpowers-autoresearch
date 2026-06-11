#!/usr/bin/env python3
"""Micro-test #2: reviewer-dispatch construction guidance.
Does positive recipe beat prohibition for 'no open-ended directives' and
'no test re-runs' in controller-written reviewer prompts?"""
import json, os, sys, urllib.request, pathlib, re

API = "https://api.anthropic.com/v1/messages"
KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = "claude-opus-4-8"
OUT = pathlib.Path("/tmp/sdd-exp/micro2/out")

VARIANTS = {
 "A-prohibition": """- Do not add open-ended directives like "check all uses" or "run race tests
  if useful" without a concrete, task-specific reason
- Do not ask a reviewer to re-run tests the implementer already ran on the
  same code — the implementer's report carries the test evidence""",
 "B-positive": """- Each directive you add for the reviewer should name a concrete,
  task-specific risk: the file or interaction you are asking about and why
  it is in scope for this task. Scope-wide sweeps belong to the final
  whole-branch review.
- When your prompt mentions tests, point at a specific doubt the
  implementer's report leaves open — name the test you want run and what it
  would confirm. The implementer's reported output already covers
  everything they ran.""",
 "D-control": """""",
}

SYSTEM = """You are the controller agent in the superpowers subagent-driven-development workflow. You dispatch a task reviewer subagent after each implementer finishes; the reviewer template takes the task brief path, the implementer's report path, a review-package diff file path, and global constraints. You fill the template and may add task-specific guidance of your own.

From the skill's "Constructing Reviewer Prompts" section:

- Per-task reviews are task-scoped gates. The broad review happens once, at the final whole-branch review.
{variant}
- Include the spec/design's global constraints that bind the task in the requirements you paste."""

USER = """Project: Go CLI "fractals" (cobra, go 1.21), ASCII fractal renderers. Plan has 10 tasks; TDD required.

Task 5 (Mandelbrot algorithm, internal/mandelbrot package) just finished. Implementer's summary: DONE; commits a1b2c3d "feat: mandelbrot renderer"; "11/11 passing, output pristine"; no concerns; report at /work/fractals-cli/.git/sdd/task-5-report.md. The algorithm package uses complex128 math and is consumed by Task 6 (CLI wiring, not yet built). Design global constraints: Go 1.21+ floor; gradient string " .:-=+*#%@" exact; no external deps beyond cobra.

Paths ready: brief /work/fractals-cli/.git/sdd/task-5-brief.md, report /work/fractals-cli/.git/sdd/task-5-report.md, review package /work/fractals-cli/.git/sdd/review-d4e5f6a..a1b2c3d.diff.

Write the reviewer dispatch prompt now (the full prompt text you would send to the reviewer subagent). Output ONLY the prompt text."""

def call(vtext):
    body = {"model": MODEL, "max_tokens": 2000,
        "system": SYSTEM.format(variant=vtext),
        "messages": [{"role": "user", "content": USER}]}
    req = urllib.request.Request(API, json.dumps(body).encode(),
        {"x-api-key": KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.loads(r.read())
    return "".join(b.get("text","") for b in d.get("content",[]) if b.get("type")=="text")

BAD = {
 "open_ended": lambda t: re.search(r'check all|all uses|all call ?sites|everywhere|entire codebase|throughout the', t, re.I) is not None,
 "rerun_tests": lambda t: re.search(r'(re-?run|run) (the )?(full |test )?(suite|tests)\b(?![^.]*only if)(?![^.]*specific doubt)', t, re.I) is not None,
 "race_heavy": lambda t: re.search(r'race detector|-race|-count=', t, re.I) is not None,
}
GOOD = {
 "diff_path": lambda t: 'review-d4e5f6a..a1b2c3d.diff' in t,
 "constraints": lambda t: ('1.21' in t) and (' .:-=+*#%@' in t or 'gradient' in t),
 "named_risk": lambda t: re.search(r'Task 6|complex128|consumed by', t, re.I) is not None,
}
N = int(os.environ.get("N","5"))
print(f"{'variant':14} {'rep':3} {'chars':>6} bad | good")
for name, vtext in VARIANTS.items():
    for i in range(N):
        f = OUT / f"{name}-{i}.txt"
        if not f.exists(): f.write_text(call(vtext))
        t = f.read_text()
        bad=[k for k,fn in BAD.items() if fn(t)]; good=[k for k,fn in GOOD.items() if fn(t)]
        print(f"{name:14} {i:3} {len(t):6} {len(bad)}:{','.join(bad) or '-':28} | {','.join(good) or '-'}")
