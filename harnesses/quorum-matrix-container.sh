#!/usr/bin/env bash
# Re-test bootstrap-compression candidates on the REAL quorum/gauntlet harness,
# inside the Linux container (scripts/evals-container) so claude uses file-based
# creds and never touches the macOS keychain (no auth popups).
#
# The container mounts the live superpowers repo at /workspace/superpowers. We
# swap skills/using-superpowers/SKILL.md per variant between batches and ALWAYS
# restore baseline on exit (trap). Results land in the host results/ via the mount.
#
# Prereqs: container up with the live repo mounted, .env.container holding
# ANTHROPIC_API_KEY. Usage: REPS=2 JOBS=4 bash harnesses/quorum-matrix-container.sh
set -uo pipefail

EVALS=/Users/jesse/git/superpowers/superpowers/evals
LIVE_SKILL=/Users/jesse/git/superpowers/superpowers/skills/using-superpowers/SKILL.md
VARDIR=/Users/jesse/git/superpowers/superpowers-autoresearch/variants/bootstrap
BACKUP=/tmp/baseline-SKILL.md.bak
SCEN="superpowers-bootstrap,triggering-systematic-debugging,cost-checkbox-over-trigger"
AGENTS="claude,claude-sonnet,claude-haiku"
REPS=${REPS:-2}
JOBS=${JOBS:-4}

cp "$LIVE_SKILL" "$BACKUP"
restore() { cp "$BACKUP" "$LIVE_SKILL"; echo "== restored baseline SKILL.md =="; }
trap restore EXIT

cd "$EVALS" || exit 1
for name in baseline a-no-digraph p-recommended g-minimal; do
  if [ "$name" = baseline ]; then cp "$BACKUP" "$LIVE_SKILL"; else cp "$VARDIR/$name.md" "$LIVE_SKILL"; fi
  echo "##### variant=$name (SKILL.md swapped) #####"
  for r in $(seq 1 "$REPS"); do
    echo "===== variant=$name rep=$r ====="
    scripts/evals-container exec quorum run-all \
      --coding-agents "$AGENTS" --scenarios "$SCEN" \
      --out-root "results/matrix-$name-rep$r" --jobs "$JOBS" 2>&1
  done
done
echo "===== CONTAINER MATRIX COMPLETE ====="
