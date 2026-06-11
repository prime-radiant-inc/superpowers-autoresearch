#!/usr/bin/env python3
"""Micro-test: which guidance phrasing keeps the controller from re-typing
spec values into dispatch prompts while preserving curation?
One API call per sample; programmatic scoring."""
import json, os, sys, urllib.request, pathlib, re

API = "https://api.anthropic.com/v1/messages"
KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = "claude-opus-4-8"

PLAN = pathlib.Path(sys.argv[1]).read_text()  # fixture plan.md
OUT = pathlib.Path("/tmp/sdd-exp/micro/out")

VARIANTS = {
 "A-negative": """- **Task brief:** before dispatching an implementer, run this skill's `scripts/task-brief PLAN_FILE N` — it extracts the task's full text to a uniquely named file and prints the path. The brief carries the task text: do not restate it in the dispatch. Your Context section adds only what the brief cannot know — cross-task interfaces, decisions made in earlier tasks, ambiguity resolutions, global constraints.""",
 "B-source-of-truth": """- **Task brief:** before dispatching an implementer, run this skill's `scripts/task-brief PLAN_FILE N` — it extracts the task's full text to a uniquely named file and prints the path. You should make sure the brief stays the implementer's single source for requirements and exact values (numbers, magic strings, signatures, test cases): point at the brief for all of those — "your requirements and their exact values are in the brief; use them verbatim." Spend your dispatch text on what only you know: where the task fits, interfaces settled by earlier tasks, your resolution of any ambiguity in the brief, and the design's global constraints.""",
 "C-recipe": """- **Task brief:** before dispatching an implementer, run this skill's `scripts/task-brief PLAN_FILE N` — it extracts the task's full text to a uniquely named file and prints the path. Compose the dispatch so the brief stays the single source of requirements. Your dispatch should contain: (1) one line on where this task fits in the project; (2) the brief path, introduced as "read this first — it is your requirements, with the exact values to use verbatim"; (3) interfaces and decisions from earlier tasks that the brief cannot know; (4) your resolution of any ambiguity you noticed in the brief; (5) the report-file path and report contract. Exact values (numbers, magic strings, signatures, test cases) appear only in the brief.""",
 "C2-reference": """- **Task brief:** before dispatching an implementer, run this skill's `scripts/task-brief PLAN_FILE N` — it extracts the task's full text to a uniquely named file and prints the path. Compose the dispatch so the brief stays the single source of requirements. Your dispatch should contain: (1) one line on where this task fits in the project; (2) the brief path, introduced as "read this first — it is your requirements, with the exact values to use verbatim"; (3) interfaces and decisions from earlier tasks that the brief cannot know; (4) your resolution of any ambiguity you noticed in the brief — when that means discussing a value from the brief, name it by reference ("the 10-character gradient in your brief") and quote only the fragment your point needs; (5) the report-file path and report contract. Exact values (numbers, magic strings, signatures, test cases) appear only in the brief.""",
 "D-control": """- **Task brief:** before dispatching an implementer, run this skill's `scripts/task-brief PLAN_FILE N` — it extracts the task's full text to a uniquely named file and prints the path. Give the implementer that path in the dispatch.""",
}

SYSTEM = """You are the controller agent in the superpowers subagent-driven-development workflow, executing an implementation plan by dispatching fresh subagents per task. You never implement anything yourself.

Relevant skill guidance for constructing implementer dispatches:

{variant}

- **Report file:** name the implementer's report file after the brief (brief `.../task-N-brief.md` -> report `.../task-N-report.md`) and put it in the dispatch prompt. The implementer writes the full report there and returns only status, commits, a one-line test summary, and concerns."""

USER = """Project: a Go CLI ("fractals") rendering ASCII fractals, per design.md and plan.md in the repo root. Working dir: /work/fractals-cli. Go 1.21, cobra. TDD is required by the plan.

State: Tasks 1-4 are complete and reviewed (project setup; cobra CLI framework with --help; sierpinski algorithm in internal/sierpinski; sierpinski CLI subcommand). HEAD is clean.

The full plan (you read it at session start):

<plan>
{plan}
</plan>

You have just run: scripts/task-brief plan.md 5
-> wrote /work/fractals-cli/.git/sdd/task-5-brief.md: 19 lines (it contains the plan's Task 5 section verbatim)

Write the dispatch prompt for the Task 5 implementer subagent now. Output ONLY the prompt text you would send to the subagent."""

def call(variant_text):
    body = {
        "model": MODEL, "max_tokens": 2000,
        "system": SYSTEM.format(variant=variant_text),
        "messages": [{"role": "user", "content": USER.format(plan=PLAN)}],
    }
    req = urllib.request.Request(API, json.dumps(body).encode(),
        {"x-api-key": KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.loads(r.read())
    return "".join(b.get("text","") for b in d.get("content",[]) if b.get("type")=="text")

MARKERS = {  # unambiguous transcription of brief values
 "gradient":  lambda t: ' .:-=+*#%@' in t,
 "region":    lambda t: '-2.5' in t,
 "signature": lambda t: re.search(r'Render\(width,\s*height,\s*maxIter int', t) is not None,
 "verifycmd": lambda t: 'go test ./internal/mandelbrot' in t,
 "testpoint": lambda t: re.search(r'\(2,\s*0\)|2\+0i', t) is not None,
}
GOOD = {
 "brief_ref": lambda t: 'task-5-brief' in t,
 "report_ref":lambda t: 'task-5-report' in t,
 "boundary":  lambda t: re.search(r'Task 6|task 6', t) is not None,  # curation: scope boundary
}

N = int(os.environ.get("N", "5"))
print(f"{'variant':18} {'rep':3} {'chars':>6} transcribed | good")
for name, vtext in VARIANTS.items():
    for i in range(N):
        f = OUT / f"{name}-{i}.txt"
        if not f.exists():
            f.write_text(call(vtext))
        t = f.read_text()
        bad = [k for k,fn in MARKERS.items() if fn(t)]
        good = [k for k,fn in GOOD.items() if fn(t)]
        print(f"{name:18} {i:3} {len(t):6} {len(bad)}:{','.join(bad) or '-':40} | {','.join(good) or '-'}")
