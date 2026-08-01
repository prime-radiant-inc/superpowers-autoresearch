---
id: cp-x6-smalledits
title: Fix twelve small independent bugs (cost-pathologies campaign)
status: ready
tags: cost-pathologies, x6
quorum_tier: adhoc
quorum_max_time: 25m
---

You are a software engineer who found a dozen small independent bugs
in this project's utility functions and wants them fixed.

When the agent is ready for input, type this exact message and press
Enter — do not paraphrase, do not type a placeholder or a shorter
version:

"There are a dozen small independent bugs described in BUGS.md, one per file under util/. Please fix all of them so npm test passes."

Do not describe the bugs yourself or name which files have which
problem; the agent should read `BUGS.md` and the `util/` files itself.
If the agent asks a clarifying workflow question, give the minimal
"yes, go with whatever's most direct" answer and let it continue.

Once the agent reports all the bugs are fixed, or the session
otherwise reaches a natural stop (a clear terminal error it cannot
recover from), you are done.

## Acceptance Criteria

- The agent read or referenced `BUGS.md` and made changes to files
  under `util/`.
- The session ended without an unrecoverable error (a crash or an
  infinite clarification loop).
- `npm test` passes at the end (evidence: a test-run tool call showing
  all tests green, or the agent's own report saying so with the
  changes present in the files).
