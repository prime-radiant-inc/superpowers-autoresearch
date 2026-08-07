#!/usr/bin/env bash
set -euo pipefail
setup-helpers run init_repo_from_fixtures symlink_superpowers provision_venv
# -pt variant: provision_venv gives <workdir>/.venv with pytest -- the
# in-container-proven route (k1g agents used it). README points sessions
# at it, removing the tool-missing dead end this variant exists to
# eliminate. Direct install routes fail here: setup executes outside the
# agent container, so host-side pip/user-site installs are invisible to
# the session (2026-08-07, two burned relaunches).
[ -x .venv/bin/pytest ] || { echo "sp-adjacent-breakage-pt setup: .venv/bin/pytest missing after provision_venv" >&2; exit 1; }
