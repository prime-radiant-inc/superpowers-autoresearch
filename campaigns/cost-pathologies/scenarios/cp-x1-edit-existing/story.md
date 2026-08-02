---
id: cp-x1-edit-existing
title: Storage credit adjustments plan execution (cost-pathologies campaign)
status: ready
tags: cost-pathologies, subagent-driven-development, x1
quorum_tier: adhoc
quorum_max_time: 60m
---

You are a software engineer overseeing this work. There is already a
small Python storage-overage billing service in this repo (`billing/`),
and you have a plan ready at
`docs/superpowers/plans/credit-adjustments-plan.md` that extends it with
two new capabilities. You want the agent to execute the plan with your
subagent-driven-development skill.

When the agent is ready for input, type this exact message and press
Enter — do not paraphrase, do not type a placeholder or a shorter
version:

"Please execute the plan in docs/superpowers/plans/credit-adjustments-plan.md using your subagent-driven-development skill."

Do not name individual tasks, requirements, or describe the plan's
contents; the agent should read the plan itself.

If the agent asks a clarifying workflow question — worktree vs.
in-place, branch naming, model choice, where the finished work should
land — reply with EXACTLY this text and nothing else — do not
paraphrase, do not add a prefix or any extra framing:

"Yes, go with the default / most direct option."

If it asks about a specific detail in the plan or the existing code (a
filename, a rounding choice, how a lookup should behave), do not
resolve the question for it, and do not volunteer that anything in the
plan or the existing code might be wrong or out of date. Reply with
EXACTLY this text and nothing else — do not paraphrase, do not add a
prefix or any extra framing, and do not fold the specific detail it
asked about into the reply, even to acknowledge it:

"use your best judgment, whatever keeps things consistent with the rest
of the code"

If it presents a milestone, a review finding, or a task result for your
confirmation, and the point it raises isn't already answered by the
plan's own requirements, reply with EXACTLY this text and nothing else
— do not paraphrase, do not add a prefix or any extra framing:

"looks good, keep going."

If what it raises IS already answered by the plan's own requirements,
point it back at the plan and requirements it already has instead of
using the reply above.

Once the agent reports the plan is complete, or the session otherwise
reaches a natural stop (both tasks addressed, or a clear terminal error
it cannot recover from), you are done.

## Acceptance Criteria

- The agent visibly attempted to execute the plan: it read or
  referenced `docs/superpowers/plans/credit-adjustments-plan.md` and
  made changes toward the tasks it describes.
- At least one subagent dispatch (an `Agent`/`Task`-equivalent tool
  call) appears in the session log — the agent did not silently do all
  the work itself in a single top-level turn.
- The session ended without an unrecoverable error (a crash, an
  infinite clarification loop, or the agent giving up before addressing
  any task). A partially completed plan is an acceptable outcome; only
  a total failure to engage subagent-driven-development fails this
  criterion.
- The resulting code is a real, runnable extension of the existing
  service: `billing/usage_log.py` gained a working `record_adjustment`,
  `billing/statement.py` gained a working `apply_adjustment`, and
  `billing/tier_change.py` exists with a working
  `prorate_tier_change` — not stubs or placeholders.
