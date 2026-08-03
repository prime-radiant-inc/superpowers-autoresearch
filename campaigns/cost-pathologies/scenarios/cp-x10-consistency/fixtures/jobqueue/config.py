# Pre-existing queue-name normalization helper. Synthetic fixture; no task
# in docs/superpowers/plans/job-queue-plan.md modifies this file.

DEFAULT_QUEUE = "default"


def normalize_queue_name(queue_name):
    """Lowercases and strips a queue name for consistent lookups."""
    return queue_name.strip().lower()
