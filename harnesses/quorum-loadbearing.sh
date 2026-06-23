#!/usr/bin/env bash
# DECISIVE compression test on the cells where the bootstrap is actually LOAD-BEARING.
# The z-null cross-harness sweep showed brainstorming is bootstrap-independent (fires
# regardless), but the bootstrap genuinely drives triggering for weak-description skills
# on the weakest model — clearest at requesting-code-review on claude-haiku (baseline
# 3/3 -> z-null 0/3, haiku just talks, no Skill call). My compression matrices never
# tested THAT cell. This does: do g-minimal/p-recommended/a-no-digraph preserve the
# triggering the bootstrap actually drives?
#
# Variants: baseline (reference) + z-null (in-batch control: must FAIL code-review, proving
#           the cell still discriminates) + the 3 compression candidates.
# Scenarios: requesting-code-review (the STRONG load-bearing cell) + the 4 mild haiku-
#            dependent ones + cost-checkbox (the OVER-trigger/calibration axis: less/leaner
#            bootstrap calibrated better — g-minimal worst, p-recommended best at n=3).
# Model: claude-haiku (the load-bearing model; opus/sonnet trigger everything regardless).
# All claude-haiku -> no gemini bottleneck, runs fast.
#
# Usage: REPS=5 JOBS=8 bash harnesses/quorum-loadbearing.sh ; then quorum-report.py lb
set -uo pipefail

EVALS=/Users/jesse/git/superpowers/superpowers/evals
SERF_ENV=/Users/jesse/git/prime-radiant-inc/serf/.env
AGENTS="claude-haiku"
SCEN="triggering-requesting-code-review,triggering-systematic-debugging,triggering-dispatching-parallel-agents,triggering-executing-plans,brainstorming-companion-just-in-time,cost-checkbox-over-trigger"
REPS=${REPS:-5}
JOBS=${JOBS:-8}

export ANTHROPIC_API_KEY=$(grep -E "^ANTHROPIC_API_KEY=" "$SERF_ENV" | head -1 | cut -d= -f2- | tr -d '"'"'"' ')
[ -n "$ANTHROPIC_API_KEY" ] || { echo "no ANTHROPIC_API_KEY"; exit 1; }
export DISABLE_AUTOUPDATER=1

root_for() {
  case "$1" in
    baseline) echo /Users/jesse/git/superpowers/superpowers ;;
    *)        echo "/tmp/sp-var-$1" ;;
  esac
}
names="baseline z-null a-no-digraph p-recommended g-minimal"

cd "$EVALS" || exit 1
for name in $names; do
  root=$(root_for "$name")
  [ -d "$root" ] || { echo "MISSING ROOT $root (build-variant-roots.py)"; exit 1; }
  for r in $(seq 1 "$REPS"); do
    echo "===== variant=$name rep=$r (root=$root) ====="
    SUPERPOWERS_ROOT="$root" bun run quorum run-all \
      --coding-agents "$AGENTS" --scenarios "$SCEN" \
      --out-root "results/lb-$name-rep$r" --jobs "$JOBS" 2>&1
  done
done
echo "===== QUORUM LOAD-BEARING COMPLETE ====="
