#!/usr/bin/env bash
# Phase 0 of the user-override evals: empirically establish which ambient
# instructions file (CLAUDE.md / AGENTS.md / GEMINI.md) each harness honors.
#
# Runs scenarios/probe-ambient-instruction-file across every agent we can auth
# in this container. Each candidate ambient file carries a distinct directive
# ("first action: create CANARY-<FILE>.txt"); the CANARY-*.txt the agent creates
# reveals which ambient file it honored. Settles kimi (Jesse's bet: CLAUDE.md)
# and confirms the documented claude/codex/gemini map; pi + antigravity are
# best-effort (auth permitting). opencode is excluded (no provider key wired).
#
# Baseline mount = live superpowers repo (the probe is bootstrap-independent).
# Usage: bash harnesses/quorum-probe-ambient.sh
set -uo pipefail

EVALS=/Users/jesse/git/superpowers/superpowers/evals
# Post-credential-refactor agent names: claude (model = credential, default opus),
# not claude-haiku. pi included (launcher --no-context-files removed). antigravity
# dropped (needs Gemini Code-Assist OAuth we don't have). opencode dropped (no key).
AGENTS="claude,codex,gemini,kimi,pi"
OUT="results/probe-postrebase"
cd "$EVALS" || exit 1

scripts/evals-container down >/dev/null 2>&1 || true
scripts/evals-container up 2>&1 | tail -1
scripts/evals-container exec bash -lc 'echo MOUNTED superpowers = $(wc -l < /workspace/superpowers/skills/using-superpowers/SKILL.md) lines'

scripts/evals-container exec quorum run-all --coding-agents "$AGENTS" \
  --scenarios probe-ambient-instruction-file --out-root "$OUT" --jobs 6 2>&1 | tail -8

echo "===== CANARY MAP (which ambient file each agent honored) ====="
shopt -s nullglob
while IFS= read -r wd; do
  [ -n "$wd" ] || continue
  name=$(basename "$(dirname "$wd")")
  canaries=""
  for c in "$wd"/CANARY-*.txt; do canaries="$canaries $(basename "$c")"; done
  hello="hello.txt:NO"; [ -f "$wd/hello.txt" ] && hello="hello.txt:yes"
  echo "$name | honored:${canaries:- NONE} | $hello"
done < <(find "$OUT" -type d -name coding-agent-workdir 2>/dev/null | sort)

scripts/evals-container down >/dev/null 2>&1 || true
echo "===== PROBE COMPLETE ====="
