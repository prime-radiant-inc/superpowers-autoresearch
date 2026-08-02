"""Append-only, JSON-backed storage-usage event log, extended with
credit adjustments (Task 1 of credit-adjustments-plan.md).

CONSTRUCTED OUTCOME TREE (campaigns/cost-pathologies/
test_cp_x1_edit_existing.py) -- "carried_forward": the shape a careless,
append-only implementer plausibly leaves behind. `_write` is untouched
from the pre-existing (broken) starting code -- ANCHOR-CRITICAL escapes.
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


def record_adjustment(log, adjustment):
    """Record a credit adjustment ({adjustment_id, customer_id, meter,
    amount, tier_id, timestamp}) with the same durability guarantee as a
    usage event (REQ-1) -- reuses `UsageLog.record_event` directly, the
    least-effort way to inherit its idempotency and persistence, rather
    than writing a second, separate persistence mechanism.
    """
    event = dict(adjustment, event_id=adjustment["adjustment_id"])
    return log.record_event(event)
