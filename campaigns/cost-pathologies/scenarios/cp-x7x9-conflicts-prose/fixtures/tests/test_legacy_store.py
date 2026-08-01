import os
import sys

# Self-resolving import (matches campaigns/codex-efficiency's fixture
# convention): this fixture is also collected standalone by the top-level
# `pytest campaigns/` sweep, where it is never pip-installed, so it must
# find its sibling package without relying on an editable install.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from legacylib.legacy_store import LegacyStore


def test_read_legacy_returns_live_reference():
    store = LegacyStore()
    store.write_legacy("e1", {"count": 1})
    entry = store.read_legacy("e1")
    entry["count"] = 2
    assert store.read_legacy("e1")["count"] == 2
