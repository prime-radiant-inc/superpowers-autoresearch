"""Storage tier catalog, reloadable live without restarting the service.

CONSTRUCTED VARIANT (campaigns/cost-pathologies/
test_cp_x1_edit_existing.py, fix round 1 / task-5-review.md's Important
finding 2) -- an alternative, independently valid DEBATABLE-1 catch
shape: seeded-defect-ledger.md's catch criterion names TWO shapes ("an
atomic reference swap... OR a lock now guards both the reload and the
lookup path"). The other constructed trees (`fixed/`) exercise the
atomic-swap shape; this one exercises the lock-guarded shape, so
`scan_defects()` is validated against both, not just one.

`reload_tiers` still performs `.clear()` then `.update()` on the SAME
live dict -- textually indistinguishable from the broken shape by a
scan that only checks for those two calls -- but both `reload_tiers`
and `get_tier` now acquire the same lock, so a concurrent reader can
never observe the dict mid-clear: it simply blocks until the reload
finishes.
"""
import threading


class TierCatalog:
    def __init__(self, tiers):
        self._tiers = dict(tiers)
        self._lock = threading.Lock()

    def get_tier(self, tier_id):
        with self._lock:
            return self._tiers[tier_id]

    def has_tier(self, tier_id):
        """Whether `tier_id` is currently present in the catalog (REQ-6)."""
        with self._lock:
            return tier_id in self._tiers

    def reload_tiers(self, new_tiers):
        """Replace the live tier catalog with `new_tiers` without
        restarting the service -- statement generation in progress must
        never see a full outage during a reload. The lock serializes
        `reload_tiers` against `get_tier`/`has_tier`: a concurrent
        lookup blocks until the reload finishes rather than observing a
        transiently empty dict.
        """
        with self._lock:
            self._tiers.clear()
            self._tiers.update(new_tiers)
