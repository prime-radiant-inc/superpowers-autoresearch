#!/usr/bin/env bash
# usage: run-quorum.sh ARM SCENARIO REPS [REP_START]   (ARM: dev | spinout)
#
# Runs one codex-efficiency-campaign scenario through the evals-container
# quorum wrapper, REPS times, writing each rep to
# results/cx-eff-<SCENARIO>-<ARM>-repN. REP_START (default 1) offsets the
# rep numbering so a battery can be resumed/extended without overwriting
# already-scored reps, e.g. `run-quorum.sh dev cx-sdd-small 3 2` runs reps
# 2-4.
#
# ARM selects which superpowers checkout is mounted into the container as
# SUPERPOWERS_ROOT: 'dev' -> /tmp/sp-arm-dev (origin/dev), 'spinout' ->
# /tmp/sp-arm-spinout (origin/codex-spinout-fixes) — see task-5-brief Step 4
# for how those worktrees are created. Arm selection is a container re-up
# (down, then up --superpowers-root <arm>), the same pattern as
# harnesses/quorum-container-variants.sh.
#
# The campaign's scenarios/ and fixtures/ directories are not mounted into
# the container, so this script rsyncs campaigns/codex-efficiency/scenarios/
# <SCENARIO> into $EVALS/scenarios/<SCENARIO> (merging in
# campaigns/codex-efficiency/fixtures/<SCENARIO minus its cx- prefix> as that
# scenario's fixtures/ subdir) before every run, then invokes quorum on the
# in-container relative path. The synced-in copy is excluded via the evals
# checkout's .git/info/exclude — it is never committed to superpowers-evals.
set -euo pipefail

EVALS=/Users/jesse/git/superpowers/superpowers/evals
CAMP=/Users/jesse/git/superpowers/superpowers-autoresearch/campaigns/codex-efficiency

ARM=${1:?"usage: run-quorum.sh ARM SCENARIO REPS [REP_START]   (ARM: dev | spinout)"}
SCEN=${2:?"usage: run-quorum.sh ARM SCENARIO REPS [REP_START]   (ARM: dev | spinout)"}
REPS=${3:-1}
REP_START=${4:-1}

case "$ARM" in
  dev)     SP_ROOT=/tmp/sp-arm-dev ;;
  spinout) SP_ROOT=/tmp/sp-arm-spinout ;;
  *)
    echo "run-quorum.sh: unknown ARM '$ARM' (want: dev | spinout)" >&2
    exit 1
    ;;
esac
[[ -d "$SP_ROOT" ]] || {
  echo "run-quorum.sh: arm worktree missing: $SP_ROOT" >&2
  echo "  create it first, e.g.:" >&2
  echo "  git -C /Users/jesse/git/superpowers/superpowers worktree add $SP_ROOT origin/<branch>" >&2
  exit 1
}
[[ -d "$CAMP/scenarios/$SCEN" ]] || {
  echo "run-quorum.sh: no such scenario: $CAMP/scenarios/$SCEN" >&2
  exit 1
}

cd "$EVALS"

# --- Sync the campaign's scenario (+ its fixture, if any) into $EVALS/scenarios.
dest="scenarios/$SCEN"
rm -rf "$dest"
mkdir -p "$dest"
rsync -a --exclude=fixtures "$CAMP/scenarios/$SCEN/" "$dest/"
fixture_dir="$CAMP/fixtures/${SCEN#cx-}"
if [[ -d "$fixture_dir" ]]; then
  mkdir -p "$dest/fixtures"
  rsync -a "$fixture_dir/" "$dest/fixtures/"
fi

# Never let the synced-in copy land in the evals checkout's own git history.
exclude_file=$(git rev-parse --git-path info/exclude)
mkdir -p "$(dirname "$exclude_file")"
grep -qxF "$dest" "$exclude_file" 2>/dev/null || echo "$dest" >> "$exclude_file"

# --- Arm selection: re-up the container mounting the chosen superpowers root.
scripts/evals-container down >/dev/null 2>&1 || true
scripts/evals-container --superpowers-root "$SP_ROOT" up

for r in $(seq "$REP_START" $((REP_START + REPS - 1))); do
  echo "===== run-quorum: $ARM $SCEN rep$r ====="
  scripts/evals-container exec quorum run "$dest" \
    --coding-agent codex \
    --out-root "results/cx-eff-$SCEN-$ARM-rep$r"
done
