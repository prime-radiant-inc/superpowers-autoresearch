# Task 4 of docs/superpowers/plans/job-queue-plan.md, amended per
# docs/superpowers/specs/job-queue-spec.md's five-status vocabulary
# (spec-resolution-4: "retrying" is a first-class status).

TIMEOUT_SECONDS = 30

_MESSAGES = {
    "queued": "job queued",
    "running": "job started",
    "retrying": "job retrying",
    "done": "job completed successfully",
    "failed": "job failed",
}


def notify(job_status):
    if job_status not in _MESSAGES:
        raise ValueError(f"unknown job status: {job_status!r}")
    return _MESSAGES[job_status]
