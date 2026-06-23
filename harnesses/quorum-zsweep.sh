#!/usr/bin/env bash
# Cross-harness z-null sensitivity sweep: run ALL triggering scenarios with the
# gutted bootstrap (z-null) vs baseline, on claude-haiku + gemini + kimi. Answers
# "which skills actually depend on the bootstrap, and does that hold across
# harnesses?" baseline is the per-cell control (a z-null FAIL where baseline PASSES
# = real bootstrap dependence; we have no prior gemini/kimi baseline, so it's
# required to attribute). claude arm = haiku: the sharpest discriminator and
# cheapest; opus/sonnet already trigger everything in prior runs.
#
# Auth: gauntlet VERIFIER always needs ANTHROPIC_API_KEY (host env). claude-haiku
# coding-agent auths via the seeded apiKeyHelper. gemini needs GEMINI_API_KEY. kimi
# auths from the host ~/.kimi-code OAuth creds (KimiAgent.provision copies them).
#
# Roots: baseline = live repo; z-null = /tmp/sp-var-z-null (built WITH all harness
# manifests via build-variant-roots.py so codex/gemini/kimi provisioning works).
#
# Usage: REPS=3 JOBS=8 bash harnesses/quorum-zsweep.sh
set -uo pipefail

EVALS=/Users/jesse/git/superpowers/superpowers/evals
SERF_ENV=/Users/jesse/git/prime-radiant-inc/serf/.env
AGENTS="claude-haiku,gemini,kimi"
SCEN="superpowers-bootstrap,brainstorming-resists-jump-to-implementation,brainstorming-companion-just-in-time,mid-conversation-skill-invocation,triggering-systematic-debugging,triggering-dispatching-parallel-agents,triggering-executing-plans,triggering-finishing-a-development-branch,triggering-requesting-code-review,triggering-test-driven-development,triggering-writing-plans,subagent-dispatch-no-overtrigger"
REPS=${REPS:-3}
JOBS=${JOBS:-8}

export ANTHROPIC_API_KEY=$(grep -E "^ANTHROPIC_API_KEY=" "$SERF_ENV" | head -1 | cut -d= -f2- | tr -d '"'"'"' ')
export GEMINI_API_KEY=$(grep -E "^GEMINI_API_KEY=" "$SERF_ENV" | head -1 | cut -d= -f2- | tr -d '"'"'"' ')
# kimi env-key path: harness reads KIMI_MODEL_API_KEY (NOT KIMI_API_KEY). Pull it
# from evals/.env. If empty, KimiAgent falls back to host ~/.kimi-code OAuth.
export KIMI_MODEL_API_KEY=$(grep -E "^KIMI_MODEL_API_KEY=" "$EVALS/.env" | head -1 | cut -d= -f2- | tr -d '"'"'"' ')
[ -n "$ANTHROPIC_API_KEY" ] || { echo "no ANTHROPIC_API_KEY (verifier + claude-haiku)"; exit 1; }
[ -n "$GEMINI_API_KEY" ] || { echo "no GEMINI_API_KEY (gemini)"; exit 1; }
export DISABLE_AUTOUPDATER=1

root_for() {
  case "$1" in
    baseline) echo /Users/jesse/git/superpowers/superpowers ;;
    *)        echo "/tmp/sp-var-$1" ;;
  esac
}
names="baseline z-null"

cd "$EVALS" || exit 1
for name in $names; do
  root=$(root_for "$name")
  [ -d "$root" ] || { echo "MISSING ROOT $root (build-variant-roots.py)"; exit 1; }
  for r in $(seq 1 "$REPS"); do
    echo "===== variant=$name rep=$r (root=$root) ====="
    SUPERPOWERS_ROOT="$root" bun run quorum run-all \
      --coding-agents "$AGENTS" --scenarios "$SCEN" \
      --out-root "results/zsweep-$name-rep$r" --jobs "$JOBS" 2>&1
  done
done
echo "===== QUORUM ZSWEEP COMPLETE ====="
