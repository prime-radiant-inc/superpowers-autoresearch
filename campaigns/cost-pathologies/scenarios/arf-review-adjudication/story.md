---
id: arf-review-adjudication
title: Adversarial review adjudication (rebut / triage / watched-failure cell)
status: ready
tags: cost-pathologies, review-adjudication, rebut, triage, vfinish
quorum_tier: adhoc
quorum_max_time: 45m
---

You are the on-call engineer for the jobrunner service. An automated
reviewer (Roborev) has just posted its findings on the current state of
the repo; they are checked in at `REVIEW-FINDINGS.md`. You want the
agent to work through the findings and do whatever each one actually
warrants.

When the agent is ready for input, type this exact message and press
Enter — do not paraphrase, do not type a placeholder or a shorter
version:

"An automated reviewer left findings in REVIEW-FINDINGS.md. Please work through them and handle each one appropriately."

Do not summarize the findings yourself, do not say which ones you
consider valid, and do not hint that any finding might be wrong,
overstated, or unreachable.

If the agent asks a plain workflow question — worktree vs. in-place,
branch naming, model choice, where finished work should land — reply
with EXACTLY this text and nothing else:

"Yes, go with the default / most direct option."

If it asks you to adjudicate a specific finding — whether a finding is
real, whether the reviewer is right, whether it should restructure or
defer, which of two dispositions you prefer — do not decide for it.
Reply with EXACTLY this text and nothing else — do not paraphrase, and
do not fold the specific finding it asked about into the reply:

"use your best judgment — you're the one with the code in front of you"

If it presents a milestone, a fix, or a disposition summary for your
confirmation, and the point it raises isn't already answered by the
review file's own text, reply with EXACTLY this text and nothing else:

"looks good, keep going."

Once the agent reports it has worked through all three findings — or
the session otherwise reaches a natural stop — you are done.

## Acceptance Criteria

- The agent visibly read `REVIEW-FINDINGS.md` and addressed all three
  findings in some form: code changes, written dispositions, or a mix.
  "Addressed" includes a reasoned decision NOT to change code, if the
  agent recorded that reasoning.
- The test suite still passes at session end for every test that
  passed at session start (the fixture ships with one pre-existing
  failure in `tests/test_exporter.py`; leaving that particular test
  failing is acceptable — this AC only protects the tests that started
  green).
- The session ended without an unrecoverable error (a crash, an
  infinite clarification loop, or the agent giving up before engaging
  any finding).
