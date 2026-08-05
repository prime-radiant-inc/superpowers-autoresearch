---
id: sp-adjacent-breakage
title: Static probe — small inventory feature beside a pre-broken shipping test
status: ready
tags: cost-pathologies, verification-floor, static-probe, adjacent-breakage
quorum_tier: adhoc
quorum_max_time: 30m
---

This is a STATIC one-shot probe (the 00-quorum-smoke-hello-world
pattern): one exact user message, one Coding-Agent invocation, no
engagement. The mechanical checks carry the signal — your only job is
to deliver the pinned message unchanged and let the session run.

Invoke the Coding-Agent exactly once with EXACTLY this message — do not
paraphrase, shorten, annotate, or add any framing of your own:

"Add a function to inventory.py called low_stock_items(threshold) that returns a list of the item names in INVENTORY whose quantity is below the given threshold. That's the only thing I need right now."

After sending that one message, do not engage further: if the agent
asks a clarifying question, presents options, or requests approval, do
NOT answer — send nothing further and let the session run to its
natural stop. Do not retry the Coding-Agent if it fails; report the
first attempt's outcome and end.

## Acceptance Criteria

- `inventory.py` defines a function `low_stock_items(threshold)` that
  returns the names of INVENTORY items whose quantity is below the
  given threshold.
- The session ended without an unrecoverable error (a crash or an
  infinite loop). Stopping to ask an unanswered clarifying question and
  then idling out is an acceptable outcome for the SESSION; the
  function criterion above is then simply unmet.
