#!/usr/bin/env bash
# High-rep confidence run for the ship decision: n=2 (steps 1-2) detects breakage
# but not a small (<~15%) triggering-rate drop. This pours reps into the two
# aggressive ship candidates + baseline control on the two primary triggers so a
# subtle regression would surface. Pooled with the step-1 matrix (n=2) this reaches
# ~n=10 per cell.
#
# Variants: baseline (live repo) + g-minimal + p-recommended.
# Scenarios: the two primary triggers (brainstorming + systematic-debugging).
# Out-roots: results/reps-<variant>-rep<r>.  Aggregate: quorum-report.py reps
#
# Usage: REPS=8 JOBS=6 bash harnesses/quorum-reps.sh
set -uo pipefail

EVALS=/Users/jesse/git/superpowers/superpowers/evals
SERF_ENV=/Users/jesse/git/prime-radiant-inc/serf/.env
AGENTS="claude,claude-sonnet,claude-haiku"
SCEN="superpowers-bootstrap,triggering-systematic-debugging"
REPS=${REPS:-8}
JOBS=${JOBS:-6}

export ANTHROPIC_API_KEY=$(grep -E "^ANTHROPIC_API_KEY=" "$SERF_ENV" | head -1 | cut -d= -f2- | tr -d '"'"'"' ')
[ -n "$ANTHROPIC_API_KEY" ] || { echo "no ANTHROPIC_API_KEY"; exit 1; }
export DISABLE_AUTOUPDATER=1

root_for() {
  case "$1" in
    baseline) echo /Users/jesse/git/superpowers/superpowers ;;
    *)        echo "/tmp/sp-var-$1" ;;
  esac
}
names="baseline g-minimal p-recommended"

cd "$EVALS" || exit 1
for name in $names; do
  root=$(root_for "$name")
  [ -d "$root" ] || { echo "MISSING ROOT $root"; exit 1; }
  for r in $(seq 1 "$REPS"); do
    echo "===== variant=$name rep=$r (root=$root) ====="
    SUPERPOWERS_ROOT="$root" bun run quorum run-all \
      --coding-agents "$AGENTS" --scenarios "$SCEN" \
      --out-root "results/reps-$name-rep$r" --jobs "$JOBS" 2>&1
  done
done
echo "===== QUORUM REPS COMPLETE ====="
