import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest

from jobqueue.worker import (
    JobPayloadError,
    WorkerExhausted,
    parse_job,
    run_with_retries,
    validate_priority,
)


def test_parse_job_normal_line():
    assert parse_job("j1,3,do the thing") == {
        "job_id": "j1",
        "priority": 3,
        "payload": "do the thing",
        "status": "queued",
    }


def test_parse_job_missing_field_raises_named_error():
    with pytest.raises(JobPayloadError, match="payload"):
        parse_job("j1,3,")


def test_validate_priority_accepts_minimum():
    validate_priority(1)


def test_validate_priority_rejects_below_minimum():
    with pytest.raises(ValueError):
        validate_priority(0)


def test_run_with_retries_gives_up_after_retry_limit():
    calls = []

    def always_fails():
        calls.append(1)
        raise OSError("transient")

    with pytest.raises(WorkerExhausted):
        run_with_retries(always_fails)
    assert len(calls) == 4
