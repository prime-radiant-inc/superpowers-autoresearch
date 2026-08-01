#!/usr/bin/env bash
# usage: run-quorum.sh ARM SCENARIO REPS [REP_START]   (ARM: control | cp/<arm>)
#
# Runs one cost-pathologies-campaign scenario through the evals-container
# quorum wrapper, REPS times, writing each rep to
# results/<SCENARIO>-<ARM>-repN (SCENARIO already carries its own 'cp-'
# prefix, e.g. cp-x1-buggy-sdd -- do not double it). REP_START (default 1)
# offsets the rep numbering, same convention as
# campaigns/codex-efficiency/run-quorum.sh (`run-quorum.sh control
# cp-x1-buggy-sdd 3 2` runs reps 2-4).
#
# KNOWN LIMITATION (inherited from the codex-efficiency script this is
# modeled on): `quorum run` exits 1 on a measured `fail` verdict and 2 on
# `indeterminate` -- NOT only on an infra crash. Because this script has
# `set -euo pipefail`, a single rep's ordinary non-pass verdict aborts the
# REMAINING reps in THIS invocation silently. Each already-completed rep's
# results dir/verdict.json is unaffected; a rep never reached is silently
# never run -- the caller must diff the requested rep range against what
# landed on disk and backfill with a separate REPS=1 call per missing rep.
#
# ARM SELECTION -- KNOWN GAP (Task 6, disclosed for Task 8+ to close). The
# cost-pathologies arm-manifest (campaigns/cost-pathologies/arm-manifest.md)
# defines 17 treatment branches (cp/x1a, cp/x2b, ...) as local branches in
# the superpowers checkout, cut from codex-efficiency-fixes @ 329b8f1. This
# script does NOT yet know how to materialize an arbitrary cp/<arm> branch
# into its own /tmp/cp-arm-<arm> worktree the way codex-efficiency's script
# resolves its four fixed arm names -- only 'control' is wired up here,
# pointing at a worktree the CALLER must have already created (e.g.
# `git -C /Users/jesse/git/superpowers/superpowers worktree add --detach
# /tmp/cp-arm-control 329b8f1`). The minimal generalization (resolve any
# 'cp/<arm>' ARM by materializing /tmp/cp-arm-<arm> on demand if the
# worktree doesn't already exist) is Task 8's job, not duplicated here --
# see campaigns/cost-pathologies/arm-manifest.md's "Runner integration gap"
# note for the fuller design constraint (each arm needs its own directory;
# JOBS>1 would race on a shared one).
#
# Env EVALS_ROOT overrides which evals checkout (lane) is used, same
# convention as codex-efficiency's script. Default:
# /Users/jesse/git/superpowers/superpowers/evals.
#
# Env CODING_AGENT (default codex) selects which Coding-Agent quorum
# drives. Env CREDENTIAL (unset by default) adds `--credential <name>`
# when set.
#
# This campaign's scenarios/ directories carry their OWN fixtures/
# subdirectory (unlike codex-efficiency's split top-level fixtures/ dir --
# simpler because none of these scenarios currently share a fixture across
# variants), so syncing a scenario is a single rsync of the whole
# directory. The synced-in copy is excluded via the evals checkout's
# .git/info/exclude -- it is never committed to superpowers-evals.
set -euo pipefail

EVALS=${EVALS_ROOT:-/Users/jesse/git/superpowers/superpowers/evals}
CAMP=/Users/jesse/git/superpowers/superpowers-autoresearch/campaigns/cost-pathologies
CODING_AGENT=${CODING_AGENT:-codex}
CREDENTIAL=${CREDENTIAL:-}

ARM=${1:?"usage: run-quorum.sh ARM SCENARIO REPS [REP_START]   (ARM: control | cp/<arm>)"}
SCEN=${2:?"usage: run-quorum.sh ARM SCENARIO REPS [REP_START]   (ARM: control | cp/<arm>)"}
REPS=${3:-1}
REP_START=${4:-1}

case "$ARM" in
  control) SP_ROOT=/tmp/cp-arm-control ;;
  *)
    echo "run-quorum.sh: unknown ARM '$ARM' (only 'control' is wired up -- see the ARM SELECTION comment at the top of this script)" >&2
    exit 1
    ;;
esac
[[ -d "$SP_ROOT" ]] || {
  echo "run-quorum.sh: arm worktree missing: $SP_ROOT" >&2
  echo "  create it first, e.g.:" >&2
  echo "  git -C /Users/jesse/git/superpowers/superpowers worktree add --detach $SP_ROOT 329b8f1" >&2
  exit 1
}
[[ -d "$CAMP/scenarios/$SCEN" ]] || {
  echo "run-quorum.sh: no such scenario: $CAMP/scenarios/$SCEN" >&2
  exit 1
}

cd "$EVALS"

# --- Sync the campaign's scenario (fixtures included -- see header note).
dest="scenarios/$SCEN"
rm -rf "$dest"
mkdir -p "$dest"
rsync -a "$CAMP/scenarios/$SCEN/" "$dest/"

# Never let the synced-in copy land in the evals checkout's own git history.
exclude_file=$(git rev-parse --git-path info/exclude)
mkdir -p "$(dirname "$exclude_file")"
grep -qxF "$dest" "$exclude_file" 2>/dev/null || echo "$dest" >> "$exclude_file"

# --- Arm selection: re-up the container mounting the chosen superpowers root.
scripts/evals-container down >/dev/null 2>&1 || true
scripts/evals-container --superpowers-root "$SP_ROOT" up

run_rep() {
  local r=$1
  echo "===== run-quorum: $ARM $SCEN rep$r ($CODING_AGENT) ====="
  if [[ -n "$CREDENTIAL" ]]; then
    scripts/evals-container exec quorum run "$dest" \
      --coding-agent "$CODING_AGENT" \
      --credential "$CREDENTIAL" \
      --out-root "results/$SCEN-$ARM-rep$r"
  else
    scripts/evals-container exec quorum run "$dest" \
      --coding-agent "$CODING_AGENT" \
      --out-root "results/$SCEN-$ARM-rep$r"
  fi
}

rep_last=$((REP_START + REPS - 1))
for r in $(seq "$REP_START" "$rep_last"); do
  run_rep "$r"
done
