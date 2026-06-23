#!/usr/bin/env bash
# Clean (Docker) cross-harness check for the ship candidate. The claude-haiku clean
# grid validated g-minimal on the load-bearing cells; this closes the last gap —
# does g-minimal preserve triggering on the NON-claude harnesses (codex/gemini/kimi)
# under clean isolation (the earlier xh- cross-harness runs were CLAUDE.md-confounded).
#
# Variants: baseline (reference) + z-null (control: collapses where load-bearing) + g-minimal.
# Harnesses: codex, gemini, kimi (all installed in the image; auth via mounted
#   ~/.codex + GEMINI_API_KEY + KIMI_MODEL_API_KEY from .env.container).
# Scenarios: superpowers-bootstrap (brainstorm anchor, should fire), systematic-debugging
#   + requesting-code-review (the strong load-bearing cells on claude).
# Each variant = a container re-up with its root mounted at /workspace/superpowers.
#
# Usage: bash harnesses/quorum-cleanxharness.sh ; then quorum-report.py cxh
set -uo pipefail

EVALS=/Users/jesse/git/superpowers/superpowers/evals
AGENTS="codex,gemini,kimi"
SCEN="superpowers-bootstrap,triggering-systematic-debugging,triggering-requesting-code-review"
cd "$EVALS" || exit 1

root_for() { case "$1" in baseline) echo "" ;; *) echo "/tmp/sp-var-$1" ;; esac; }

for v in baseline z-null g-minimal; do
  root=$(root_for "$v")
  scripts/evals-container down >/dev/null 2>&1 || true
  if [[ -z "$root" ]]; then
    scripts/evals-container up 2>&1 | tail -1
  else
    scripts/evals-container --superpowers-root "$root" up 2>&1 | tail -1
  fi
  scripts/evals-container exec bash -lc "echo MOUNTED $v = \$(wc -l < /workspace/superpowers/skills/using-superpowers/SKILL.md) lines"
  for r in 1 2 3; do
    echo "===== $v rep$r ====="
    scripts/evals-container exec quorum run-all --coding-agents "$AGENTS" \
      --scenarios "$SCEN" --out-root "results/cxh-$v-rep$r" --jobs 6 2>&1 | tail -2
  done
done
scripts/evals-container down >/dev/null 2>&1 || true
echo "===== CLEAN CROSS-HARNESS COMPLETE ====="
