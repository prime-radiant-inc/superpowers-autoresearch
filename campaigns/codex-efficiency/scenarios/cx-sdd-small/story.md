---
id: cx-sdd-small
title: SDD small-plan execution (codex efficiency campaign)
status: ready
tags: codex, subagent-driven-development, codex-efficiency
quorum_tier: adhoc
quorum_max_time: 25m
---

You have a plan ready at `plan.md` for a tiny Python package. You want the
agent to execute it with subagent-driven-development.

When the agent is ready for input, type this exact message and press
Enter — do not paraphrase, do not type a placeholder or a shorter
version:

"Please execute the plan in plan.md using your subagent-driven-development skill."

Do not name individual tasks or describe the plan's contents; the agent
should read `plan.md` itself. If the agent asks a clarifying workflow
question — worktree vs. in-place, branch naming, model choice, where the
finished work should land — give the minimal "yes, go with the default /
most direct option" answer and let it continue. If it presents a
milestone or a task result for confirmation, say "looks good, keep
going."

This run feeds an efficiency-instrumentation pipeline, not a code-quality
review — your job is to keep the agent moving, not to inspect the
output. Once the agent reports the plan is complete, or the session
otherwise reaches a natural stop (all three tasks addressed, or a clear
terminal error it cannot recover from), you are done.

## Acceptance Criteria

- The agent visibly attempted to execute the plan: it read or referenced
  `plan.md` and made changes toward the tasks it describes.
- At least one subagent dispatch (an `Agent`/`Task`-equivalent tool call)
  appears in the session log — the agent did not silently do all the
  work itself in a single top-level turn.
- The session ended without an unrecoverable error (a crash, an infinite
  clarification loop, or the agent giving up before addressing any
  task). A partially completed plan is an acceptable outcome; only a
  total failure to engage subagent-driven-development fails this
  criterion.

Note: this scenario feeds an offline efficiency scorer that reads the raw
Codex rollout directly (fork hygiene, spawn args, review recursion).
Passing here only certifies the run is usable input for that scorer — it
does not grade code quality.
