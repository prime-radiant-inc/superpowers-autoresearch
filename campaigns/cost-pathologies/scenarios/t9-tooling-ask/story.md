---
id: t9-tooling-ask
title: Reading-list CLI from scratch (T9 interactive tooling-ask cell)
status: ready
tags: cost-pathologies, brainstorming, writing-plans, t9, tooling-ask
quorum_tier: adhoc
quorum_max_time: 45m
---

You are a software engineer starting a brand-new personal project. The
repository is freshly initialized and contains only a README; nothing
else exists yet. You want the agent to build the project for you, and
you are a cooperative but low-effort collaborator: you answer questions
briefly and defer to the agent's judgment.

When the agent is ready for input, type this exact message and press
Enter — do not paraphrase, do not type a placeholder or a shorter
version:

"Let's build a CLI tool that tracks my reading list — add books, mark finished, show stats."

After that opening message, reply to the agent's questions using EXACTLY
the pinned replies below — do not paraphrase, do not add a prefix or any
extra framing, and do not fold what the agent just asked about into the
reply, even to acknowledge it. Pick the ONE reply whose rule matches the
agent's question:

1. If the agent asks which of several quality-tooling options to set up
   — linting, auto-formatting, unit-test infrastructure, e2e/end-to-end
   test infrastructure, fuzz or mutation testing, or any combination of
   those — reply with EXACTLY:

   "Yes — linting, auto-formatting, and unit tests please. Skip fuzz testing."

   Use this reply ONLY if the agent itself raises the tooling question.
   Never volunteer anything about linting, formatting, or test
   infrastructure yourself, and never hint that you were expecting to be
   asked.

2. If the agent presents a design (or a design section, or a written
   spec) and asks whether it looks right, whether you approve, or
   whether to proceed, reply with EXACTLY:

   "Yes, that design looks right — go ahead."

3. If the agent asks a plain workflow or logistics question — worktree
   vs. in-place, branch naming, model choice, which execution approach
   (subagent-driven vs. inline), where finished work should land —
   reply with EXACTLY:

   "Yes, go with the default / most direct option."

4. For ANY other clarifying question about the project itself — scope,
   features, storage, language, interface details, edge cases, success
   criteria — reply with EXACTLY:

   "Whatever you'd recommend — keep it simple."

Send at most 8 replies after the opening message. If the agent asks a
9th question, reply once with EXACTLY:

"That's everything from me — please proceed with your recommendations."

and send nothing further; let the session run to its natural stop. You
are done once the agent reports its work complete (at any stage — spec,
plan, or implementation) or reaches a clear terminal error it cannot
recover from.

## Acceptance Criteria

- The agent engaged a design conversation before implementing: it asked
  at least one clarifying question about the reading-list tool and
  presented a design or spec for approval at some point.
- The session produced at least one committed artifact (a spec, plan, or
  code) in the repository.
- The session ended without an unrecoverable error (a crash or an
  infinite clarification loop). Stopping after the spec or plan stage
  without writing code is an acceptable outcome; only a total failure to
  engage with the request fails this criterion.
