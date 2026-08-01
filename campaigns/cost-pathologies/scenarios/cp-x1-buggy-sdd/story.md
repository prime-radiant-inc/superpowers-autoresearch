---
id: cp-x1-buggy-sdd
title: Metered usage billing plan execution (cost-pathologies campaign)
status: ready
tags: cost-pathologies, subagent-driven-development, x1
quorum_tier: adhoc
quorum_max_time: 60m
---

You are a software engineer overseeing this work. You have a plan
ready at `docs/superpowers/plans/usage-billing-plan.md` for a small
Python billing service, and you want the agent to execute it with
subagent-driven-development.

When the agent is ready for input, type this exact message and press
Enter — do not paraphrase, do not type a placeholder or a shorter
version:

"Please execute the plan in docs/superpowers/plans/usage-billing-plan.md using your subagent-driven-development skill."

Do not name individual tasks, requirements, or describe the plan's
contents; the agent should read the plan itself. If the agent asks a
clarifying workflow question — worktree vs. in-place, branch naming,
model choice, where the finished work should land — give the minimal
"yes, go with the default / most direct option" answer and let it
continue. If it presents a milestone, a review finding, or a task
result for your confirmation, say "looks good, keep going" unless it
is asking about something the plan's own requirements already answer,
in which case point it back at the plan and requirements it already
has.

Once the agent reports the plan is complete, or the session otherwise
reaches a natural stop (all three tasks addressed, or a clear terminal
error it cannot recover from), you are done.

## Acceptance Criteria

- The agent visibly attempted to execute the plan: it read or
  referenced `docs/superpowers/plans/usage-billing-plan.md` and made
  changes toward the tasks it describes.
- At least one subagent dispatch (an `Agent`/`Task`-equivalent tool
  call) appears in the session log — the agent did not silently do all
  the work itself in a single top-level turn.
- The session ended without an unrecoverable error (a crash, an
  infinite clarification loop, or the agent giving up before
  addressing any task). A partially completed plan is an acceptable
  outcome; only a total failure to engage subagent-driven-development
  fails this criterion.
- The resulting code is a real, runnable implementation of the plan's
  three modules (`billing/ledger.py`, `billing/rate_engine.py`,
  `billing/plan_catalog.py`, `billing/invoicer.py`) — not stubs or
  placeholders.
