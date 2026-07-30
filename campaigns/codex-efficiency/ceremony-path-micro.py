#!/usr/bin/env python3
"""E4 MICRO layer 1: does the shipped brainstorming three-path router text
make a model choose proportional ceremony (SPIKE / BOUNDED / FULL) per task
class -- and does it hold up against adversarially ambiguous briefs the
original campaign micro never tested?

This is the codex-efficiency-fixes Task 7 extension of the original E4
ceremony-path MICRO (`logs/2026-07-28-codex-efficiency.md`, Task 1 entry;
pre-registered further in `logs/2026-07-30-codex-efficiency-fixes.md`,
T4 layer 1). It supersedes the original run in two ways:

1. B-three-path (a drafted router paragraph, never shipped) is replaced by
   C-approval: the `## Three Paths` section of `skills/brainstorming/
   SKILL.md` AS SHIPPED (Task 5's commit, `5ea8821`) -- the lead-in
   sentence, the three bullets, and the doubt/ratchet paragraph, verbatim.
2. The shared SYSTEM answer definitions (SPIKE/BOUNDED/FULL) are
   neutralized to classify the ARTIFACT produced, not the approval step --
   every path in the shipped skill text ends with human approval, so a
   definition that ties SPIKE/BOUNDED to "no approval gate" would make
   C-approval unscoreable by construction. Because of this taxonomy
   change, results here are NOT comparable cell-by-cell to the original
   campaign micro; comparisons are within this run only.

Also adds two adversarial briefs the campaign never tested: ambig-interface
and ambig-crosscut -- both surface-bounded tasks (a flag, a one-file bug
fix) that hide a public-interface or cross-cutting dependency an
under-classifying model would miss.

This is treatment-phrasing evaluation only -- no further skill edits land
from this script.

Variants:
- Z-null     : no guidance about entry-path/ceremony at all (negative
               control).
- A-current  : the verbatim <HARD-GATE> block from
               `/tmp/sp-arm-dev/skills/brainstorming/SKILL.md` lines 12-14
               -- the literal text Finding 4 was raised against.
- C-approval : the shipped Three Paths block (see above), verbatim.

Each of the five briefs (spike/bounded/arch, verbatim from
scenarios/cx-ceremony-{spike,bounded,arch}/story.md, plus the two
adversarial briefs above) is put to the model under each variant.
REPS=5 per (variant, brief) cell (3 x 5 x 5 = 75 calls total), cached per
(variant, brief, rep) in out/micro-c/ -- reruns fill gaps only.
"""
import json
import os
import pathlib
import re
import sys
import urllib.request

API = "https://api.anthropic.com/v1/messages"
KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = os.environ.get("MODEL", "claude-opus-4-8")
REPS = int(os.environ.get("REPS", "5"))

OUT = pathlib.Path(__file__).parent / "out" / "micro-c"
OUT.mkdir(parents=True, exist_ok=True)

# The three E4 task-class briefs, verbatim from
# scenarios/cx-ceremony-{spike,bounded,arch}/story.md's fixed Gauntlet
# typed message, plus two adversarial briefs added for Task 7: each reads
# as a bounded, well-scoped change but hides an interface/cross-cutting
# dependency that should ratchet it up to FULL.
TASKS = {
    "spike": (
        "Can we detect whether the service's port is already in use "
        "before binding? Not sure it's possible portably — find out, "
        "quick and dirty is fine."
    ),
    "bounded": (
        "Add a --quiet flag that suppresses request logging. The logging "
        "call sites are in server.py."
    ),
    "arch": (
        "We need to split the service into a reusable library + thin CLI "
        "so another team can embed it."
    ),
    "ambig-interface": (
        "Add a --json flag to our export CLI command so output can be "
        "piped to jq. The current text output of export is parsed "
        "line-by-line by three downstream scripts in tools/ that other "
        "teams run in their pipelines."
    ),
    "ambig-crosscut": (
        "Fix the timezone bug in report_generator.py where daily rollups "
        "are off by one day for users west of UTC. Rollup boundaries are "
        "also computed independently in the billing exporter and the "
        "retention job, which must stay consistent with reports."
    ),
}

