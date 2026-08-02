# Daily digest: summarizes a batch of already-exported reading rows (from
# a nightly export job, not from alertpipe.ingest) into a per-kind count
# and a flagged list. Synthetic fixture; no real export job, no real file
# I/O -- rows are passed in already parsed.

THRESHOLD = 90.0


def classify_severity(value):
    """This module's own severity vocabulary for a digest row: "warn"
    below THRESHOLD, "error" at or above it."""
    return "error" if value >= THRESHOLD else "warn"


def build_digest(rows):
    """rows: list of dicts shaped {"sensor_id", "kind", "value",
    "recorded_at"} where recorded_at is this module's own timestamp
    format, "%d/%m/%Y %H:%M" (day-first, no seconds) -- these rows come
    from the nightly export job, not from alertpipe.ingest.parse_reading.

    Returns {"count": int, "by_kind": {kind: count}, "flagged": [row,
    ...]} where flagged holds every row classify_severity marks "error".
    """
    by_kind = {}
    flagged = []
    for row in rows:
        by_kind[row["kind"]] = by_kind.get(row["kind"], 0) + 1
        if classify_severity(row["value"]) == "error":
            flagged.append(row)
    return {"count": len(rows), "by_kind": by_kind, "flagged": flagged}
