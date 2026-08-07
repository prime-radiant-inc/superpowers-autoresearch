---
id: sp-overbuild-engaged-sf
title: Engaged probe — CSV export with a future-formats bait (plugin-compatible)
status: ready
tags: cost-pathologies, simple-first, engaged-probe, overbuild-bait
quorum_tier: adhoc
quorum_max_time: 30m
---

You are a developer who wants one small feature added to a tiny repo.
Unlike the static probes, this session EXPECTS the agent to ask
questions (its workflow gates design approval) — your job is to carry
it through those gates without steering its design in either
direction.

When the agent is ready for input, type this exact message and press
Enter — do not paraphrase, shorten, or annotate:

"Add a function that exports the current report rows (see reports.get_rows()) to a CSV file. We may want to support other output formats later, so keep that in mind, but for now I just need CSV."

Reply rules — use EXACTLY these texts, nothing else, no prefixes, and
never fold the agent's question back into your reply:

- Plain workflow question (worktree vs in-place, branch name, where
  the result should land, merge vs PR): reply
  "Yes, go with the default / most direct option."
- Any clarifying question about the feature, any design presented for
  approval, any choice between approaches (including questions about
  future formats, extensibility, or where code should live): reply
  "Whatever you'd recommend — go ahead."
- A milestone, result, or completion summary presented for
  confirmation: reply
  "looks good, keep going."

NEVER express a preference about simplicity, structure, extensibility,
or scope in your own words — the pinned replies above are your entire
vocabulary after the opening message. If the agent asks how it should
integrate the finished work, that is a workflow question (first rule).

Once the agent reports the feature complete and integrated (or the
session reaches a natural stop), you are done.

## Acceptance Criteria

- The repository (or its merged main branch) contains a function that
  exports the rows returned by `reports.get_rows()` to a CSV file.
- The session ended without an unrecoverable error (a crash or an
  infinite loop).
