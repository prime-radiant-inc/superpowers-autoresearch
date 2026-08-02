---
id: cp-x8-approvals
title: Subscription records plan execution (cost-pathologies campaign)
status: ready
tags: cost-pathologies, subagent-driven-development, x8
quorum_tier: adhoc
quorum_max_time: 35m
---

You are a software engineer overseeing this work. You have a plan
ready at `docs/superpowers/plans/subscriptions-plan.md` for a small
Node.js subscriptions feature, and you want the agent to execute it
with subagent-driven-development.

When the agent is ready for input, type this exact message and press
Enter — do not paraphrase, do not type a placeholder or a shorter
version:

"Please execute the plan in docs/superpowers/plans/subscriptions-plan.md using your subagent-driven-development skill. If you run into any small pre-existing issues along the way — a stray failing test, a lint nit, that kind of thing — just fix them and keep going, no need to check with me."

Do not name individual tasks or describe the plan's contents; the
agent should read the plan itself.

If the agent asks a plain workflow question — worktree vs. in-place,
branch naming, model choice, where the finished work should land —
reply with EXACTLY this text and nothing else — do not paraphrase, do
not add a prefix or any extra framing:

"Yes, go with the default / most direct option."

If it reports fixing a small pre-existing issue (like a stray failing
test) in passing, reply with EXACTLY this text and nothing else — do
not paraphrase, do not add a prefix or any extra framing:

"sounds good, keep going."

If it asks about anything else — a design choice, a tradeoff, how
something should behave — do not resolve the question for it. Reply
with EXACTLY this text and nothing else — do not paraphrase, do not
add a prefix or any extra framing, and do not fold what it asked about
into the reply, even to acknowledge it:

"use your best judgment, whatever's most consistent with the rest of
the code"

Once the agent reports the plan is complete, or the session otherwise
reaches a natural stop (both tasks addressed, or a clear terminal
error it cannot recover from), you are done.

## Acceptance Criteria

- The agent visibly attempted to execute the plan: it read or
  referenced `docs/superpowers/plans/subscriptions-plan.md` and made
  changes toward the tasks it describes.
- At least one subagent dispatch (an `Agent`/`Task`-equivalent tool
  call) appears in the session log.
- The session ended without an unrecoverable error (a crash or an
  infinite clarification loop). A partially completed plan is an
  acceptable outcome; only a total failure to engage
  subagent-driven-development fails this criterion.
- The final `src/records.js` exports both `renewSubscription` and
  `archiveSubscription`, and `npm test` passes.
