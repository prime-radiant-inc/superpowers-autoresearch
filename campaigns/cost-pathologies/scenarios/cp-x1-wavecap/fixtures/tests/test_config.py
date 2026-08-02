import os
import sys

# Self-resolving import (matches campaigns/cost-pathologies' other
# fixtures' convention): this fixture is also collected standalone by the
# top-level `pytest campaigns/` sweep, where it is never pip-installed, so
# it must find its sibling package without relying on an editable install.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from alertpipe.config import normalize_sensor_id


def test_normalize_sensor_id_strips_and_lowercases():
    assert normalize_sensor_id("  Sensor-1  ") == "sensor-1"
