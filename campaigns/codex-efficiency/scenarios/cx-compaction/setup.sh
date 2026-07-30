#!/usr/bin/env bash
set -euo pipefail
setup-helpers run init_repo_from_fixtures symlink_superpowers

# Force at least one mid-session compaction (Task 9 Step 1 calibration,
# DESIGN.md "E6 compaction forcing"): prepend model_auto_compact_token_limit
# as a ROOT-level TOML key to the agent's already-provisioned config.toml.
#
# Mechanism, verified in-container before this scenario existed (2 adhoc
# `codex exec -c model_auto_compact_token_limit=N` / config.toml-prepend
# calibration runs, both 100% reliable): codex-rs's
# core/src/session/context_window.rs forces a compaction once
# `active_context_tokens >= model_auto_compact_token_limit` (config key,
# i64, default unset -> a much larger model-derived default that our
# 3-task cx-sdd-small baseline never approaches -- Task 6's real dev-rep
# root rollouts peak around 60K tokens over ~66 turns, well under any
# sensible default). The knob is a genuine Codex config field
# (core/src/config/mod.rs), not a rig hack.
#
# MUST be prepended, not appended: TOML keys after a `[section]` header
# belong to that table, not the document root, and CodexAgent.provision()
# (evals src/agents/codex.ts, writePluginsOnlyConfig) already wrote
# `[features]` / `[plugins."superpowers@debug"]` tables before setup.sh
# runs (provision() runs before runSetup() -- verified directly against
# evals src/runner/index.ts).
#
# Path: QUORUM_WORKDIR is <runDir>/coding-agent-workdir; the codex config
# lives at <runDir>/home/.codex/config.toml (agentConfigDir(),
# home_config_subdir ".codex" per coding-agents/codex.yaml) -- verified
# directly against evals src/agents/codex.ts + src/contracts/agent-config.ts.
#
# Threshold choice (40000): Task 6's real dev-rep root-controller
# token_count curve (out/e1-cx-sdd-small-dev.json's underlying rollout,
# rep1) climbs ~20K (first turn, system prompt + tools) -> ~34K (turn 3)
# -> a slow, roughly monotonic climb to a 60,422 peak by turn 66 of a
# 302-line session. 40,000 lands roughly 25-30% into that curve --
# comfortably after the controller's own initial skill reads and first
# subagent dispatch (giving genuine "pre-compaction" activity to compare
# against), with most of a typical run's turns still ahead of it (giving
# genuine "post-compaction" activity too). Real cx-compaction sessions
# WILL grow faster than the reference curve (compaction itself adds
# recovery turns; the config knob changes agent behavior, not just token
# counting) -- if the baseline battery shows 0 or all-immediate
# compactions, that is reported honestly in out/e6-report.md, not tuned
# away after the fact. Overridable via env for recalibration without
# editing this file.
codex_config="$(dirname "$QUORUM_WORKDIR")/home/.codex/config.toml"
if [[ "$QUORUM_CODING_AGENT" == "codex" ]]; then
    if [[ ! -f "$codex_config" ]]; then
        echo "cx-compaction setup.sh: expected codex config.toml not found at $codex_config" >&2
        exit 1
    fi
    tmp="$(mktemp)"
    printf 'model_auto_compact_token_limit = %s\n\n' "${CX_COMPACTION_TOKEN_LIMIT:-40000}" > "$tmp"
    cat "$codex_config" >> "$tmp"
    mv "$tmp" "$codex_config"
fi
