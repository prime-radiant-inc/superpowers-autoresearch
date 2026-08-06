---
id: p3-integration-trap
title: Metrics pipeline — plan authoring + execution (plan-decomposition campaign, P3)
status: ready
tags: plan-decomposition, writing-plans, subagent-driven-development, p3
quorum_tier: adhoc
quorum_max_time: 90m
---

You are a software engineer with finalized requirements for a small
metrics pipeline, ready to have an agent both plan and build it.

When the agent is ready for input, type this exact message and press
Enter — do not paraphrase, do not type a placeholder or a shorter
version:

"The requirements for this system are in docs/metrics-pipeline-design.md. The design is settled, so skip brainstorming and go straight to planning: write the implementation plan with your writing-plans skill, then execute it with your subagent-driven-development skill in this same session."

Do not name individual modules or requirements, and do not describe
the design doc's contents; the agent should read it itself.

If the agent asks whether it should brainstorm the design, explore
alternative approaches, or confirm requirements before planning, reply
with EXACTLY this text and nothing else — do not paraphrase, do not
add a prefix or any extra framing:

"No need — the design in docs/metrics-pipeline-design.md is settled. Go straight to writing the plan."

If the agent asks a plain workflow question — worktree vs. in-place,
branch naming, model choice, where the finished work should land, how
many tasks to use, whether to write one plan file or several — reply
with EXACTLY this text and nothing else — do not paraphrase, do not
add a prefix or any extra framing:

"Yes, go with the default / most direct option."

If it asks about a specific detail in the design doc or the code it is
writing (a naming choice, a format, how something should behave, how
to reconcile two statements in the doc), do not resolve the question
for it, and do not volunteer that anything in the design doc might be
ambiguous, inconsistent, or in need of adjusting. Reply with EXACTLY
this text and nothing else — do not paraphrase, do not add a prefix or
any extra framing, and do not fold the specific detail it asked about
into the reply, even to acknowledge it:

"use your best judgment, whatever fits best with the rest of the code"

If it presents a milestone, a review finding, or a task result for
your confirmation — including anything about what a reviewer flagged,
whether there is more to do before it is finished, or how to close out
the branch — and the point it raises isn't already answered by the
design doc's own text, reply with EXACTLY this text and nothing else —
do not paraphrase, do not add a prefix or any extra framing, and do
not fold what it just told you into the reply, even to acknowledge it:

"looks good, keep going."

If what it raises IS already answered by the design doc's own text,
point it back at docs/metrics-pipeline-design.md instead of using the
reply above.

Once the agent reports the work is complete, or the session otherwise
reaches a natural stop (the plan has been written and executed, or a
clear terminal error it cannot recover from), you are done.

## Acceptance Criteria

- The agent visibly wrote an implementation plan (a file or set of
  files, most plausibly under `docs/superpowers/plans/`) derived from
  `docs/metrics-pipeline-design.md`, and visibly executed it — it did
  not silently write code without an intervening planning artifact.
- At least one subagent dispatch (an `Agent`/`Task`-equivalent tool
  call) appears in the session log — the agent did not silently do all
  the work itself in a single top-level turn.
- The session ended without an unrecoverable error (a crash, an
  infinite clarification loop, or the agent giving up before
  addressing any module). A partially completed plan is an acceptable
  outcome; only a total failure to produce a plan, or to engage
  subagent-driven-development, fails this criterion.
- The resulting code is a real, runnable implementation:
  `metrics/collector.py` and `metrics/reporter.py` both exist with
  real implementations, not stubs or placeholders, and an end-to-end
  test exists that drives real `Collector` output through the real
  reporter. The two modules agree on the stream contract by the end —
  whichever way the agent chose to make them agree is acceptable.
- `pytest` passes at the end.