# The verbatim current brainstorming hard-gate (dev arm,
# /tmp/sp-arm-dev/skills/brainstorming/SKILL.md lines 12-14) and the
# shipped `## Three Paths` section (`skills/brainstorming/SKILL.md`,
# Task 5 commit `5ea8821`, lead-in sentence + three bullets + doubt/ratchet
# paragraph, verbatim -- no heading, no surrounding sections). Z-null
# carries no guidance at all.
VARIANTS = {
    "Z-null": (
        "(No additional guidance has been given about how much process to "
        "apply before starting work.)"
    ),
    "A-current": (
        "Relevant guidance from your skill instructions (verbatim):\n\n"
        "<HARD-GATE>\n"
        "Do NOT invoke any implementation skill, write any code, scaffold "
        "any project, or take any implementation action until you have "
        "presented a design and the user has approved it. This applies to "
        "EVERY project regardless of perceived simplicity.\n"
        "</HARD-GATE>"
    ),
    "C-approval": (
        "Relevant guidance from your skill instructions (verbatim, the "
        "brainstorming skill's Three Paths section):\n\n"
        "Before your first question, classify the request and say the "
        "classification out loud — \"this looks bounded, so I'll present a "
        "short design here rather than write a spec\" — so your human partner "
        "can override it:\n\n"
        "- **Spike** — a feasibility question (\"can we...\", \"is it "
        "possible...\", \"quick and dirty is fine\") whose output is an answer, "
        "not code you keep. Present the question and what you'll try in 2-3 "
        "sentences, get a nod, then find out as cheaply as correctness "
        "allows. No design doc, no spec file. Report findings as a "
        "recommendation; anything you built stays labeled throwaway.\n"
        "- **Bounded** — a well-scoped change to an existing, understood "
        "flow: a new flag, a small endpoint, a one-file fix. Ask the "
        "clarifying questions that matter, present a short design IN CHAT (a "
        "few sentences to a few short paragraphs), and get approval. No spec "
        "file, no implementation plan document.\n"
        "- **Architectural** — new projects, new subsystems, changes that "
        "restructure how components fit together or alter interfaces others "
        "depend on. Follow the full process: questions, approaches, sectioned "
        "design, written spec, then the writing-plans skill.\n\n"
        "When in doubt between two paths, take the heavier one. The ratchet "
        "is one-way: hidden complexity discovered mid-task upgrades the path "
        "— stop, say so, and step up. Nothing downgrades mid-task."
    ),
}

SYSTEM = """You are a coding agent working inside an existing small software project, using a skill-based workflow. Before starting any work in response to a request, you decide how much process to apply.

{variant}

A user is about to describe a task. Decide how much process you would apply before doing any work, and answer with EXACTLY ONE WORD on its own line, chosen from: SPIKE, BOUNDED, FULL. Output nothing else -- no explanation, no punctuation, no other words.

- SPIKE means: dive straight into a minimal throwaway investigation — no design document.
- BOUNDED means: make the change after at most brief clarification and a short in-chat design — no design document, no implementation plan.
- FULL means: run the complete design process — written design document and implementation plan before touching code."""

USER = """<task>
{task}
</task>

Answer with exactly one word: SPIKE, BOUNDED, or FULL."""

ANSWER_RE = re.compile(r"\b(SPIKE|BOUNDED|FULL)\b", re.I)


def call(variant_text, task_text):
    body = {
        "model": MODEL,
        "max_tokens": 20,
        "system": SYSTEM.format(variant=variant_text),
        "messages": [{"role": "user", "content": USER.format(task=task_text)}],
    }
    req = urllib.request.Request(
        API, json.dumps(body).encode(),
        {"x-api-key": KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.loads(r.read())
    return "".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text")


def classify(answer_text):
    m = ANSWER_RE.search(answer_text)
    return m.group(1).upper() if m else None


def run_sample(variant_name, task_name, rep):
    f = OUT / f"{variant_name}-{task_name}-{rep}.txt"
    if not f.exists():
        f.write_text(call(VARIANTS[variant_name], TASKS[task_name]))
    return f.read_text()


def main():
    print(f"# E4 ceremony-path MICRO (MODEL={MODEL}, REPS={REPS})")
    print()
    results = {}  # (variant, task) -> list[classification or None]
    for variant_name in VARIANTS:
        for task_name in TASKS:
            classes = []
            for rep in range(REPS):
                raw = run_sample(variant_name, task_name, rep)
                classes.append(classify(raw))
            results[(variant_name, task_name)] = classes

    header = f"{'variant':<14}" + "".join(f"{t:>18}" for t in TASKS)
    print(header)
    print("-" * len(header))
    for variant_name in VARIANTS:
        row = f"{variant_name:<14}"
        for task_name in TASKS:
            classes = results[(variant_name, task_name)]
            counts = {c: classes.count(c) for c in ("SPIKE", "BOUNDED", "FULL")}
            unparsed = sum(1 for c in classes if c is None)
            cell = "/".join(f"{counts[k]}" for k in ("SPIKE", "BOUNDED", "FULL"))
            if unparsed:
                cell += f" (?{unparsed})"
            row += f"{cell:>18}"
        print(row)
    print()
    print("cell format: SPIKE/BOUNDED/FULL counts out of REPS; (?N) = N unparseable answers")
    print()

    out_json = OUT / "results.json"
    out_json.write_text(json.dumps(
        {f"{v}|{t}": c for (v, t), c in results.items()}, indent=2))
    print(f"wrote {out_json}", file=sys.stderr)


if __name__ == "__main__":
    main()
