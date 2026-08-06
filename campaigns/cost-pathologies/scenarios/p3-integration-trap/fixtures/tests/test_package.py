import os
import sys

# Self-resolving import (matches this campaign's other fixtures'
# convention): this fixture is also collected standalone by the
# top-level `pytest` sweep, where it is never pip-installed, so it must
# find its sibling package without relying on an editable install.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import metrics


def test_package_imports():
    assert metrics.__name__ == "metrics"
