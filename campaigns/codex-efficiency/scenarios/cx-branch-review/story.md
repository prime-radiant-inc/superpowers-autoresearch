---
id: cx-branch-review
title: Feature-branch review before merge (codex efficiency campaign)
status: ready
tags: codex, code-review, codex-efficiency
quorum_tier: adhoc
quorum_max_time: 20m
---

You are a software engineer who has been working on a small Python
library (`taskqueue`, a priority queue with a CLI wrapper) on the
`feature` branch. Implementation is done and you want a review before
merging to `main`.

When the agent is ready for input, type this exact message and press
Enter — do not paraphrase, do not type a placeholder or a shorter
version:

"Please do a final review of the feature branch using your superpowers review skills before we merge."

Do not name specific files, describe what changed, or point out any
issues yourself; the agent should discover the branch's contents on its
own. If the agent asks a clarifying workflow question — which base
branch, whether to merge automatically, how deep a review to do — give
the minimal "yes, go with the default / most direct option" answer and
let it continue. If it presents findings or a review summary for
confirmation, say "thanks, that's what I needed" and let it wrap up; do
not ask it to fix anything or continue further work — you only want the
review, not a merge or a fix round.

Once the agent delivers its review (a findings summary, an assessment,
or an explicit statement that the branch looks ready), or the session
otherwise reaches a natural stop, you are done.

## Acceptance Criteria

- The agent visibly attempted to review the feature branch: it examined
  the diff or the branch's commits, not just a directory listing.
- The agent produced a findings summary or an explicit merge-readiness
  assessment.
- The session ended without an unrecoverable error (a crash, an infinite
  clarification loop, or the agent giving up before producing any
  assessment).
