import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jobqueue.reporter import build_report


def test_build_report_counts_total_and_by_status():
    jobs = [
        {"job_id": "j1", "status": "done"},
        {"job_id": "j2", "status": "done"},
        {"job_id": "j3", "status": "running"},
        {"job_id": "j4", "status": "retrying"},
    ]
    report = build_report(jobs)
    assert report["total"] == 4
    assert report["by_status"]["done"] == 2
    assert report["by_status"]["running"] == 1
    assert report["by_status"]["retrying"] == 1
    assert report["by_status"]["queued"] == 0
    assert report["by_status"]["failed"] == 0


def test_build_report_unrecognized_status_not_in_by_status():
    jobs = [{"job_id": "j1", "status": "archived"}]
    report = build_report(jobs)
    assert report["total"] == 1
    assert "archived" not in report["by_status"]
