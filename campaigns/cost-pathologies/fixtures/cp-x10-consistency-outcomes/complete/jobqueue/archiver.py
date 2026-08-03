# Task 6 of docs/superpowers/plans/job-queue-plan.md.

ARCHIVE_AFTER_DAYS = 30


def should_archive(job_status, age_days):
    return job_status in ("done", "failed") and age_days >= ARCHIVE_AFTER_DAYS
