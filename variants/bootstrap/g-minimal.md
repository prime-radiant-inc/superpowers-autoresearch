---
name: using-superpowers
description: Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

## The Rule

**Invoke relevant or requested skills BEFORE any response or action** — including clarifying questions, exploring the codebase, or checking files. Even a 1% chance a skill applies means you invoke it to check. If it turns out wrong for the situation, you don't have to use it.

**Before entering plan mode:** if you haven't already brainstormed, invoke the brainstorming skill first.

Then announce "Using [skill] to [purpose]" and follow the skill exactly. If it has a checklist, create a todo per item.

## Skill Priority

Process skills first (brainstorming, systematic-debugging) — they determine HOW to approach the task. Implementation skills (frontend-design, etc.) second.

- "Let's build X" → brainstorming first, then implementation skills.
- "Fix this bug" → systematic-debugging first, then domain skills.

## Red Flags

These thoughts mean STOP—you're rationalizing your way out of a skill:

"This is just a simple question" · "I need more context first" · "Let me explore the codebase first" · "I can check git/files quickly" · "I remember this skill" · "The skill is overkill" · "I'll just do this one thing first".

Questions are tasks. Actions are tasks. The skill check comes BEFORE clarifying questions, exploring, or gathering information. Skills evolve — invoke the current version, don't rely on memory.

## How to Access Skills

Never read skill files manually — load them via your platform's skill mechanism (Claude Code/Copilot: `Skill` tool; Codex: native; Gemini: `activate_skill`). Per-platform tool mappings: `references/*-tools.md`.

## User Instructions

User instructions (CLAUDE.md, GEMINI.md, AGENTS.md, direct requests) take precedence over skills, which in turn override default system behavior. Instructions say WHAT, not HOW — "Add X" or "Fix Y" doesn't mean skip workflows.
