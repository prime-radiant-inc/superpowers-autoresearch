# Task 3 of docs/superpowers/plans/job-queue-plan.md.

MIN_PRIORITY = 2


class InvalidSubmissionError(Exception):
    pass


def parse_submission(payload):
    names = ["job_id", "priority", "payload"]
    for name in names:
        if not payload.get(name):
            raise InvalidSubmissionError(f"submission rejected: field {name!r} is required")
    return {
        "job_id": payload["job_id"],
        "priority": int(payload["priority"]),
        "payload": payload["payload"],
        "status": "queued",
    }


def validate_priority(priority):
    if priority < MIN_PRIORITY:
        raise ValueError(f"priority {priority} is not allowed")
