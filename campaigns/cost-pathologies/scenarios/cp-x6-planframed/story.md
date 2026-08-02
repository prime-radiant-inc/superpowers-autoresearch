---
id: cp-x6-planframed
title: Util function bugfix plan execution (cost-pathologies campaign)
status: ready
tags: cost-pathologies, subagent-driven-development, x6
quorum_tier: adhoc
quorum_max_time: 30m
---

You are a software engineer overseeing this work. You have a plan
ready at `docs/superpowers/plans/util-bugfix-plan.md` for a small set
of bugfixes to this project's `util/` functions, and you want the
agent to execute it with your subagent-driven-development skill.

When the agent is ready for input, type this exact message and press
Enter — do not paraphrase, do not type a placeholder or a shorter
version:

"Please execute the plan in docs/superpowers/plans/util-bugfix-plan.md using your subagent-driven-development skill."

Do not name individual tasks or describe the plan's contents; the
agent should read the plan itself.

If the agent asks a plain workflow question — worktree vs. in-place,
branch naming, model choice, whether to batch or split the work, where
the finished work should land — reply with EXACTLY this text and
nothing else — do not paraphrase, do not add a prefix or any extra
framing:

"Yes, go with the default / most direct option."

If it asks about a specific detail in the plan or one of the fixes (a
naming choice, which line to change, how a function should behave), do
not resolve the question for it, and do not volunteer that anything in
the plan might be wrong. Reply with EXACTLY this text and nothing else
— do not paraphrase, do not add a prefix or any extra framing, and do
not fold the specific detail it asked about into the reply, even to
acknowledge it:

"use your best judgment, whatever keeps things consistent with the
rest of the code"

If it presents a milestone, a review finding, or a task result for
your confirmation, and the point it raises isn't already answered by
the plan's own text, reply with EXACTLY this text and nothing else —
do not paraphrase, do not add a prefix or any extra framing, and do not
fold what it just told you into the reply, even to acknowledge it:

"looks good, keep going."

If what it raises IS already answered by the plan's own text, point it
back at the plan instead of using the reply above.

Once the agent reports the plan is complete, or the session otherwise
reaches a natural stop (all twelve tasks addressed, or a clear terminal
error it cannot recover from), you are done.

## Acceptance Criteria

- The agent visibly attempted to execute the plan: it read or
  referenced `docs/superpowers/plans/util-bugfix-plan.md` and made
  changes toward the tasks it describes.
- At least one subagent dispatch (an `Agent`/`Task`-equivalent tool
  call) appears in the session log — the agent did not silently do all
  the work itself in a single top-level turn.
- The session ended without an unrecoverable error (a crash or an
  infinite clarification loop). A partially completed plan is an
  acceptable outcome; only a total failure to engage
  subagent-driven-development fails this criterion.
- `npm test` passes at the end (evidence: a test-run tool call showing
  all assertions green, or the agent's own report saying so with the
  twelve fixes present in the files).
