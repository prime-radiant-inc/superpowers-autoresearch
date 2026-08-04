import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest

from jobqueue.notifier import notify


def test_notify_known_statuses():
    assert notify("queued") == "job queued"
    assert notify("running") == "job started"
    assert notify("retrying") == "job retrying"
    assert notify("done") == "job completed successfully"
    assert notify("failed") == "job failed"


def test_notify_unknown_status_raises():
    with pytest.raises(ValueError):
        notify("archived")
