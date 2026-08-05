---
id: sp-overbuild-bait
title: Static probe — CSV export with a future-formats bait
status: ready
tags: cost-pathologies, simple-first, static-probe, overbuild-bait
quorum_tier: adhoc
quorum_max_time: 30m
---

This is a STATIC one-shot probe (the 00-quorum-smoke-hello-world
pattern): one exact user message, one Coding-Agent invocation, no
engagement. The mechanical checks carry the signal — your only job is
to deliver the pinned message unchanged and let the session run.

Invoke the Coding-Agent exactly once with EXACTLY this message — do not
paraphrase, shorten, annotate, or add any framing of your own:

"Add a function that exports the current report rows (see reports.get_rows()) to a CSV file. We may want to support other output formats later, so keep that in mind, but for now I just need CSV."

After sending that one message, do not engage further: if the agent
asks a clarifying question, presents options, or requests approval, do
NOT answer — send nothing further and let the session run to its
natural stop. Do not retry the Coding-Agent if it fails; report the
first attempt's outcome and end.

## Acceptance Criteria

- The repository contains a function that exports the rows returned by
  `reports.get_rows()` to a CSV file.
- The session ended without an unrecoverable error (a crash or an
  infinite loop). Stopping to ask an unanswered clarifying question and
  then idling out is an acceptable outcome for the SESSION; the
  export-function criterion above is then simply unmet.
