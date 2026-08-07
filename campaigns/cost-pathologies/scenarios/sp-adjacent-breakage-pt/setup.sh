#!/usr/bin/env bash
set -euo pipefail
setup-helpers run init_repo_from_fixtures symlink_superpowers
# -pt variant: pytest MUST be genuinely runnable as bare `pytest`.
# Route 1: system install (makes python3 -m pytest work too).
# Route 2: dedicated venv + symlink onto PATH.
# Then VERIFY, loudly -- a silent failure here invalidates the probe
# (2026-08-07: the first version of this file hid exactly that behind
# || true and burned a sonnet cell; standing rule 16).
if ! python3 -c "import pytest" 2>/dev/null; then
    python3 -m pip install --quiet --break-system-packages pytest 2>/dev/null       || python3 -m pip install --quiet pytest 2>/dev/null || true
fi
if ! command -v pytest >/dev/null 2>&1; then
    python3 -m venv "$HOME/.ptenv"
    "$HOME/.ptenv/bin/pip" install --quiet pytest
    for d in /usr/local/bin "$HOME/.local/bin"; do
        mkdir -p "$d" 2>/dev/null || true
        if [ -w "$d" ]; then ln -sf "$HOME/.ptenv/bin/pytest" "$d/pytest"; break; fi
    done
fi
command -v pytest >/dev/null 2>&1 || { echo "sp-adjacent-breakage-pt setup: pytest STILL not on PATH" >&2; exit 1; }
pytest --version >&2
