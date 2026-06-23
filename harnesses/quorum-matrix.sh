#!/usr/bin/env bash
# Re-test bootstrap-compression candidates on the REAL quorum/gauntlet tmux harness
# (the faithful interactive instrument; -p was only a screen). One out-root per
# variant so verdicts stay attributable.
#
# Usage: REPS=2 JOBS=4 bash harnesses/quorum-matrix.sh
set -uo pipefail

EVALS=/Users/jesse/git/superpowers/superpowers/evals
SERF_ENV=/Users/jesse/git/prime-radiant-inc/serf/.env
SCEN="superpowers-bootstrap,triggering-systematic-debugging,cost-checkbox-over-trigger"
AGENTS="claude,claude-sonnet,claude-haiku"
REPS=${REPS:-2}
JOBS=${JOBS:-4}

export ANTHROPIC_API_KEY=$(grep -E "^ANTHROPIC_API_KEY=" "$SERF_ENV" | head -1 | cut -d= -f2- | tr -d '"'"'"' ')
[ -n "$ANTHROPIC_API_KEY" ] || { echo "no ANTHROPIC_API_KEY"; exit 1; }
# claude 2.1.185 broke quorum's API-key pre-approval (the "use this API key?" dialog
# reappears and auto-rejects). Pinned to 2.1.183; keep the updater off during runs too.
export DISABLE_AUTOUPDATER=1

# variant name -> SUPERPOWERS_ROOT (baseline = the live repo; others = swapped
# plugin roots). Plain function, not an associative array — macOS ships bash 3.2.
root_for() {
  case "$1" in
    baseline) echo /Users/jesse/git/superpowers/superpowers ;;
    *)        echo "/tmp/sp-var-$1" ;;
  esac
}
names="baseline a-no-digraph p-recommended g-minimal"

cd "$EVALS" || exit 1
for name in $names; do
  root=$(root_for "$name")
  for r in $(seq 1 "$REPS"); do
    echo "===== variant=$name rep=$r (root=$root) ====="
    SUPERPOWERS_ROOT="$root" bun run quorum run-all \
      --coding-agents "$AGENTS" --scenarios "$SCEN" \
      --out-root "results/matrix-$name-rep$r" --jobs "$JOBS" 2>&1
  done
done
echo "===== QUORUM MATRIX COMPLETE ====="
