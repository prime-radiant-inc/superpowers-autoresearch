import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest

from jobqueue.api import InvalidSubmissionError, parse_submission, validate_priority


def test_parse_submission_normal_payload():
    payload = {"job_id": "j1", "priority": "2", "payload": "do the thing"}
    assert parse_submission(payload) == {
        "job_id": "j1",
        "priority": 2,
        "payload": "do the thing",
        "status": "queued",
    }


def test_parse_submission_missing_field_raises_named_error():
    payload = {"job_id": "j1", "priority": "2", "payload": ""}
    with pytest.raises(InvalidSubmissionError, match="payload"):
        parse_submission(payload)


def test_validate_priority_accepts_minimum():
    validate_priority(2)


def test_validate_priority_rejects_below_minimum():
    with pytest.raises(ValueError):
        validate_priority(1)
