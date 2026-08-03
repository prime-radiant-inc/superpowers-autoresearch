"""Resolves the directive-unit corpus for the CLAUDE.md-lift campaign.

PRIVACY-CRITICAL: the verbatim unit text is private config and lives OUTSIDE
this repo, at UNITS_DIR (a sibling checkout's _tmp scratch area, same
handling as other donor corpora -- see docs/2026-08-03-claudemd-lift-campaign-
design.md). This module only ever reads those files by path at runtime; it
must never inline, cache-to-repo, or log their contents. Callers that need
the actual directive text (the runner, when composing a unit arm's CLAUDE.md)
must read it fresh from disk and write it straight into a workdir OUTSIDE this
repo (/tmp) -- never into anything that could be `git add`ed here.

Layout (not tracked by this repo):
    UNITS_DIR/units/<UNIT-ID>.md      verbatim directive text for the unit
    UNITS_DIR/units-index.tsv         "<UNIT-ID>\t<class>" per line, class in {A,B,C}
"""
from __future__ import annotations

import os

# Sibling of the superpowers-autoresearch checkout's parent (/Users/jesse/git/superpowers/),
# not this repo. Overridable for tests via CLAUDEMD_LIFT_UNITS_DIR.
DEFAULT_UNITS_DIR = os.path.expanduser("~/git/superpowers/_tmp/claudemd-lift")


def units_dir():
    return os.environ.get("CLAUDEMD_LIFT_UNITS_DIR", DEFAULT_UNITS_DIR)


def index_path():
    return os.path.join(units_dir(), "units-index.tsv")


def unit_path(unit_id):
    return os.path.join(units_dir(), "units", f"{unit_id}.md")


def load_index():
    """Return {unit_id: class} from units-index.tsv. Empty dict if missing."""
    path = index_path()
    if not os.path.exists(path):
        return {}
    index = {}
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                index[parts[0]] = parts[1]
    return index


def read_unit_text(unit_id):
    """Read a unit's verbatim directive text by ID. Raises FileNotFoundError if absent.

    Callers MUST NOT print, log, or persist the returned text anywhere inside
    this repo -- write it only into throwaway /tmp workdirs.
    """
    path = unit_path(unit_id)
    with open(path) as f:
        return f.read()


def available_units():
    """List of unit IDs that have both an index entry and a text file on disk."""
    index = load_index()
    return sorted(u for u in index if os.path.exists(unit_path(u)))
