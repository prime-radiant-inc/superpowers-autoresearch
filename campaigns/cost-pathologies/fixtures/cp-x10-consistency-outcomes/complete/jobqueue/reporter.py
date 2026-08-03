# Task 5 of docs/superpowers/plans/job-queue-plan.md.

TIMEOUT_SECONDS = 90

_KNOWN_STATUSES = ("queued", "running", "done", "failed")


def build_report(jobs):
    by_status = {status: 0 for status in _KNOWN_STATUSES}
    for job in jobs:
        status = job["status"]
        if status in by_status:
            by_status[status] += 1
    return {"total": len(jobs), "by_status": by_status}
