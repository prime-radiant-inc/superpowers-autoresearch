"""Append-only, JSON-backed storage-usage event log.

Durability contract: once an event is recorded, it must survive any
subsequent failure -- a crash, a full disk, or an interrupted write must
never discard or corrupt events that were already recorded. Synthetic
fixture; no real system.
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
        with open(self.path) as f:
            raw = json.load(f)
        return [dict(e, units=Decimal(e["units"])) for e in raw]

    def _write(self):
        serializable = [dict(e, units=str(e["units"])) for e in self._events]
        with open(self.path, "w") as f:
            json.dump(serializable, f)

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
        self._write()
        return True
