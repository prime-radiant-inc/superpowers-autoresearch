import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jobqueue.archiver import should_archive


def test_archives_done_job_past_threshold():
    assert should_archive("done", 30) is True


def test_does_not_archive_running_job():
    assert should_archive("running", 60) is False


def test_does_not_archive_done_job_under_threshold():
    assert should_archive("done", 10) is False
