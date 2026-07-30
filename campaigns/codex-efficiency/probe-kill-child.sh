#!/usr/bin/env bash
# usage: probe-kill-child.sh --dry-run RUNDIR
#        probe-kill-child.sh --live CONTAINER RUNDIR [POLL_INTERVAL_S] [TIMEOUT_S]
#
# E10 probe (b) driver -- lifecycle-truthfulness campaign, Task 14. Detects
# the first CHILD rollout to appear in a quorum run (a spawn_agent
# dispatch), then kills the run's root `codex` OS process from the HOST --
# an uncontrolled, external failure, not an in-band interrupt_agent call
# the controller chooses for itself.
#
# ARCHITECTURE NOTE (source-grounded + live-verified before this script was
# trusted -- see the E10 pre-registration entry,
# logs/2026-07-28-codex-efficiency.md): spawned agents run as tokio tasks
# INSIDE THE SAME OS PROCESS as their parent (codex-rs/core/src/agent/
# control.rs:473, `tokio::spawn`; no `std::process::Command` anywhere in
# the agent/multi_agents_v2 modules). There is no separate child PID to
# target -- "docker exec ps; kill -9 the child process" has no target as
# literally specified. This script kills the run's ONE root `codex`
# process instead -- the only real host-level failure-injection unit this
# architecture affords -- timed to fire once >=1 child has been spawned but
# not yet completed. That is a deliberate, documented ADAPTATION of the
# probe, not a literal per-child kill.
#
# --dry-run RUNDIR: no process interaction at all. Reads an EXISTING,
# COMPLETED run's rollout files (RUNDIR/home/.codex/sessions/**/
# rollout-*.jsonl) in filename order (chronological -- rollout filenames
# embed an ISO timestamp, see rollout_parser.py/score_e1.py's own
# "earliest by filename == chronological" convention) and reports when the
# watch loop WOULD have detected a live child and WOULD have fired the
# kill. Validates detection logic against real data before any live
# process is ever touched. Exit 0 if >=1 child would have been detected,
# 1 if the run never spawned one (nothing to probe).
#
# --live CONTAINER RUNDIR: polls the HOST-visible RUNDIR (the results/
# dir is bind-mounted, so no docker exec is needed for the watch itself)
# every POLL_INTERVAL_S seconds (default 5) for a second rollout file (the
# first child) to appear; once found, waits SETTLE_S (default 3, fixed) for
# it to have actually started writing, lists the container's `codex`
# process(es) (`docker exec CONTAINER ps aux`), SIGKILLs the root one, and
# writes a JSON summary to RUNDIR/probe-kill-summary.json. Exits 1 if no
# child appears within TIMEOUT_S (default 900).
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

usage() {
  echo "usage: probe-kill-child.sh --dry-run RUNDIR" >&2
  echo "       probe-kill-child.sh --live CONTAINER RUNDIR [POLL_INTERVAL_S] [TIMEOUT_S]" >&2
  exit 1
}

