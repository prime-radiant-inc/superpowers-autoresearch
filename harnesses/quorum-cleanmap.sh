#!/usr/bin/env bash
# Phase 1 of the full clean re-map (Docker-isolated): baseline + z-null across the
# triggering scenarios NOT yet tested clean, to find the TRUE clean load-bearing set.
# (systematic-debugging flipped mild->strong once the CLAUDE.md confound was removed,
# so the host map can't be trusted for the other scenarios.) Appends to the existing
# cclean-* out-roots (which already hold 5 scenarios), so quorum-report.py cclean sees
# the full grid. Phase 2 (compression candidates on the load-bearing cells) follows
# once this identifies them.
#
# Usage: bash harnesses/quorum-cleanmap.sh
set -uo pipefail

EVALS=/Users/jesse/git/superpowers/superpowers/evals
# the 8 triggering scenarios not in the first clean batch
SCEN="brainstorming-companion-just-in-time,mid-conversation-skill-invocation,subagent-dispatch-no-overtrigger,triggering-dispatching-parallel-agents,triggering-executing-plans,triggering-finishing-a-development-branch,triggering-test-driven-development,triggering-writing-plans"
cd "$EVALS" || exit 1

run_variant() {
  local name="$1"; shift
  for r in 1 2 3; do
    echo "===== $name rep$r ====="
    scripts/evals-container exec quorum run-all --coding-agents claude-haiku \
      --scenarios "$SCEN" --out-root "results/cclean-$name-rep$r" --jobs 6 2>&1 | tail -2
  done
}

# baseline = live repo (default superpowers-root)
scripts/evals-container down >/dev/null 2>&1 || true
scripts/evals-container up 2>&1 | tail -1
scripts/evals-container exec bash -lc 'echo MOUNTED baseline = $(wc -l < /workspace/superpowers/skills/using-superpowers/SKILL.md) lines'
run_variant baseline

# z-null
scripts/evals-container down >/dev/null 2>&1 || true
scripts/evals-container --superpowers-root /tmp/sp-var-z-null up 2>&1 | tail -1
scripts/evals-container exec bash -lc 'echo MOUNTED z-null = $(wc -l < /workspace/superpowers/skills/using-superpowers/SKILL.md) lines'
run_variant z-null

scripts/evals-container down >/dev/null 2>&1 || true
echo "===== CLEAN MAP PHASE 1 COMPLETE ====="
