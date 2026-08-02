# Pre-existing sensor-id normalization helper. Synthetic fixture; no task
# in docs/superpowers/plans/alert-pipeline-plan.md modifies this file.

DEFAULT_TIMEZONE = "UTC"


def normalize_sensor_id(sensor_id):
    """Lowercases and strips a sensor id for consistent lookups."""
    return sensor_id.strip().lower()
