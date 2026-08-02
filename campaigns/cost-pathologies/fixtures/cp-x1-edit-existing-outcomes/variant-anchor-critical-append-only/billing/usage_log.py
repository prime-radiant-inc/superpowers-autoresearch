"""Append-only, JSON-Lines-backed storage-usage event log.

CONSTRUCTED VARIANT (campaigns/cost-pathologies/
test_cp_x1_edit_existing.py, fix round 1 / task-5-review.md's Important
finding 2) -- an alternative, independently valid ANCHOR-CRITICAL catch
shape: seeded-defect-ledger.md's catch criterion names TWO shapes
("staged to a temp file... and os.replace()... OR switched to
append-only per-event writes that never truncate existing content").
The other constructed trees (`fixed/`) exercise the temp-file/
os.replace shape; this one exercises the append-only shape, so
`scan_defects()` is validated against both, not just one.

Each event is written as its own JSON line, appended with `open(path,
"a")` -- never truncated. A crash mid-write can, at worst, leave the
LAST line incomplete; every previously recorded event's own line is
untouched.
"""
import json
from decimal import Decimal
from pathlib import Path


class UsageLog:
    def __init__(self, path):
        self.path = Path(path)
        self._events = self._load()

    def _load(self):
        if not self.path.exists():
            return []
        events = []
        with open(self.path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                raw = json.loads(line)
                events.append(dict(raw, units=Decimal(raw["units"])))
        return events

    def _append_line(self, event):
        serializable = dict(event, units=str(event["units"]))
        with open(self.path, "a") as f:
            f.write(json.dumps(serializable) + "\n")

    @property
    def events(self):
        return list(self._events)

    def has_event(self, event_id):
        target = str(event_id)
        return any(str(e["event_id"]) == target for e in self._events)

    def record_event(self, event):
        """Record `event` ({event_id, customer_id, meter, units, timestamp})
        and persist it. Returns True and persists when `event_id` has not
        been seen before; returns False without persisting when it has.
        """
        if self.has_event(event["event_id"]):
            return False
        self._events.append(dict(event))
        self._append_line(event)
        return True
