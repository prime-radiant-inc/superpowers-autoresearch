import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orders.archiving import should_archive


def test_shipped_past_threshold_is_archived():
    assert should_archive("shipped", 30) is True


def test_running_never_archived():
    assert should_archive("picking", 999) is False


def test_shipped_under_threshold_not_archived():
    assert should_archive("shipped", 5) is False
