#!/usr/bin/env python3
"""E4 MICRO: does an entry-decision guidance paragraph make a model choose
proportional ceremony (SPIKE / BOUNDED / FULL) per task class, or does it
apply the same heavy process regardless of task shape?

E4's registered baseline prediction (`logs/2026-07-28-codex-efficiency.md`,
Task 1 entry, extended by the Task 11 pre-registration) is that ceremony
census is statistically indistinguishable across spike/bounded/
architectural task classes on live Codex sessions -- i.e. the
`brainstorming` hard-gate's absolute wording ("This applies to EVERY
project regardless of perceived simplicity") is applied uniformly rather
than scaled to task complexity. This MICRO isolates the entry-decision TEXT
from session-shape confounds (a live Codex session's own triggering
behavior, subagent dispatch, etc.) by asking a model directly, out of band:
given only a system-prompt paragraph and one task description, which path
would it choose? One Anthropic Messages API call per sample; programmatic
scoring via a forced one-word answer.

This is treatment-phrasing PRE-WORK only, per the task brief -- no skill
edits land in this campaign. B-three-path is a router paragraph drafted for
this task; it is not the current brainstorming skill text and is not
proposed for adoption without further evaluation.

Variants:
- Z-null       : no guidance about entry-path/ceremony at all (negative
                 control).
- A-current    : the verbatim <HARD-GATE> block from
                 `/tmp/sp-arm-dev/skills/brainstorming/SKILL.md` lines
                 12-14 -- the literal text Finding 4 was raised against.
- B-three-path : a drafted router paragraph distinguishing spike/bounded/
                 architectural ceremony levels explicitly.

Each of the three E4 task-class briefs (spike/bounded/arch, verbatim from
scenarios/cx-ceremony-{spike,bounded,arch}/story.md) is put to the model
under each variant. REPS=5 per (variant, task) cell (45 calls total),
cached per (variant, task, rep) -- reruns fill gaps only.
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

OUT = pathlib.Path("/tmp/ceremony-path-micro/out")
OUT.mkdir(parents=True, exist_ok=True)

# The three E4 task-class briefs, verbatim from
# scenarios/cx-ceremony-{spike,bounded,arch}/story.md's fixed Gauntlet
# typed message.
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
}

# The verbatim current brainstorming hard-gate (dev arm,
# /tmp/sp-arm-dev/skills/brainstorming/SKILL.md lines 12-14) and a drafted
# three-path router. Z-null carries no guidance at all.
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
    "B-three-path": (
        "Relevant guidance from your skill instructions:\n\n"
        "Before starting any work, classify the request into one of three "
        "paths and calibrate ceremony accordingly:\n"
        "- Spike: a feasibility question or throwaway investigation "
        '("can we...", "is it possible...", "quick and dirty is fine") '
        "needs no design document and no approval gate — just go find "
        "out, as cheaply as correctness allows.\n"
        "- Bounded: a well-scoped change to an existing, understood flow "
        "(a new flag, a small endpoint, a one-file fix) needs at most a "
        "couple of clarifying questions — skip the design document and "
        "approval gate unless the user asks for one.\n"
        "- Architectural: a change that restructures how components fit "
        "together, adds a new subsystem, or changes a public interface "
        "other teams depend on needs the full design-and-approval process "
        "— present a design, write it up, and wait for explicit "
        "approval before implementing.\n"
        "When in doubt between two paths, use the heavier one."
    ),
}

SYSTEM = """You are a coding agent working inside an existing small software project, using a skill-based workflow. Before starting any work in response to a request, you decide how much process to apply.

{variant}

A user is about to describe a task. Decide how much process you would apply before doing any work, and answer with EXACTLY ONE WORD on its own line, chosen from: SPIKE, BOUNDED, FULL. Output nothing else -- no explanation, no punctuation, no other words.

- SPIKE means: dive in immediately with a minimal, quick investigation or throwaway prototype -- no design document, no approval step before starting.
- BOUNDED means: make the change directly, asking at most a couple of clarifying questions if truly needed -- no design document, no approval gate.
- FULL means: follow the complete design-and-approval process before touching any code -- present a design, write it up, and get explicit user approval before implementing anything."""

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

    out_json = OUT.parent / "results.json"
    out_json.write_text(json.dumps(
        {f"{v}|{t}": c for (v, t), c in results.items()}, indent=2))
    print(f"wrote {out_json}", file=sys.stderr)


if __name__ == "__main__":
    main()
