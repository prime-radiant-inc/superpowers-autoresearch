#!/usr/bin/env bash
set -euo pipefail
setup-helpers run init_repo_from_fixtures symlink_superpowers
# The scenario's suite must be runnable with bare pytest: several
# sp-adjacent reps showed "tried to look, pytest missing, gave up".
python3 -m pip install --quiet --break-system-packages pytest 2>/dev/null \
  || python3 -m pip install --quiet pytest 2>/dev/null \
  || true
