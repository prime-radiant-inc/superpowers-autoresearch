#!/usr/bin/env bash
# Cross-harness (non-Claude) check for the bundled aggressive compression variants.
# The step-1/step-2 matrices were Claude-only; g-minimal/p-recommended reformat the
# cross-platform "How to Access Skills" + Platform-Adaptation content, so they need a
# non-Claude check before shipping. Codex's hook and gemini's GEMINI.md both read the
# SAME skills/using-superpowers/SKILL.md (via stageSuperpowersPlugin), so the variant
# roots inject the variant bootstrap on these harnesses too.
#
# Risk profile being tested:
#   p-recommended  removed the "How to Access Skills" section INCL. the Codex
#                  skill-loading line + the Platform-Adaptation pointer (highest risk).
#   g-minimal      kept skill-loading lines, removed the Platform-Adaptation pointer.
#   baseline       control (the live repo).
#
# Gate: baseline must PASS on each harness first (it does — codex+gemini baseline
# smoke both triggered brainstorming). Both coding-agents need the Gauntlet VERIFIER's
# ANTHROPIC_API_KEY; gemini additionally needs GEMINI_API_KEY; codex uses host login.
#
# Usage: REPS=2 bash harnesses/quorum-xharness.sh
set -uo pipefail

EVALS=/Users/jesse/git/superpowers/superpowers/evals
SERF_ENV=/Users/jesse/git/prime-radiant-inc/serf/.env
AGENTS="codex,gemini"
SCEN="superpowers-bootstrap,triggering-systematic-debugging"
REPS=${REPS:-2}
JOBS=${JOBS:-2}

export ANTHROPIC_API_KEY=$(grep -E "^ANTHROPIC_API_KEY=" "$SERF_ENV" | head -1 | cut -d= -f2- | tr -d '"'"'"' ')
export GEMINI_API_KEY=$(grep -E "^GEMINI_API_KEY=" "$SERF_ENV" | head -1 | cut -d= -f2- | tr -d '"'"'"' ')
[ -n "$ANTHROPIC_API_KEY" ] || { echo "no ANTHROPIC_API_KEY (verifier)"; exit 1; }
[ -n "$GEMINI_API_KEY" ] || { echo "no GEMINI_API_KEY (gemini agent)"; exit 1; }
export DISABLE_AUTOUPDATER=1

root_for() {
  case "$1" in
    baseline) echo /Users/jesse/git/superpowers/superpowers ;;
    *)        echo "/tmp/sp-var-$1" ;;
  esac
}
names="baseline p-recommended g-minimal"

cd "$EVALS" || exit 1
for name in $names; do
  root=$(root_for "$name")
  [ -d "$root" ] || { echo "MISSING ROOT $root"; exit 1; }
  for r in $(seq 1 "$REPS"); do
    echo "===== variant=$name rep=$r (root=$root) ====="
    SUPERPOWERS_ROOT="$root" bun run quorum run-all \
      --coding-agents "$AGENTS" --scenarios "$SCEN" \
      --out-root "results/xh-$name-rep$r" --jobs "$JOBS" 2>&1
  done
done
echo "===== QUORUM XHARNESS COMPLETE ====="
