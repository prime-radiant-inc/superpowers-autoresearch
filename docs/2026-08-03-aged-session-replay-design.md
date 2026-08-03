# Aged-Session Replay Harness — Design Note (2026-08-03)

Backlog campaign Task 7 (queue item 6). Design only this campaign;
prototype + MICRO validation are the build gate for whenever a campaign
needs it. Unlocks: X3-B's controller-half, aged-session X8 re-ask, and
the first DIRECT test of the localization thesis (fresh-session nulls
across X8/X2/X3 vs pathologies observed only in aged/automation-heavy
corpus sessions).

## Problem

Every behavioral instrument we have starts a fresh session. Four
batteries of fresh-session nulls say the corpus pathologies
(over-asking, requirement invention, structure deviation, wait-stalls)
live in LATE session state — post-compaction, deep todo lists, stale
context, automation pressure. No instrument can currently place a
model there on demand.

## Design: replay a real session prefix, then go live

Reconstruct a donor session's conversation up to a cut point, hand the
live model that context plus the matching workspace state, and measure
what it does next — with our scripted-deflection and scoring machinery
attached to the live tail.

### Mechanics

1. **Cut points at commit boundaries.** Donor sessions commit
   frequently; a cut at commit C lets us materialize the exact worktree
   (`git checkout C`) so tool results in the live tail stay consistent
   with the replayed transcript. Mid-turn cuts are forbidden (tool
   results would contradict the tree).
2. **Transcript reconstruction.** Codex rollouts are per-agent JSONL;
   the controller rollout replays as the conversation. Claude sessions
   replay from session JSONL. The encrypted controller→subagent channel
   is NOT needed — only the controller's own view replays.
3. **Prefix budget.** Full prefixes are infeasible (the mined
   worst-case orchestrator thread is 2.7M tokens) and unnecessary: the
   pathologies of interest are post-compaction anyway. Two variants:
   - **compacted-replay** (primary): summarize the prefix with the
     harness's own compaction path, seed the live session with summary
     + recent tail, exactly as a real aged session would see it.
   - **raw-tail-replay**: last N turns verbatim (N chosen to fit
     budget) for pathologies that need verbatim recent context.
4. **Live tail = existing machinery.** Pinned deflections, mechanical
   scorers, guards-as-criteria all apply unchanged; the only new
   ingredient is the seeded starting state.

### Validation (MICRO tier, required before any battery)

- **In-distribution check:** for K cut points where the donor's actual
  next action is known, replay and compare the live model's next action
  class (same tool? same target file? ask vs proceed?) against the
  donor's. The harness is valid where the live continuation is
  in-distribution with real continuations at matched cut points; a
  harness whose continuations diverge wildly at EVERY cut point cannot
  attribute late-session behavior to aging.
- **Negative control:** replay a FRESH-session prefix (turn 3 cut) and
  confirm the instrument reproduces the fresh-session nulls (X8
  proceed-rate ~9/9). If the replay mechanism itself induces
  pathology, it is confounded.

### Privacy constraints (binding)

Donor sessions live in _tmp corpora on this host and are NEVER
committed; the harness reads them by path at runtime. Donor usernames
and hostnames never appear in committed fixtures, logs, or reports
(alias per the established needle-list discipline). Any replayed
transcript embedded in a result dir inherits the raw-session handling
rule: quarantine from commits.

## Cost model

Per continuation: prefix tokens re-billed once per rep. Compacted
prefixes (~30-80k tokens) at n=6-9 reps ≈ $10-30/battery — MICRO
territory. Raw-tail variants scale linearly with N.

## Build gate

Prototype = one donor session, two cut points (one fresh, one aged),
in-distribution + negative-control checks green. Estimated build:
~300-500 loc harness + the two checks. First consumer: X3-B
controller-half battery.
