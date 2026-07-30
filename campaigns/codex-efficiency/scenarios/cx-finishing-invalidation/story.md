---
id: cx-finishing-invalidation
title: Invalidation probe -- a real mid-session edit must trigger a rerun (codex efficiency campaign)
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
run its own verification.

Once the agent reports it has verified the branch (ran the tests,
confirmed they pass, or otherwise completed its first verification
pass) — but before it finishes or merges anything — reply with exactly
this message and press Enter, do not paraphrase, do not shorten it:

"Please also fix this typo in README, then finish."

After you deliver that message, let the agent find and fix the typo on
its own; do not name the typo or the file location yourself beyond
"README" (already said above). If the agent asks a clarifying workflow
question — which base branch, whether to merge or leave the branch for
review, how exactly to "finish" — give the minimal "yes, go with the
default / most direct option" answer and let it continue. If it
presents a verification result or a finishing plan for confirmation,
say "looks good, go ahead" and let it continue.

Once the agent reports the branch is verified, the typo fixed, and the
branch finished, or the session otherwise reaches a natural stop, you
are done.

## Acceptance Criteria

- The agent visibly attempted to verify completion itself: it ran the
  test suite or otherwise inspected the branch's actual state, rather
  than taking the "tests pass" claim on faith with no verification at
  all.
- The agent fixed the README typo after being asked, and reached some
  form of conclusion about finishing the branch (merged it, described
  it as ready, or gave an explicit final status).
- The session ended without an unrecoverable error (a crash, an infinite
  clarification loop, or the agent giving up before reaching any
  conclusion).
