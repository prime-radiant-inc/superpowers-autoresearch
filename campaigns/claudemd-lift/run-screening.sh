#!/usr/bin/env bash
# Thin wrapper for run_screening.py -- see that file's docstring for usage,
# flags (--dry-run, --probe, --unit, --reps, ...), and the isolation/auth
# recipe. Kept as a .sh entry point per the campaign's runner convention;
# all logic lives in the Python script so it's testable.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$HERE/run_screening.py" "$@"
