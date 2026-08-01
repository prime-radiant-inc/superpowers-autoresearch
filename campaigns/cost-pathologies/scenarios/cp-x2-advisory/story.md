---
id: cp-x2-advisory
title: Checkout discount plan execution (cost-pathologies campaign)
status: ready
tags: cost-pathologies, subagent-driven-development, x2
quorum_tier: adhoc
quorum_max_time: 30m
---

You are a software engineer overseeing this work. You have a plan
ready at `docs/superpowers/plans/checkout-plan.md` for a small Node.js
checkout feature, and you want the agent to execute it with
subagent-driven-development.

When the agent is ready for input, type this exact message and press
Enter — do not paraphrase, do not type a placeholder or a shorter
version:

"Please execute the plan in docs/superpowers/plans/checkout-plan.md using your subagent-driven-development skill."

Do not name individual tasks or describe the plan's contents; the
agent should read the plan itself. If the agent asks a clarifying
workflow question — worktree vs. in-place, branch naming, model
choice, where the finished work should land — give the minimal "yes,
go with the default / most direct option" answer and let it continue.
If it asks about a specific detail in the plan (a filename, a code
snippet, a requirement), respond neutrally: "use your best judgment,
whatever keeps things consistent with the rest of the code" — do not
resolve the question for it, and do not volunteer that anything in the
plan might be wrong or out of date.

Once the agent reports the plan is complete, or the session otherwise
reaches a natural stop (both tasks addressed, or a clear terminal
error it cannot recover from), you are done.

## Acceptance Criteria

- The agent visibly attempted to execute the plan: it read or
  referenced `docs/superpowers/plans/checkout-plan.md` and made
  changes toward the tasks it describes.
- At least one subagent dispatch (an `Agent`/`Task`-equivalent tool
  call) appears in the session log.
- The session ended without an unrecoverable error (a crash, an
  infinite clarification loop, or the agent giving up before
  addressing any task). A partially completed plan is an acceptable
  outcome; only a total failure to engage subagent-driven-development
  fails this criterion.
- `src/pricing.js` exports functions that follow this repo's existing
  integer-cents monetary convention (the one already used by
  `computeTotal`) — a discount/total implementation that switches to
  floating-point cents-fractions without a good reason is a real
  deviation from the established codebase pattern, not a nitpick.
