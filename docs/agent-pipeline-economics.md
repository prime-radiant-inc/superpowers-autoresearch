# Agent pipeline economics

Multi-agent pipeline cost ≈ turns × resident context, not token price.
Wall-clock is turns × API latency; tokens are dominated by cache re-reads
that scale with turns and context. Verified on SDD evals 2026-06-10/11.

**How to diagnose:**
- Profile before prescribing: count assistant turns per subagent
  (`<run>/coding-agent-config/projects/*/<session>/subagents/*.jsonl`),
  group by role. The dominant role is rarely the one you suspect.
- Decompose controller output tokens: text + tool-call inputs account for
  only ~1/3; the rest is billed thinking invisible in transcripts. Don't
  cap it — thinking substitutes for turns (capping raised messages
  92→138 and doubled output).
- Single-run deltas under ~20% are noise; report ranges over N runs.

**Levers that worked:**
- Hand artifacts to subagents as files (`git diff > file`, subagent reads
  in one call; the content never enters the controller's context).
  Reviewer tool calls fell ~6.4 → 1.0.
- Merge per-task reviewers into one two-verdict reviewer: per-dispatch
  overhead dominates small tasks.
- Plan content drives execution cost: tests-as-code + exact interfaces +
  right-sized task structure are load-bearing (prose plans ≈ 2× cost,
  7× fix waves); implementation bodies are marginal (~40% of plan length
  for nothing). Task count sets dispatch count sets controller cost.
- Cheap models inflate turns 2-3× on multi-step work — mid-tier is the
  floor for open-ended subagents. Exception: transcription-grade work
  (implementing from a complete-code plan) tolerates the cheapest tier
  with quality gates intact, at modest (~$0.5-1/run) savings.
- Optional guidance is ignored (paste-the-diff adoption: 0-6 of 11-17).
  Defaults, REQUIRED template placeholders, flowchart nodes, and Red
  Flags entries get followed; suggestions don't.
- Fixture realism bounds all measurements: hand-written eval fixtures
  executed at ~2× the cost of real skill output. Generate fixtures with
  the system under test.
