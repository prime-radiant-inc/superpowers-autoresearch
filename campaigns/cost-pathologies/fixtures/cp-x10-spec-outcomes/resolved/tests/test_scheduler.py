import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jobqueue.scheduler import next_status, reschedule


def test_reschedule_true_under_cap():
    assert reschedule(3) is True


def test_reschedule_false_at_cap():
    assert reschedule(4) is False


def test_next_status_retrying_under_cap():
    assert next_status(3) == "retrying"


def test_next_status_failed_at_cap():
    assert next_status(4) == "failed"
