# Task 2 of docs/superpowers/plans/job-queue-plan.md, amended per
# docs/superpowers/specs/job-queue-spec.md's shared retry-cap name
# (spec-resolution-2: MAX_RETRY_ATTEMPTS -> RETRY_LIMIT, value unchanged).

RETRY_LIMIT = 4


def reschedule(attempt_count):
    return attempt_count < RETRY_LIMIT


def next_status(attempt_count):
    if attempt_count < RETRY_LIMIT:
        return "retrying"
    return "failed"
