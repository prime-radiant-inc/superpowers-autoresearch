import os
from jobrunner.queue import JobQueue
from jobrunner.worker import run


def test_run_processes_all_pending(tmp_path):
    state = str(tmp_path / "state.json")
    q = JobQueue(state)
    q.add(1, "email", {"to": "a@example.com", "subject": "hi"})
    q.add(2, "cleanup", {"older_than_days": 7})
    processed = run(state)
    assert [job_id for job_id, _ in processed] == [1, 2]


def test_done_jobs_are_not_reprocessed(tmp_path):
    state = str(tmp_path / "state.json")
    q = JobQueue(state)
    q.add(1, "email", {"to": "a@example.com", "subject": "hi"})
    run(state)
    processed_again = run(state)
    assert processed_again == []
