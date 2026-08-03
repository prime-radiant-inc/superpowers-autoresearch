# Task 2 of docs/superpowers/plans/job-queue-plan.md.

MAX_RETRY_ATTEMPTS = 4


def reschedule(attempt_count):
    return attempt_count < MAX_RETRY_ATTEMPTS


def next_status(attempt_count):
    if attempt_count < MAX_RETRY_ATTEMPTS:
        return "retrying"
    return "failed"
