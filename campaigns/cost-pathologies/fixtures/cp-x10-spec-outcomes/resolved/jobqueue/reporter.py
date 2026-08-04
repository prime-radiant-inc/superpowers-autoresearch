# Task 5 of docs/superpowers/plans/job-queue-plan.md, amended per
# docs/superpowers/specs/job-queue-spec.md's shared downstream-sink
# timeout and five-status vocabulary (spec-resolution-1: TIMEOUT_SECONDS
# 90 -> 30; spec-resolution-4: "retrying" is a first-class status).

TIMEOUT_SECONDS = 30

_KNOWN_STATUSES = ("queued", "running", "retrying", "done", "failed")


def build_report(jobs):
    by_status = {status: 0 for status in _KNOWN_STATUSES}
    for job in jobs:
        status = job["status"]
        if status in by_status:
            by_status[status] += 1
    return {"total": len(jobs), "by_status": by_status}
