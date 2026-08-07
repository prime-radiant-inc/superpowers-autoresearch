#!/usr/bin/env bash
set -euo pipefail
setup-helpers run init_repo_from_fixtures symlink_superpowers
# -pt variant: pytest preinstalled, so \"tried to look, tool missing\"
# cannot occur -- separates wont-look from friction-stopped.
python3 -m pip install --quiet --break-system-packages pytest 2>/dev/null   || python3 -m pip install --quiet pytest 2>/dev/null   || true
