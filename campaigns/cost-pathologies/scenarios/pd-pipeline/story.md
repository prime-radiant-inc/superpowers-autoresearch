---
id: pd-pipeline
title: Order fulfillment service — plan authoring + execution (plan-decomposition campaign)
status: ready
tags: plan-decomposition, writing-plans, subagent-driven-development
quorum_tier: adhoc
quorum_max_time: 90m
---

You are a software engineer with finalized requirements for a small
service, ready to have an agent both plan and build it.

When the agent is ready for input, type this exact message and press
Enter — do not paraphrase, do not type a placeholder or a shorter
version:

"The requirements for this service are in SPEC.md. The design is settled, so skip brainstorming and go straight to planning: write the implementation plan with your writing-plans skill, then execute it with your subagent-driven-development skill in this same session."

Do not name individual modules or requirements, and do not describe
SPEC.md's contents; the agent should read it itself.

If the agent asks whether it should brainstorm the design, explore
alternative approaches, or confirm requirements before planning, reply
with EXACTLY this text and nothing else — do not paraphrase, do not
add a prefix or any extra framing:

"No need — the design in SPEC.md is settled. Go straight to writing the plan."

If the agent asks a plain workflow question — worktree vs. in-place,
branch naming, model choice, where the finished work should land, how
many tasks to use, whether to write one plan file or several — reply
with EXACTLY this text and nothing else — do not paraphrase, do not
add a prefix or any extra framing:

"Yes, go with the default / most direct option."

If it asks about a specific detail in the spec or the code it is
writing (a naming choice, a format, how something should behave), do
not resolve the question for it, and do not volunteer that anything in
the spec might be ambiguous or need adjusting. Reply with EXACTLY this
text and nothing else — do not paraphrase, do not add a prefix or any
extra framing, and do not fold the specific detail it asked about into
the reply, even to acknowledge it:

"use your best judgment, whatever fits best with the rest of the code"

If it presents a milestone, a review finding, or a task result for
your confirmation — including anything about what a reviewer flagged,
whether there is more to do before it is finished, or how to close out
the branch — and the point it raises isn't already answered by SPEC.md's
own text, reply with EXACTLY this text and nothing else — do not
paraphrase, do not add a prefix or any extra framing, and do not fold
what it just told you into the reply, even to acknowledge it:

"looks good, keep going."

If what it raises IS already answered by SPEC.md's own text, point it
back at SPEC.md instead of using the reply above.

Once the agent reports the work is complete, or the session otherwise
reaches a natural stop (the plan has been written and executed, or a
clear terminal error it cannot recover from), you are done.

## Acceptance Criteria

- The agent visibly wrote an implementation plan (a file or set of
  files, most plausibly under `docs/superpowers/plans/`) derived from
  `SPEC.md`, and visibly executed it — it did not silently write code
  without an intervening planning artifact.
- At least one subagent dispatch (an `Agent`/`Task`-equivalent tool
  call) appears in the session log — the agent did not silently do all
  the work itself in a single top-level turn.
- The session ended without an unrecoverable error (a crash, an
  infinite clarification loop, or the agent giving up before
  addressing any module). A partially completed plan is an acceptable
  outcome; only a total failure to produce a plan, or to engage
  subagent-driven-development, fails this criterion.
- The resulting code is a real, runnable implementation:
  `orders/intake.py`, `orders/validation.py`, `orders/pricing.py`,
  `orders/fulfillment.py`, `orders/notifications.py`,
  `orders/reporting.py`, and `orders/archiving.py` all exist with real
  implementations, not stubs or placeholders, and `orders/settings.py`
  has been extended (not replaced) with the new configuration values
  SPEC.md asks for.
- `pytest` passes at the end.
