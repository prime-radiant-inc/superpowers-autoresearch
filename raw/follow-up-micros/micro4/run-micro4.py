#!/usr/bin/env python3
"""Micro-test #4: writing-plans crispening (strict-cost L1).
Can guidance get opus to produce right-sized plans with a Global
Constraints header and per-task Interfaces lines?"""
import json, os, re, time, urllib.request, urllib.error, pathlib

API = "https://api.anthropic.com/v1/messages"
KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = os.environ.get("MODEL", "claude-opus-4-8")
OUT = pathlib.Path(os.environ.get("OUT_DIR","/tmp/sdd-exp/micro4/out"))
SPEC = pathlib.Path(os.environ.get("SPEC_FILE","/tmp/sdd-exp/micro4/fixture-design.md")).read_text()
REPS = 5

RIGHT_SIZE = """## Task Right-Sizing

A task is the smallest unit that carries its own test cycle and is worth a
fresh reviewer's gate. When drawing task boundaries: fold setup,
configuration, scaffolding, and documentation steps into the task whose
deliverable needs them; split only where a reviewer could meaningfully
reject one task while approving its neighbor. Each task ends with an
independently testable deliverable."""

CONSTRAINTS_HDR = """## Global Constraints Section

Immediately after the plan header, write a `## Global Constraints` section
listing the spec's project-wide requirements — version floors, dependency
limits, naming and copy rules, platform requirements — one line each, with
exact values copied verbatim from the spec. Every task's requirements
implicitly include this section."""

INTERFACES = """## Per-Task Interfaces

Give each task an `**Interfaces:**` block naming what it consumes from
earlier tasks and what it produces for later ones, with exact signatures
(function names, parameter and return types). A task's implementer sees
only their own task; the Interfaces block is how they learn the exact
names and types neighboring tasks rely on."""

import os as _os
CRITICAL_ONLY = """## Code in Plans: Critical Sections Only

Include complete code only where correctness is non-obvious: novel
algorithms, tricky math or edge-case logic, exact public interfaces, and
test cases that pin behavior. For routine code — scaffolding, flag
wiring, boilerplate, straightforward glue — write one line describing
what to build and let the implementer write it test-first. A step is
complete when the implementer cannot get the hard parts wrong and is
trusted with the easy parts."""

VARIANTS = {
    "A-control": "",
    "D-critical": RIGHT_SIZE + "\n\n" + CONSTRAINTS_HDR + "\n\n" + INTERFACES + "\n\n" + CRITICAL_ONLY,
    "B-rightsize": RIGHT_SIZE,
    "C-full": RIGHT_SIZE + "\n\n" + CONSTRAINTS_HDR + "\n\n" + INTERFACES,
}
VARIANTS["E-budget"] = VARIANTS["C-full"] + """

## Plan Economy

Keep the complete plan under 1,200 words of prose. Code blocks do not
count against the budget."""
if _os.environ.get("VARIANTS"):
    keep=_os.environ["VARIANTS"].split(",")
    VARIANTS={k:v for k,v in VARIANTS.items() if k in keep}

SYSTEM = """You are writing an implementation plan using the superpowers
writing-plans skill. Write comprehensive plans assuming the engineer has
zero context for our codebase: which files to touch for each task, the
code, the tests, exact commands with expected output. DRY. YAGNI. TDD.
Frequent commits.

## File Structure

Before defining tasks, map out which files will be created or modified and
what each is responsible for. Each file has one clear responsibility.

## Bite-Sized Step Granularity

Within each task, each step is one action (2-5 minutes): write the failing
test / run it to see it fail / implement / run to see it pass / commit.

{extra}

## Task Structure

Use `### Task N: [Component Name]` headings, a **Files:** list with exact
paths, then checkbox steps with complete code blocks, runnable commands,
and expected output.

## Self-Review

After writing the complete plan, check it against the spec yourself:
spec coverage, placeholder scan, type consistency. Fix issues inline."""

def call_with_retry(payload, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(API, json.dumps(payload).encode(),
                {"x-api-key": KEY, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"})
            with urllib.request.urlopen(req, timeout=600) as r:
                return json.loads(r.read())
        except Exception as e:
            if i == tries - 1: raise
            print(f"    retry {i+1} after {type(e).__name__}: {e}")
            time.sleep(20 * (i + 1))

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    user = ("Here is the approved design spec. Write the complete "
            "implementation plan now. Output ONLY the plan markdown.\n\n"
            "<spec>\n" + SPEC + "\n</spec>")
    for vname, extra in VARIANTS.items():
        system = SYSTEM.format(extra=extra).replace("\n\n\n\n", "\n\n")
        for rep in range(REPS):
            f = OUT / f"{vname}-r{rep}.md"
            if f.exists() and f.stat().st_size > 500:
                print(f"  cached {f.name}"); continue
            print(f"  calling {vname} r{rep} ...")
            resp = call_with_retry({
                "model": MODEL, "max_tokens": 12000,
                "system": system,
                "messages": [{"role": "user", "content": user}]})
            text = "".join(b.get("text", "") for b in resp["content"])
            f.write_text(text)
            u = resp.get("usage", {})
            print(f"    {len(text)} chars, in={u.get('input_tokens')} out={u.get('output_tokens')}")

if __name__ == "__main__":
    main()
