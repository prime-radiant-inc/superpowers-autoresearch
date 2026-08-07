#!/usr/bin/env bash
set -euo pipefail
# The -sf arm is meaningless without the injected unit file (it is
# git-ignored in the campaign repo; re-inject from the local units dir
# if this trips).
[ -f "$QUORUM_SCENARIO_DIR/fixtures/CLAUDE.md" ] || { echo "sp-overbuild-engaged-sf: fixtures/CLAUDE.md missing (unit not injected)" >&2; exit 1; }
setup-helpers run init_repo_from_fixtures symlink_superpowers
