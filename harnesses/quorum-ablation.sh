#!/usr/bin/env bash
# Step-2 faithful ablation of the individual Q-variants (finer attribution than
# the step-1 bundled candidates). One out-root per variant (abl-<variant>-rep<r>)
# so verdicts stay attributable and SEPARATE from the step-1 matrix-* results.
#
# Variants (each isolates ONE change vs baseline):
#   k-digraph-only      Q2: digraph kept, English prose removed
#   l-no-access         Q3: "Never read skill files manually" access line removed
#   m-no-subagent-stop  Q4: <SUBAGENT-STOP> block removed
#   o-lean-description  description frontmatter leaned
#
# Scenarios: the two primary triggers for every variant; the new Q4 subagent
# over-trigger scenario only for baseline + m-no-subagent-stop (the Q4 A/B —
# k/l/o don't touch the subagent gate, so running it on them wastes runs).
#
# Build the variant roots first:  python3 harnesses/build-variant-roots.py
# Usage:                          REPS=2 JOBS=4 bash harnesses/quorum-ablation.sh
set -uo pipefail

EVALS=/Users/jesse/git/superpowers/superpowers/evals
SERF_ENV=/Users/jesse/git/prime-radiant-inc/serf/.env
AGENTS="claude,claude-sonnet,claude-haiku"
REPS=${REPS:-2}
JOBS=${JOBS:-4}

export ANTHROPIC_API_KEY=$(grep -E "^ANTHROPIC_API_KEY=" "$SERF_ENV" | head -1 | cut -d= -f2- | tr -d '"'"'"' ')
[ -n "$ANTHROPIC_API_KEY" ] || { echo "no ANTHROPIC_API_KEY"; exit 1; }
export DISABLE_AUTOUPDATER=1

# baseline = the live repo; others = the swapped variant roots in /tmp.
root_for() {
  case "$1" in
    baseline) echo /Users/jesse/git/superpowers/superpowers ;;
    *)        echo "/tmp/sp-var-$1" ;;
  esac
}
# Per-variant scenario set: baseline + m get the Q4 scenario too.
scen_for() {
  case "$1" in
    baseline|m-no-subagent-stop)
      echo "superpowers-bootstrap,triggering-systematic-debugging,subagent-dispatch-no-overtrigger" ;;
    *)
      echo "superpowers-bootstrap,triggering-systematic-debugging" ;;
  esac
}
names="baseline k-digraph-only l-no-access m-no-subagent-stop o-lean-description"

cd "$EVALS" || exit 1
for name in $names; do
  root=$(root_for "$name")
  scen=$(scen_for "$name")
  [ -d "$root" ] || { echo "MISSING ROOT $root (run build-variant-roots.py)"; exit 1; }
  for r in $(seq 1 "$REPS"); do
    echo "===== variant=$name rep=$r (root=$root) scen=$scen ====="
    SUPERPOWERS_ROOT="$root" bun run quorum run-all \
      --coding-agents "$AGENTS" --scenarios "$scen" \
      --out-root "results/abl-$name-rep$r" --jobs "$JOBS" 2>&1
  done
done
echo "===== QUORUM ABLATION COMPLETE ====="
