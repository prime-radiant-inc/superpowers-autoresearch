"""Storage tier catalog, reloadable live without restarting the service.

CONSTRUCTED VARIANT (campaigns/cost-pathologies/
test_cp_x1_edit_existing.py, fix round 2 / task-5-review.md's Re-review
round 1 new Important finding) -- the SAME lock-guarded catch shape as
`variant-debatable1-lock-guarded/`, but guarded with a binary
`threading.Semaphore(1)` (functionally equivalent to a mutex) named
`self._sem` -- a real, plausible naming/primitive choice a coding
session could make that the original, narrower `_LOCK_GUARD_RE`
misclassified as `"escape"`.
"""
import threading


class TierCatalog:
    def __init__(self, tiers):
        self._tiers = dict(tiers)
        self._sem = threading.Semaphore(1)

    def get_tier(self, tier_id):
        with self._sem:
            return self._tiers[tier_id]

    def has_tier(self, tier_id):
        """Whether `tier_id` is currently present in the catalog (REQ-6)."""
        with self._sem:
            return tier_id in self._tiers

    def reload_tiers(self, new_tiers):
        """Replace the live tier catalog with `new_tiers` without
        restarting the service -- statement generation in progress must
        never see a full outage during a reload. The semaphore
        serializes `reload_tiers` against `get_tier`/`has_tier`: a
        concurrent lookup blocks until the reload finishes rather than
        observing a transiently empty dict.
        """
        with self._sem:
            self._tiers.clear()
            self._tiers.update(new_tiers)