[[ $# -ge 1 ]] || usage
MODE=$1; shift

find_rollouts() {
  # Sorted (chronological, per filename convention) list of rollout files
  # under RUNDIR/home/.codex/sessions/**/rollout-*.jsonl.
  local rundir=$1
  find "$rundir/home/.codex/sessions" -name 'rollout-*.jsonl' 2>/dev/null | sort
}

case "$MODE" in
  --dry-run)
    [[ $# -eq 1 ]] || usage
    RUNDIR=$1
    [[ -d "$RUNDIR" ]] || { echo "probe-kill-child.sh: no such RUNDIR: $RUNDIR" >&2; exit 1; }

    ROLLOUTS=()
    while IFS= read -r line; do
      ROLLOUTS+=("$line")
    done < <(find_rollouts "$RUNDIR")
    if [[ ${#ROLLOUTS[@]} -eq 0 ]]; then
      echo "DRY-RUN: no rollout files found under $RUNDIR -- nothing to probe" >&2
      exit 1
    fi
    ROOT=${ROLLOUTS[0]}
    echo "DRY-RUN: root rollout: $(basename "$ROOT")"
    if [[ ${#ROLLOUTS[@]} -lt 2 ]]; then
      echo "DRY-RUN: only 1 rollout file total -- this run never spawned a" \
           "child; the watch loop would never have fired. Nothing to probe." >&2
      exit 1
    fi
    CHILD=${ROLLOUTS[1]}
    echo "DRY-RUN: first child rollout: $(basename "$CHILD")"
    echo "DRY-RUN: total rollout files in this run: ${#ROLLOUTS[@]}"

    # Elapsed time between root and first-child start, parsed out of the
    # filenames' embedded timestamps (rollout-<ISO-with-dashes>-<uuid>.jsonl).
    # A small python3 one-liner, not bash date arithmetic, because dry-run
    # replays HOST-collected (macOS/BSD date) files while a live run's kill
    # decision happens against a Linux container's clock -- one portable
    # implementation for both, instead of two divergent date(1) dialects.
    python3 - "$ROOT" "$CHILD" <<'PYEOF'
import re, sys, datetime
pat = re.compile(r"rollout-(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2})-")
def parse(path):
    m = pat.search(path)
    ts = m.group(1)
    date_part, time_part = ts.split("T")
    time_part = time_part.replace("-", ":")
    return datetime.datetime.fromisoformat(f"{date_part}T{time_part}")
root_ts = parse(sys.argv[1])
child_ts = parse(sys.argv[2])
delta = (child_ts - root_ts).total_seconds()
print(f"DRY-RUN: first child appeared {delta:.0f}s after root session start")
print(f"DRY-RUN: a live watch loop polling every 5s would detect this child")
print(f"DRY-RUN:   within 5s of it appearing (T+{delta:.0f}s to T+{delta+5:.0f}s),")
print(f"DRY-RUN:   then fire the kill after a fixed settle delay.")
PYEOF
    echo "DRY-RUN: PASS -- detection logic confirmed against a real completed run."
    exit 0
    ;;

  --live)
    [[ $# -ge 2 ]] || usage
    CONTAINER=$1
    RUNDIR=$2
    POLL_INTERVAL=${3:-5}
    TIMEOUT=${4:-900}
    SETTLE_S=3

    [[ -d "$RUNDIR" ]] || { echo "probe-kill-child.sh: no such RUNDIR: $RUNDIR" >&2; exit 1; }
    docker inspect "$CONTAINER" >/dev/null 2>&1 || {
      echo "probe-kill-child.sh: no such container: $CONTAINER" >&2; exit 1; }

    echo "LIVE: watching $RUNDIR for a second rollout file (poll every ${POLL_INTERVAL}s, timeout ${TIMEOUT}s)..." >&2
    START_EPOCH=$(date +%s)
    while true; do
      ROLLOUTS=()
    while IFS= read -r line; do
      ROLLOUTS+=("$line")
    done < <(find_rollouts "$RUNDIR")
      if [[ ${#ROLLOUTS[@]} -ge 2 ]]; then
        echo "LIVE: child rollout detected: $(basename "${ROLLOUTS[1]}")" >&2
        break
      fi
      NOW=$(date +%s)
      if (( NOW - START_EPOCH >= TIMEOUT )); then
        echo "LIVE: TIMEOUT after ${TIMEOUT}s -- no child ever spawned; not firing a kill." >&2
        exit 1
      fi
      sleep "$POLL_INTERVAL"
    done

    echo "LIVE: settling ${SETTLE_S}s before kill..." >&2
    sleep "$SETTLE_S"

    echo "LIVE: process listing in $CONTAINER before kill:" >&2
    PS_BEFORE=$(docker exec "$CONTAINER" ps aux 2>&1 || true)
    echo "$PS_BEFORE" >&2

    # Root codex process: the one whose command line matches `codex` and is
    # NOT itself a grep/ps/shell wrapper. See the architecture note above --
    # there is exactly one such process regardless of spawned-child count.
    ROOT_PID=$(echo "$PS_BEFORE" | grep -E '[c]odex( |$)' | grep -v 'ps aux' | awk '{print $2}' | head -1)
    if [[ -z "$ROOT_PID" ]]; then
      echo "LIVE: could not identify a codex process in $CONTAINER -- aborting without killing anything." >&2
      exit 1
    fi
    KILL_EPOCH=$(date +%s)
    echo "LIVE: killing PID $ROOT_PID in $CONTAINER at epoch $KILL_EPOCH" >&2
    docker exec "$CONTAINER" kill -9 "$ROOT_PID" || true

    ROLLOUTS_AT_KILL=()
    while IFS= read -r line; do
      ROLLOUTS_AT_KILL+=("$line")
    done < <(find_rollouts "$RUNDIR")
    SUMMARY="$RUNDIR/probe-kill-summary.json"
    python3 - "$SUMMARY" "$ROOT_PID" "$KILL_EPOCH" "${ROLLOUTS_AT_KILL[@]}" <<'PYEOF'
import json, os, sys
out_path, root_pid, kill_epoch = sys.argv[1], sys.argv[2], sys.argv[3]
rollouts = sys.argv[4:]
summary = {
    "killed_pid": root_pid,
    "kill_epoch": int(kill_epoch),
    "rollout_files_at_kill": [
        {"path": os.path.basename(p), "bytes": os.path.getsize(p)} for p in rollouts
    ],
}
with open(out_path, "w") as f:
    json.dump(summary, f, indent=2)
print(f"LIVE: wrote {out_path}", file=sys.stderr)
PYEOF
    exit 0
    ;;

  *)
    usage
    ;;
esac
