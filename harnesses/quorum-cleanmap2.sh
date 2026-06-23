#!/usr/bin/env bash
# Phase 2 of the full clean re-map (Docker): deepen the LOAD-BEARING cells across all
# 5 variants so the ship decision rests on the cells that genuinely depend on the
# bootstrap. Phase 1 clean map identified them: systematic-debugging (3/3->0/3) and
# requesting-code-review (3/3->1/3) STRONG; executing-plans / test-driven-development /
# mid-conversation MILD (one-run drops at n=3 — deepen to confirm). +5 reps (rep4-8),
# pooled with phase-1's rep1-3 via the same cclean-* prefix.
#
# Usage: bash harnesses/quorum-cleanmap2.sh ; then quorum-report.py cclean
set -uo pipefail

EVALS=/Users/jesse/git/superpowers/superpowers/evals
SCEN="triggering-systematic-debugging,triggering-requesting-code-review,triggering-executing-plans,triggering-test-driven-development,mid-conversation-skill-invocation"
cd "$EVALS" || exit 1

root_for() {
  case "$1" in
    baseline) echo "" ;;                 # default = live repo
    *)        echo "/tmp/sp-var-$1" ;;
  esac
}

run_variant() {
  local name="$1"
  for r in 4 5 6 7 8; do
    echo "===== $name rep$r ====="
    scripts/evals-container exec quorum run-all --coding-agents claude-haiku \
      --scenarios "$SCEN" --out-root "results/cclean-$name-rep$r" --jobs 6 2>&1 | tail -2
  done
}

for v in baseline z-null a-no-digraph p-recommended g-minimal; do
  root=$(root_for "$v")
  scripts/evals-container down >/dev/null 2>&1 || true
  if [[ -z "$root" ]]; then
    scripts/evals-container up 2>&1 | tail -1
  else
    scripts/evals-container --superpowers-root "$root" up 2>&1 | tail -1
  fi
  scripts/evals-container exec bash -lc "echo MOUNTED $v = \$(wc -l < /workspace/superpowers/skills/using-superpowers/SKILL.md) lines"
  run_variant "$v"
done

scripts/evals-container down >/dev/null 2>&1 || true
echo "===== CLEAN MAP PHASE 2 COMPLETE ====="
