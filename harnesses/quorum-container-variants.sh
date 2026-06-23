#!/usr/bin/env bash
# Clean (Docker-isolated) compression test on the now-confirmed load-bearing cells.
# The host runs were confounded by CLAUDE.md leakage; clean baseline-vs-z-null showed
# systematic-debugging is strongly bootstrap-dependent (3/3 -> 0/3) and requesting-code-
# review load-bearing (3/3 -> 1/3), while brainstorming self-triggers regardless. This
# re-tests the compression candidates clean. baseline + z-null already done (cclean-*);
# this adds the 3 candidates. Each variant = a container re-up with its root mounted at
# /workspace/superpowers (the container quorum wrapper hardcodes SUPERPOWERS_ROOT there).
#
# Usage: bash harnesses/quorum-container-variants.sh
set -uo pipefail

EVALS=/Users/jesse/git/superpowers/superpowers/evals
SCEN="superpowers-bootstrap,brainstorming-resists-jump-to-implementation,triggering-systematic-debugging,triggering-requesting-code-review,cost-checkbox-over-trigger"
cd "$EVALS" || exit 1

for v in a-no-digraph p-recommended g-minimal; do
  scripts/evals-container down >/dev/null 2>&1 || true
  scripts/evals-container --superpowers-root "/tmp/sp-var-$v" up 2>&1 | tail -1
  scripts/evals-container exec bash -lc "echo MOUNTED $v = \$(wc -l < /workspace/superpowers/skills/using-superpowers/SKILL.md) lines"
  for r in 1 2 3; do
    echo "===== $v rep$r ====="
    scripts/evals-container exec quorum run-all --coding-agents claude-haiku \
      --scenarios "$SCEN" --out-root "results/cclean-$v-rep$r" --jobs 6 2>&1 | tail -2
  done
done
scripts/evals-container down >/dev/null 2>&1 || true
echo "===== CLEAN COMPRESSION VARIANTS COMPLETE ====="
