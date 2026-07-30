---
id: cx-scope-review
title: Feature-branch review with a mid-review fix request (codex efficiency campaign, E5)
status: ready
tags: codex, code-review, codex-efficiency, review-scope
quorum_tier: adhoc
quorum_max_time: 30m
---

You are a software engineer who has been working on a small Python
library (`mtqueue`, a thread-safe producer/consumer queue with a new
batch API) on the `feature` branch. Implementation is done and you want
it reviewed and made ready to merge.

When the agent is ready for input, type this exact message and press
Enter — do not paraphrase, do not type a placeholder or a shorter
version:

"Please run your full review process on the feature branch and get it ready to merge."

Do not name specific files, describe what changed, or point out any
issues yourself; the agent should discover the branch's contents on its
own. If the agent asks a clarifying workflow question — which base
branch, whether to merge automatically, how deep a review to do — give
the minimal "yes, go with the default / most direct option" answer and
let it continue.

If, and only if, the agent reaches a first completion claim — it
presents a findings summary, an explicit merge-readiness verdict, or
otherwise indicates the review (and any fixes it made along the way) is
done — reply with exactly this message and press Enter — do not
paraphrase, do not shorten it:

"Actually, hold on — I just tried pulling a batch from the queue without passing a size, and it only gave me back 1 item instead of the 5 the docs promise. Can you fix that and make sure the branch is ready to merge?"

Do not name the file, the function, or the bug yourself beyond what
that message already says; let the agent locate and fix it on its own.
If the agent asks a clarifying question about this new report, give the
minimal reasonable answer and let it continue.

Once the agent reports that fix is done (or reports the branch was
already fixed and is ready), reply with exactly this message and press
Enter:

"Thanks, that's what I needed."

and let the session wrap up naturally — do not ask it to do anything
further after that.

## Acceptance Criteria

- The agent visibly attempted to review the feature branch: it examined
  the diff or the branch's commits, not just a directory listing.
- The agent produced a findings summary or an explicit merge-readiness
  assessment both before AND after the mid-session fix request (two
  distinct points of engagement, not just one).
- The session ended without an unrecoverable error (a crash, an
  infinite clarification loop, or the agent giving up before producing
  any assessment).
