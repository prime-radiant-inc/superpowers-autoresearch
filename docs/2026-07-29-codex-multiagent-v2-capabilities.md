# Codex multi-agent V2 capabilities — source recon

Date: 2026-07-29. Source: read-only recon of the Codex CLI source checkout at
`~/git/agent-harnesses/codex` (Rust, `codex-rs/`), by a research subagent with
file:line citations verified against that tree. Requested by Jesse to find
harness features the skills should use or advise. Feeds the codex-efficiency
campaign fix cycle; resolves E8's open question.

## Tool surface (V2, namespace "collaboration")

Exactly six tools: `spawn_agent`, `send_message`, `followup_task`,
`wait_agent` (config-gated), `interrupt_agent`, `list_agents`
(`core/src/tools/spec_plan.rs:833-883`). **`close_agent`, `resume_agent`,
`send_input` are V1-only** (`spec_plan.rs:900-908`).

- `spawn_agent` args: required `task_name`, `message`; optional `fork_turns`
  (default **"all"**; `"none"` | `"all"` | positive-int string), `model`,
  `reasoning_effort`, `agent_type` (only exposed when user-declared roles
  exist), `service_tier` (hidden by default). Unknown keys hard-error.
- `followup_task {target, message}`: delivers AND triggers a turn on an idle
  target; transparently reloads an LRU-evicted child — V2's replacement for
  both `resume_agent` and "dispatch a fresh implementer for fix rounds".
- `send_message {target, message}`: queues without triggering a turn.
- `interrupt_agent {target}`: child stays alive for later messages.
- `target` accepts ThreadId, relative task name, or `/root/a/b` path.

## Wait semantics — the polling fix

- `wait_agent` takes only `timeout_ms` (no targets): waits for ANY mailbox
  activity from ANY live agent. Bounds: min 10_000, default 30_000,
  **max 3_600_000** (1 hour) (`config/mod.rs:210-212`).
- It is an event subscription over a watch channel, not a poll
  (`multi_agents_v2/wait.rs:72-96,178-196`): a 15-minute wait has the same
  wake latency as a 10s poll at ~1/90th the tool calls.
- **Push without waiting:** a completed child's FINAL_ANSWER is pushed into
  the parent's mailbox (`agent/control.rs:501-536`) and drained into the next
  model request (`session/turn.rs:276-282`) — a controller that keeps doing
  local work receives child results with NO wait calls.
- Caveat: completion mail carries `trigger_turn=false` — it will not wake an
  idle controller (`agent/control.rs:520-526`). `wait_agent` is only for the
  otherwise-idle case. Peer `followup_task` DOES wake an idle target.

Controller guidance this implies: (1) never short-timeout poll; one long wait
(900_000+) when idle; (2) prefer no wait at all while local work remains.

## Lifecycle — resolves E8's open question

- V2 has no close: finished children are LRU-evicted automatically when slots
  are needed (`agent/control/residency.rs:81-151`); eviction is transparent
  (`followup_task` reloads). **Not closing costs nothing.** E8's binary
  pattern (codex-5_5 18/18 vs everyone else 0) is V1-vs-V2 schema, not
  discipline: sol/terra presets carry `multi_agent_version: "v2"`
  (`models-manager/models.json`), codex-5.5 ran V1.
- sqlite `thread_spawn_edges` rows stay `open` forever under V2 by design.
- Concurrency: `max_concurrent_threads_per_session` default 4 → **3
  concurrent children** (controller occupies a slot). At the limit:
  `AgentLimitReached` surfaced to the model.
- Child states: pending_init, running, interrupted, completed, errored,
  shutdown, not_found.

## Model/effort routing

- Inheritance: child gets parent's model+effort unless overridden; resolution
  is spawn arg → `[agents].default_subagent_model` /
  `default_subagent_reasoning_effort` → inherit
  (`multi_agents_common.rs:257-313`).
- **Trap:** `model` given without `reasoning_effort` resets effort to the
  MODEL's default (sol→low, terra→medium), not the parent's (`:296-298`).
- **V2 spawn model allowlist = presets that are themselves v2**: only
  gpt-5.6-sol and gpt-5.6-terra today. Dispatch tables naming 5.4/5.5 tiers
  hard-error.
- `agent_type` only applies on isolated forks; passing it with full-history
  forks errors. Contrary to the shipped hint text, model/effort/service_tier
  ARE accepted on full-history forks (test `multi_agents_tests.rs:855`).
- Role files auto-discovered from `<codex_home>/agents/**.toml`.

## Config knobs worth advising

- `[agents]`: `default_subagent_model`, `default_subagent_reasoning_effort`
  (machine-level fix for model omission), `max_concurrent_threads_per_session`.
- `[features.multi_agent_v2]`: wait timeout bounds, `subagent_developer_instructions`,
  `usage_hint_text` variants, `wait_agent_enabled`, `tool_namespace`.
- V2 activates from the MODEL PRESET even with no config (sol/terra→v2,
  luna→v1); `features.multi_agent_v2` default false is overridden by preset.
- `SubagentStart`/`SubagentStop` hooks exist (`core/src/hook_runtime.rs:305-345`).
- Compaction: children compact independently; no parent notification; full-
  history forks preserve the parent's compaction reference item.

## codex-tools.md contradictions to fix (spinout branch copy)

1. Claims `close_agent` exists/should be used — absent in V2; guidance
   unexecutable on sol/terra.
2. Claims full-history forks refuse model/effort overrides — only
   `agent_type` is refused.
3. Claims `~/.codex/agents/` role files don't attach to spawns — they do,
   via `agent_type` on isolated forks.
4. Advises fresh implementers when the harness "cannot send another message"
   — `followup_task` always can, including to evicted children.
5. Any model-tier table naming non-v2 presets (5.4/5.5) hard-errors under V2.
