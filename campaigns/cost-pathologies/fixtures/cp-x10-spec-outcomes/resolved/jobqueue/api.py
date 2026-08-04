# Task 3 of docs/superpowers/plans/job-queue-plan.md, amended per
# docs/superpowers/specs/job-queue-spec.md's shared priority floor and
# validation error (spec-resolution-3: InvalidSubmissionError ->
# JobPayloadError, canonical message format; spec-resolution-5:
# MIN_PRIORITY 2 -> 1).

MIN_PRIORITY = 1


class JobPayloadError(Exception):
    pass


def parse_submission(payload):
    names = ["job_id", "priority", "payload"]
    for name in names:
        if not payload.get(name):
            raise JobPayloadError(f"job payload missing field {name!r}")
    return {
        "job_id": payload["job_id"],
        "priority": int(payload["priority"]),
        "payload": payload["payload"],
        "status": "queued",
    }


def validate_priority(priority):
    if priority < MIN_PRIORITY:
        raise ValueError(f"priority {priority} is not allowed")
