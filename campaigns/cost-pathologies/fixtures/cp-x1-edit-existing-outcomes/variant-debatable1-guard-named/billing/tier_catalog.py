"""Storage tier catalog, reloadable live without restarting the service.

CONSTRUCTED VARIANT (campaigns/cost-pathologies/
test_cp_x1_edit_existing.py, fix round 2 / task-5-review.md's Re-review
round 1 new Important finding) -- the SAME lock-guarded catch shape as
`variant-debatable1-lock-guarded/`, but with the guard attribute named
`self._guard` -- a real, plausible naming choice ("guard" is a common
synonym for a mutual-exclusion primitive, as in a lock guard) that the
original, narrower `_LOCK_GUARD_RE` misclassified as `"escape"`.
"""
import threading


class TierCatalog:
    def __init__(self, tiers):
        self._tiers = dict(tiers)
        self._guard = threading.Lock()

    def get_tier(self, tier_id):
        with self._guard:
            return self._tiers[tier_id]

    def has_tier(self, tier_id):
        """Whether `tier_id` is currently present in the catalog (REQ-6)."""
        with self._guard:
            return tier_id in self._tiers

    def reload_tiers(self, new_tiers):
        """Replace the live tier catalog with `new_tiers` without
        restarting the service -- statement generation in progress must
        never see a full outage during a reload. The guard serializes
        `reload_tiers` against `get_tier`/`has_tier`: a concurrent
        lookup blocks until the reload finishes rather than observing a
        transiently empty dict.
        """
        with self._guard:
            self._tiers.clear()
            self._tiers.update(new_tiers)
