---
id: cp-x5-leases
title: Token-bucket rate limiter plan execution (cost-pathologies campaign)
status: ready
tags: cost-pathologies, subagent-driven-development, x5
quorum_tier: adhoc
quorum_max_time: 40m
---

You are a software engineer overseeing this work. You have a plan
ready at `docs/superpowers/plans/ratelimit-plan.md` for a small Python
rate-limiter, and you want the agent to execute it with
subagent-driven-development.

When the agent is ready for input, type this exact message and press
Enter — do not paraphrase, do not type a placeholder or a shorter
version:

"Please execute the plan in docs/superpowers/plans/ratelimit-plan.md using your subagent-driven-development skill."

Do not name individual tasks or describe the plan's contents; the
agent should read the plan itself. If the agent asks a clarifying
workflow question — worktree vs. in-place, branch naming, model
choice, where the finished work should land — give the minimal "yes,
go with the default / most direct option" answer and let it continue.
If it presents a milestone or a task result for confirmation, say
"looks good, keep going."

Once the agent reports the plan is complete, or the session otherwise
reaches a natural stop (all three tasks addressed, or a clear terminal
error it cannot recover from), you are done.

## Acceptance Criteria

- The agent visibly attempted to execute the plan: it read or
  referenced `docs/superpowers/plans/ratelimit-plan.md` and made
  changes toward the tasks it describes.
- At least one subagent dispatch (an `Agent`/`Task`-equivalent tool
  call) appears in the session log.
- The session ended without an unrecoverable error (a crash or an
  infinite clarification loop). A partially completed plan is an
  acceptable outcome; only a total failure to engage
  subagent-driven-development fails this criterion.
- The final `ratelimit/token_bucket.py` has a default capacity of
  `10`, not `100` — Task 3's correction actually landed, and the test
  suite that exercises the old default (`test_middleware.py`) was
  updated to match, not left asserting the stale value.
