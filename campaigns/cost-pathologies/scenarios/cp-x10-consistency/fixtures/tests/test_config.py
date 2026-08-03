import os
import sys

# Self-resolving import (matches campaigns/cost-pathologies' other
# fixtures' convention): this fixture is also collected standalone by the
# top-level `pytest campaigns/` sweep, where it is never pip-installed, so
# it must find its sibling package without relying on an editable install.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jobqueue.config import normalize_queue_name


def test_normalize_queue_name_strips_and_lowercases():
    assert normalize_queue_name("  Queue-1  ") == "queue-1"
