"""Run-summary export for the ops dashboard."""


def export_summary(processed):
    kinds = {}
    for job_id, result in processed:
        kind = result.split(":", 1)[0]
        kinds[kind] = kinds.get(kind, 0) + 1
    return {"format": "v2", "total": len(processed), "by_kind": kinds}
