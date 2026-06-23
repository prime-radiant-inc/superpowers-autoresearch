#!/usr/bin/env python3
"""Generate bootstrap-compression ablation variants from the live baseline.

Each variant is a byte-clean transformation of the baseline
`using-superpowers/SKILL.md`, changing ONE lever at a time so triggering-rate
deltas are attributable (autoresearch doctrine: ablate one thing at a time).

Run:  python3 generate-variants.py   (writes ./*.md next to this script)
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
BASE = os.path.join(REPO_PARENT, "superpowers", "skills", "using-superpowers", "SKILL.md")

baseline = open(BASE).read()

PLAN_LINE = ("**Before entering plan mode:** if you haven't already brainstormed, "
             "invoke the brainstorming skill first.")


def strip_dot(t):
    """Remove the graphviz digraph fenced block; keep its load-bearing rule as prose."""
    return re.sub(r"\n```dot\n.*?\n```\n", "\n" + PLAN_LINE + "\n", t, flags=re.S)


def strip_section(t, header):
    """Remove a markdown section: from `header` line through just before the next
    #/## header (or EOF)."""
    pat = re.compile(r"(?m)^" + re.escape(header) + r"\s*\n.*?(?=^#{1,2} |\Z)", re.S)
    return re.sub(pat, "", t)


def compress_platform(t):
    """Collapse the per-platform 'How to Access Skills' + 'Platform Adaptation'
    sections into a terse two-liner."""
    terse = (
        "## How to Access Skills\n\n"
        "Never read skill files manually — load them via your platform's skill "
        "mechanism (Claude Code/Copilot: `Skill` tool; Codex: native; Gemini: "
        "`activate_skill`). Skills speak in actions (\"dispatch a subagent\", "
        "\"read a file\"); per-platform tool mappings live in `references/*-tools.md`.\n"
    )
    t = strip_section(t, "## How to Access Skills")
    t = strip_section(t, "## Platform Adaptation")
    # reinsert the terse block where the original section was (before "# Using Skills")
    return t.replace("# Using Skills\n", terse + "\n# Using Skills\n", 1)


def strip_block(t, start, end):
    """Remove an XML-ish block from `start` line through `end` line, inclusive."""
    return re.sub(re.escape(start) + r".*?" + re.escape(end) + r"\n?", "", t, flags=re.S)


# Trigger-only description per writing-skills SDO: say WHEN to use, never WHAT it
# does or its workflow. The baseline description's "establishes how to find and use
# skills, requiring skill invocation…" is mechanism/workflow — cut it.
LEAN_DESC = ("description: Use when starting any conversation, before any response "
             "or action, including clarifying questions")


def lean_description(t):
    return re.sub(r"(?m)^description: .*$", LEAN_DESC, t)


VARIANTS = {
    # --- single-lever removals (independent ablations) ---
    "a-no-digraph": strip_dot(baseline),
    "b-no-platform": compress_platform(baseline),
    "c-no-redflags": strip_section(baseline, "## Red Flags"),
    "d-no-skill-types": strip_section(baseline, "## Skill Types"),
    "e-no-instruction-priority": strip_section(baseline, "## Instruction Priority"),
    # --- cumulative "lean" (safe removals, Red Flags + Rule + Skill Priority kept) ---
    "f-lean": strip_section(
        compress_platform(strip_dot(baseline)), "## Skill Types"),
    # --- bisection: candidate load-bearing content for systematic-debugging trigger ---
    "h-no-skill-priority": strip_section(baseline, "## Skill Priority"),
    "i-no-extremely-important": strip_block(baseline, "<EXTREMELY-IMPORTANT>", "</EXTREMELY-IMPORTANT>"),
    "j-no-the-rule": strip_section(baseline, "## The Rule"),
    # --- Jesse's targeted edits (2026-06-21 review) ---
    # l: drop the "How to Access Skills" section + Platform Adaptation ENTIRELY
    #    (Jesse: the "Never read skill files manually / Claude Code: Skill tool…" line can go).
    "l-no-access": strip_section(strip_section(baseline, "## How to Access Skills"), "## Platform Adaptation"),
    # m: drop the <SUBAGENT-STOP> block. Jesse: it's wrong when the content is INJECTED AS
    #    PROSE at session start (not invoked as a skill) — "skip this skill" has no referent.
    "m-no-subagent-stop": strip_block(baseline, "<SUBAGENT-STOP>", "</SUBAGENT-STOP>"),
    # o: trigger-only description (writing-skills SDO compliance). Single lever vs baseline.
    "o-lean-description": lean_description(baseline),
}


def main():
    print(f"baseline: {len(baseline)} chars\n")
    for name, text in VARIANTS.items():
        # collapse any triple-newlines left by removals
        text = re.sub(r"\n{3,}", "\n\n", text)
        out = os.path.join(HERE, name + ".md")
        with open(out, "w") as f:
            f.write(text)
        print(f"  {name:28s} {len(text):5d} chars  ({len(text)-len(baseline):+d} vs baseline)")
    print(f"\nwrote {len(VARIANTS)} variants to {HERE}")
    print("note: a hand-authored aggressive 'g-minimal.md' is maintained separately.")


if __name__ == "__main__":
    main()
