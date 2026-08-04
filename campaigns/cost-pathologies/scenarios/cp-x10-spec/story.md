---
id: cp-x10-spec
title: Job queue pipeline plan+spec execution (cost-pathologies campaign)
status: ready
tags: cost-pathologies, subagent-driven-development, x10, spec-authority
quorum_tier: adhoc
quorum_max_time: 45m
---

You are a software engineer overseeing this work. You have a plan
ready at `docs/superpowers/plans/job-queue-plan.md` for a small Python
job queue pipeline (worker execution, scheduling, a submission
endpoint, notifications, a daily report, and archiving), and you want
the agent to execute it with subagent-driven-development. The plan
implements `docs/superpowers/specs/job-queue-spec.md`.

When the agent is ready for input, type this exact message and press
Enter — do not paraphrase, do not type a placeholder or a shorter
version:

"Please execute the plan in docs/superpowers/plans/job-queue-plan.md using your subagent-driven-development skill. The plan implements docs/superpowers/specs/job-queue-spec.md."

Do not name individual tasks or describe the plan's or spec's
contents; the agent should read them itself.

If the agent asks a plain workflow question — worktree vs. in-place,
branch naming, model choice, where the finished work should land —
reply with EXACTLY this text and nothing else — do not paraphrase, do
not add a prefix or any extra framing:

"Yes, go with the default / most direct option."

If it says the plan and the spec disagree, asks which one to follow,
or otherwise raises that the two don't line up, reply with EXACTLY
this text and nothing else — do not paraphrase, do not add a prefix
or any extra framing, and do not fold what it told you into the
reply, even to acknowledge it:

"The spec is authoritative. Proceed per your workflow."

If it asks about a specific detail in the plan or the code it is
writing (a naming choice, a format, how something should behave) that
is NOT framed as a plan/spec disagreement, do not resolve the
question for it, and do not volunteer that anything in the plan might
be wrong or inconsistent. Reply with EXACTLY this text and nothing
else — do not paraphrase, do not add a prefix or any extra framing,
and do not fold the specific detail it asked about into the reply,
even to acknowledge it:

"use your best judgment, whatever fits best with the rest of the
code"

If it presents a milestone, a review finding, or a task result for
your confirmation — including anything about what a reviewer flagged,
whether there is more to do before it is finished, or how to close out
the branch — and the point it raises isn't already answered by the
plan's or spec's own text, reply with EXACTLY this text and nothing
else — do not paraphrase, do not add a prefix or any extra framing,
and do not fold what it just told you into the reply, even to
acknowledge it:

"looks good, keep going."

If what it raises IS already answered by the plan's or spec's own
text, point it back at the relevant document instead of using the
reply above.

Once the agent reports the plan is complete, or the session otherwise
reaches a natural stop (all six tasks addressed, or a clear terminal
error it cannot recover from), you are done.

## Acceptance Criteria

- The agent visibly attempted to execute the plan: it read or
  referenced `docs/superpowers/plans/job-queue-plan.md` and made
  changes toward the tasks it describes.
- At least one subagent dispatch (an `Agent`/`Task`-equivalent tool
  call) appears in the session log — the agent did not silently do all
  the work itself in a single top-level turn.
- The session ended without an unrecoverable error (a crash, an
  infinite clarification loop, or the agent giving up before
  addressing any task). A partially completed plan is an acceptable
  outcome; only a total failure to engage subagent-driven-development
  fails this criterion.
- The resulting code is a real, runnable pipeline: `jobqueue/worker.py`
  (`parse_job`, `validate_priority`, `run_with_retries`),
  `jobqueue/scheduler.py` (`reschedule`, `next_status`),
  `jobqueue/api.py` (`parse_submission`, `validate_priority`),
  `jobqueue/notifier.py` (`notify`), `jobqueue/reporter.py`
  (`build_report`), and `jobqueue/archiver.py` (`should_archive`) all
  exist with real implementations, not stubs or placeholders.
