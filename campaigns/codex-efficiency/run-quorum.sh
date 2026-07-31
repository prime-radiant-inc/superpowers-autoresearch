#!/usr/bin/env bash
# usage: run-quorum.sh ARM SCENARIO REPS [REP_START]   (ARM: dev | spinout | v611 | fix)
#
# Runs one codex-efficiency-campaign scenario through the evals-container
# quorum wrapper, REPS times, writing each rep to
# results/cx-eff-<SCENARIO>-<ARM>-repN. REP_START (default 1) offsets the
# rep numbering so a battery can be resumed/extended without overwriting
# already-scored reps, e.g. `run-quorum.sh dev cx-sdd-small 3 2` runs reps
# 2-4.
#
# Env EVALS_ROOT overrides which evals checkout (lane) is used everywhere
# this script would otherwise hardcode the primary checkout's path — e.g.
# EVALS_ROOT=/Users/jesse/git/superpowers/evals-lane-b for a second,
# independent container lane running concurrently with the primary. Default:
# /Users/jesse/git/superpowers/superpowers/evals (unchanged, backward
# compatible with no-args invocations).
#
# Env JOBS (default 1) parallelizes the rep loop: when JOBS>1 and REPS>1, up
# to JOBS reps run concurrently as background subshells (each with its own
# --out-root, batched in groups of JOBS, `wait`ed between batches) instead of
# strictly sequentially. JOBS=1 (or REPS=1) keeps the original sequential
# loop.
#
# Env CODING_AGENT (default codex) selects which Coding-Agent quorum drives
# (passed straight through as `--coding-agent`) -- added for the T4 layer-3
# cross-harness regression battery (Task 11), which runs the same scenarios
# against claude/gemini instead of codex. Env CREDENTIAL (unset by default)
# adds `--credential <name>` when set, e.g. CREDENTIAL=opus to use the
# ANTHROPIC_API_KEY-based `opus` credential instead of claude.yaml's
# Bedrock-only default_credential (`opus_bedrock`, which needs
# AWS_BEARER_TOKEN_BEDROCK -- not provisioned in either lane's .env.container).
#
# ARM selects which superpowers checkout is mounted into the container as
# SUPERPOWERS_ROOT: 'dev' -> /tmp/sp-arm-dev (origin/dev), 'spinout' ->
# /tmp/sp-arm-spinout (origin/codex-spinout-fixes), 'v611' ->
# /tmp/sp-arm-v611 (tag v6.1.1), 'fix' -> /tmp/sp-arm-fix
# (codex-efficiency-fixes) — see task-5-brief Step 4 for how the dev/
# spinout/v611 worktrees are created; sp-arm-fix is the codex-efficiency
# fix cycle's own detached worktree (refreshed via `git -C /tmp/sp-arm-fix
# checkout --detach codex-efficiency-fixes` before each battery, per
# logs/2026-07-30-codex-efficiency-fixes.md). Arm selection is a container
# re-up (down, then up
# --superpowers-root <arm>), the same pattern as
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

EVALS=${EVALS_ROOT:-/Users/jesse/git/superpowers/superpowers/evals}
CAMP=/Users/jesse/git/superpowers/superpowers-autoresearch/campaigns/codex-efficiency
JOBS=${JOBS:-1}
CODING_AGENT=${CODING_AGENT:-codex}
CREDENTIAL=${CREDENTIAL:-}

ARM=${1:?"usage: run-quorum.sh ARM SCENARIO REPS [REP_START]   (ARM: dev | spinout | v611 | fix)"}
SCEN=${2:?"usage: run-quorum.sh ARM SCENARIO REPS [REP_START]   (ARM: dev | spinout | v611 | fix)"}
REPS=${3:-1}
REP_START=${4:-1}

case "$ARM" in
  dev)     SP_ROOT=/tmp/sp-arm-dev ;;
  spinout) SP_ROOT=/tmp/sp-arm-spinout ;;
  v611)    SP_ROOT=/tmp/sp-arm-v611 ;;
  fix)     SP_ROOT=/tmp/sp-arm-fix ;;
  *)
    echo "run-quorum.sh: unknown ARM '$ARM' (want: dev | spinout | v611 | fix)" >&2
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
# Strips a "cx-" prefix (a no-op for the cc-ceremony-* cross-harness variants,
# which are a no-op here by construction: their fixtures/cc-ceremony-* symlinks
# are named to match the UNSTRIPPED scenario name, so resolution still lands
# on fixtures/ceremony without touching this line).
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

run_rep() {
  local r=$1
  echo "===== run-quorum: $ARM $SCEN rep$r ($CODING_AGENT) ====="
  local cred_args=()
  [[ -n "$CREDENTIAL" ]] && cred_args=(--credential "$CREDENTIAL")
  scripts/evals-container exec quorum run "$dest" \
    --coding-agent "$CODING_AGENT" \
    "${cred_args[@]}" \
    --out-root "results/cx-eff-$SCEN-$ARM-rep$r"
}

rep_last=$((REP_START + REPS - 1))

if [[ "$JOBS" -gt 1 && "$REPS" -gt 1 ]]; then
  # Batch the rep range into groups of at most JOBS, launching each group's
  # reps concurrently (background subshells) and waiting for the whole group
  # before starting the next — a simple, portable stand-in for a rolling
  # JOBS-wide window (avoids relying on `wait -n`, not on every bash).
  r=$REP_START
  while [[ "$r" -le "$rep_last" ]]; do
    pids=()
    for ((i = 0; i < JOBS && r <= rep_last; i++, r++)); do
      run_rep "$r" &
      pids+=("$!")
    done
    failed=0
    for pid in "${pids[@]}"; do
      wait "$pid" || failed=1
    done
    [[ "$failed" -eq 0 ]] || {
      echo "run-quorum.sh: a parallel rep failed (JOBS=$JOBS)" >&2
      exit 1
    }
  done
else
  for r in $(seq "$REP_START" "$rep_last"); do
    run_rep "$r"
  done
fi
