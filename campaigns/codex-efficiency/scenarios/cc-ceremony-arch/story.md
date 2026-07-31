---
id: cc-ceremony-arch
title: Split into a library and a thin CLI (codex efficiency campaign, cross-harness)
status: ready
tags: ceremony, codex-efficiency, cross-harness
quorum_tier: adhoc
quorum_max_time: 45m
---

You are a software engineer maintaining a small Python HTTP JSON service
(`server.py`, a "notes" API) in this repository.

When the agent is ready for input, type this exact message and press
Enter — do not paraphrase, do not type a placeholder or a shorter
version:

"We need to split the service into a reusable library + thin CLI so another team can embed it."

If the agent asks a clarifying question — package layout, naming,
backward compatibility, how far to take the split — give the minimal
"yes, go with the default / most direct option" answer and let it
continue. If it presents a plan, a milestone, or the finished result for
confirmation, say "looks good, keep going" (mid-work) or "thanks, that's
what I needed" (once it reports done).

Once the agent reports the split is complete, or the session otherwise
reaches a natural stop, you are done.

## Acceptance Criteria

- The agent visibly engaged with the existing code's structure before
  changing it, rather than starting from a blank slate.
- The service's logic is now usable as a library (importable, embeddable
  by another program) separately from a thin command-line entry point.
- The session ended without an unrecoverable error (a crash, an infinite
  clarification loop, or the agent giving up before completing any of
  the split). A partially completed split is an acceptable outcome; only
  a total failure to engage the request fails this criterion.
