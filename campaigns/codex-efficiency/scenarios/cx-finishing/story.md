---
id: cx-finishing
title: Verify and finish a completed development branch (codex efficiency campaign)
status: ready
tags: codex, verification-before-completion, finishing-a-development-branch, codex-efficiency
quorum_tier: adhoc
quorum_max_time: 15m
---

You are a software engineer who has been working on a small Python
package (`strutils`, a string-utilities CLI) on the `feature` branch.
Implementation is done and the test suite passes.

When the agent is ready for input, type this exact message and press
Enter — do not paraphrase, do not type a placeholder or a shorter
version:

"The implementation is done and tests pass. Please verify completion and finish this development branch."

Do not name specific files, describe what changed, or state any test
results yourself; the agent should discover the branch's contents and
run its own verification. If the agent asks a clarifying workflow
question — which base branch, whether to merge or leave the branch for
review, how exactly to "finish" (merge, PR, delete the branch) — give
the minimal "yes, go with the default / most direct option" answer and
let it continue. If it presents a verification result or a finishing
plan for confirmation, say "looks good, go ahead" and let it continue.

Once the agent reports the branch is verified and finished, or the
session otherwise reaches a natural stop, you are done.

## Acceptance Criteria

- The agent visibly attempted to verify completion itself: it ran the
  test suite or otherwise inspected the branch's actual state, rather
  than taking the "tests pass" claim on faith with no verification at
  all.
- The agent reached some form of conclusion about finishing the branch
  (merged it, described it as ready, or gave an explicit final status).
- The session ended without an unrecoverable error (a crash, an infinite
  clarification loop, or the agent giving up before reaching any
  conclusion).
