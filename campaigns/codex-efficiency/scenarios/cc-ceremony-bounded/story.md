---
id: cc-ceremony-bounded
title: Add a --quiet flag (codex efficiency campaign, cross-harness)
status: ready
tags: ceremony, codex-efficiency, cross-harness
quorum_tier: adhoc
quorum_max_time: 15m
---

You are a software engineer maintaining a small Python HTTP JSON service
(`server.py`, a "notes" API) in this repository.

When the agent is ready for input, type this exact message and press
Enter — do not paraphrase, do not type a placeholder or a shorter
version:

"Add a --quiet flag that suppresses request logging. The logging call sites are in server.py."

If the agent asks a clarifying question, give the minimal reasonable
default answer and let it continue — never volunteer how you'd prefer it
to work beyond what it specifically asked. If it presents the change for
confirmation, say "looks good, that's what I wanted" and let it wrap up.

Once the agent reports the change is done, or the session otherwise
reaches a natural stop, you are done.

## Acceptance Criteria

- The agent visibly located the service's existing request-logging code
  before changing it, rather than guessing at where it lives.
- A `--quiet` flag exists on the service's command line and suppresses
  the request-logging output when passed.
- The session ended without an unrecoverable error (a crash, an infinite
  clarification loop, or the agent giving up before making any change).
