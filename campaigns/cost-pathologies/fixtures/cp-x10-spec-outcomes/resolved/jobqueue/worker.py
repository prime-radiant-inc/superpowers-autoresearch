# Task 1 of docs/superpowers/plans/job-queue-plan.md.

MIN_PRIORITY = 1
RETRY_LIMIT = 4


class JobPayloadError(Exception):
    pass


class WorkerExhausted(Exception):
    pass


def parse_job(raw_line):
    fields = raw_line.split(",")
    names = ["job_id", "priority", "payload"]
    values = {}
    for i, name in enumerate(names):
        value = fields[i].strip() if i < len(fields) else ""
        if not value:
            raise JobPayloadError(f"job payload missing field {name!r}")
        values[name] = value
    return {
        "job_id": values["job_id"],
        "priority": int(values["priority"]),
        "payload": values["payload"],
        "status": "queued",
    }


def validate_priority(priority):
    if priority < MIN_PRIORITY:
        raise ValueError(f"invalid priority: {priority} is below minimum")


def run_with_retries(run_fn):
    attempts = 0
    while attempts < RETRY_LIMIT:
        attempts += 1
        try:
            return run_fn()
        except OSError:
            continue
    raise WorkerExhausted(f"gave up after {RETRY_LIMIT} attempts")
