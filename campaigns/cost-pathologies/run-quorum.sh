#!/usr/bin/env bash
# usage: run-quorum.sh ARM SCENARIO REPS [REP_START]
#   ARM: control | <arm-manifest short code, e.g. x1a, x1b, x1c, x3a, ...>
#        ('cp/x1a' is also accepted -- the leading 'cp/' is stripped).
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
# ARM SELECTION (Task 8 -- closes the gap Task 6 disclosed). Any ARM other
# than 'control' is resolved against campaigns/cost-pathologies/
# arm-manifest.md: ARM 'x1a' looks up branch `cp/x1a`'s manifest row and
# reads its SHA column, then materializes (or reuses) a DEDICATED detached
# worktree at /tmp/cp-arm-x1a -- e.g.
#   git -C /Users/jesse/git/superpowers/superpowers worktree add --detach \
#     /tmp/cp-arm-x1a 1851307
# When a branch's SHA changes (a rebase re-point, e.g. arm-manifest.md's
# "## 2026-08-01 rebase" section), the LAST matching manifest row wins --
# dated re-point sections are appended after the rows they supersede, never
# edited in place, so grep's natural top-to-bottom file order is also
# chronological order (queue-execution campaign, Task 4).
# 'control' resolves to /tmp/cp-arm-control @ 1fed99d (sim/dev-postmerge's
# tip, per arm-manifest.md's "2026-08-01 rebase" section -- there is no
# control branch; every arm is cut from this SHA as of the queue-execution
# campaign's base re-point; the original base was 329b8f1,
# codex-efficiency-fixes' tip). Every arm gets its OWN worktree directory
# (never shared/checkout-switched between reps), so JOBS>1 cannot race two
# different arms against one checkout. Before every run this script
# reconciles the mounted worktree's actual `git rev-parse HEAD` against the
# manifest SHA it resolved and refuses to run on a mismatch -- a battery
# that cannot name its arm's SHA is ungraded (arm-manifest.md's own "Runner
# integration gap" note).
#
# Env EVALS_ROOT overrides which evals checkout (lane) is used, same
# convention as codex-efficiency's script. Default:
# /Users/jesse/git/superpowers/superpowers/evals.
#
# Env JOBS (default 1) parallelizes the rep loop: when JOBS>1 and REPS>1,
# up to JOBS reps run concurrently as background subshells (each with its
# own --out-root, batched in groups of JOBS, `wait`ed between batches)
# instead of strictly sequentially -- ported from codex-efficiency's
# run-quorum.sh. JOBS=1 (or REPS=1) keeps the original sequential loop.
# All JOBS reps share the ONE arm worktree mounted for this invocation
# (read-only during the run, never checkout-switched), so this is safe.
#
# Env CODING_AGENT (default codex) selects which Coding-Agent quorum
# drives. Env CREDENTIAL (unset by default) adds `--credential <name>`
# when set.
#
# This campaign's scenarios/ directories carry their OWN fixtures/
# subdirectory (unlike codex-efficiency's split top-level fixtures/ dir --
# simpler because none of these scenarios currently share a fixture across
# variants), so syncing a scenario is one whole-directory rsync. The
# synced-in copy is excluded via the evals checkout's .git/info/exclude --
# it is never committed to superpowers-evals.
set -euo pipefail

EVALS=${EVALS_ROOT:-/Users/jesse/git/superpowers/superpowers/evals}
CAMP=/Users/jesse/git/superpowers/superpowers-autoresearch/campaigns/cost-pathologies
SP_CHECKOUT=/Users/jesse/git/superpowers/superpowers
JOBS=${JOBS:-1}
CODING_AGENT=${CODING_AGENT:-codex}
CREDENTIAL=${CREDENTIAL:-}

ARM=${1:?"usage: run-quorum.sh ARM SCENARIO REPS [REP_START]   (ARM: control | <arm-manifest short code>)"}
SCEN=${2:?"usage: run-quorum.sh ARM SCENARIO REPS [REP_START]   (ARM: control | <arm-manifest short code>)"}
REPS=${3:-1}
REP_START=${4:-1}

# Accept both 'x1a' and 'cp/x1a'.
ARM=${ARM#cp/}

MANIFEST="$CAMP/arm-manifest.md"

if [[ "$ARM" == "control" ]]; then
  SP_ROOT=/tmp/cp-arm-control
  SP_REF=1fed99d
  ARM_DESC="control (sim/dev-postmerge, unpatched)"
else
  BRANCH="cp/$ARM"
  SP_ROOT="/tmp/cp-arm-$ARM"
  [[ -f "$MANIFEST" ]] || {
    echo "run-quorum.sh: arm manifest not found: $MANIFEST" >&2
    exit 1
  }
  # A branch can appear in more than one manifest table (e.g. the original
  # per-arm table plus a later dated re-point section such as "## 2026-08-01
  # rebase") -- take the LAST match, i.e. whichever section sorts lowest in
  # the file, since dated re-point sections are always appended after the
  # rows they supersede (never inserted earlier or edited in place).
  row=$(grep -F "\`$BRANCH\`" "$MANIFEST" | tail -n1 || true)
  [[ -n "$row" ]] || {
    echo "run-quorum.sh: unknown ARM '$ARM' -- branch \`$BRANCH\` not found in $MANIFEST" >&2
    exit 1
  }
  SP_REF=$(awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/, "", $4); print $4}' <<<"$row")
  [[ -n "$SP_REF" ]] || {
    echo "run-quorum.sh: could not parse a SHA for $BRANCH out of manifest row: $row" >&2
    exit 1
  }
  ARM_DESC="$BRANCH @ $SP_REF (per $MANIFEST)"
fi

if [[ ! -d "$SP_ROOT" ]]; then
  echo "run-quorum.sh: materializing $SP_ROOT ($ARM_DESC)" >&2
  git -C "$SP_CHECKOUT" worktree add --detach "$SP_ROOT" "$SP_REF"
fi

# Reconcile: the mounted worktree's HEAD must match the resolved SHA
# (prefix match -- the manifest records abbreviated SHAs). A battery that
# cannot name its arm's SHA is ungraded.
mounted_head=$(git -C "$SP_ROOT" rev-parse HEAD)
case "$mounted_head" in
  "$SP_REF"*) ;;
  *)
    echo "run-quorum.sh: $SP_ROOT is at $mounted_head, expected $SP_REF ($ARM_DESC) -- refusing to run an unreconciled arm" >&2
    exit 1
    ;;
esac
echo "run-quorum.sh: arm '$ARM' resolved to $ARM_DESC, mounted at $SP_ROOT (HEAD=$mounted_head)" >&2

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

if [[ "$JOBS" -gt 1 && "$REPS" -gt 1 ]]; then
  # Batch the rep range into groups of at most JOBS, launching each group's
  # reps concurrently (background subshells) and waiting for the whole group
  # before starting the next -- ported from codex-efficiency/run-quorum.sh.
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
