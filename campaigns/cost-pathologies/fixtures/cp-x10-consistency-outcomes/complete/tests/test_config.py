import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jobqueue.config import normalize_queue_name


def test_normalize_queue_name_strips_and_lowercases():
    assert normalize_queue_name("  Queue-1  ") == "queue-1"
