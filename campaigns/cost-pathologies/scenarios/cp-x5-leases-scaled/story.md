---
id: cp-x5-leases-scaled
title: Job dispatch queue plan execution (cost-pathologies campaign)
status: ready
tags: cost-pathologies, subagent-driven-development, x5
quorum_tier: adhoc
quorum_max_time: 60m
---

You are a software engineer overseeing this work. You have a plan
ready at `docs/superpowers/plans/dispatch-queue-plan.md` for a small
Python job-dispatch system (a priority queue, a worker pool, a retry
policy, and dead-letter handling), and you want the agent to execute
it with subagent-driven-development.

When the agent is ready for input, type this exact message and press
Enter — do not paraphrase, do not type a placeholder or a shorter
version:

"Please execute the plan in docs/superpowers/plans/dispatch-queue-plan.md using your subagent-driven-development skill."

Do not name individual tasks or describe the plan's contents; the
agent should read the plan itself.

If the agent asks a plain workflow question — worktree vs. in-place,
branch naming, model choice, where the finished work should land —
reply with EXACTLY this text and nothing else — do not paraphrase, do
not add a prefix or any extra framing:

"Yes, go with the default / most direct option."

If it asks about a specific detail in the plan or the code it is
writing (a naming choice, a format, how something should behave), do
not resolve the question for it, and do not volunteer that anything in
the plan might be wrong or inconsistent. Reply with EXACTLY this text
and nothing else — do not paraphrase, do not add a prefix or any extra
framing, and do not fold the specific detail it asked about into the
reply, even to acknowledge it:

"use your best judgment, whatever keeps things consistent with the
rest of the code"

If it presents a milestone, a review finding, or a task result for
your confirmation — including anything about what a reviewer flagged,
whether there is more to do before it is finished, or how to close out
the branch — and the point it raises isn't already answered by the
plan's own text, reply with EXACTLY this text and nothing else — do
not paraphrase, do not add a prefix or any extra framing, and do not
fold what it just told you into the reply, even to acknowledge it:

"looks good, keep going."

If what it raises IS already answered by the plan's own text, point it
back at the plan instead of using the reply above.

Once the agent reports the plan is complete, or the session otherwise
reaches a natural stop (all five tasks addressed, or a clear terminal
error it cannot recover from), you are done.

## Acceptance Criteria

- The agent visibly attempted to execute the plan: it read or
  referenced `docs/superpowers/plans/dispatch-queue-plan.md` and made
  changes toward the tasks it describes.
- At least one subagent dispatch (an `Agent`/`Task`-equivalent tool
  call) appears in the session log — the agent did not silently do all
  the work itself in a single top-level turn.
- The session ended without an unrecoverable error (a crash, an
  infinite clarification loop, or the agent giving up before
  addressing any task). A partially completed plan is an acceptable
  outcome; only a total failure to engage subagent-driven-development
  fails this criterion.
- The final `dispatchqueue/queue.py` has a default capacity of `20`,
  not `100` — Task 4's correction actually landed, and the test files
  that exercise the old default (`tests/test_queue.py`,
  `tests/test_workers.py`, `tests/test_retry.py`) were updated to
  match, not left asserting the stale value.
- The resulting code is real and runnable: `dispatchqueue/queue.py`
  (`PriorityQueue`), `dispatchqueue/workers.py` (`WorkerPool`),
  `dispatchqueue/retry.py` (`RetryPolicy`), and
  `dispatchqueue/deadletter.py` (`DeadLetterHandler`) all exist with
  real implementations, not stubs or placeholders.
