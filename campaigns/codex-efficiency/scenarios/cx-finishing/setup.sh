#!/usr/bin/env bash
set -euo pipefail
cd "$QUORUM_WORKDIR"
bash "$QUORUM_SCENARIO_DIR/fixtures/build.sh"
setup-helpers run symlink_superpowers
