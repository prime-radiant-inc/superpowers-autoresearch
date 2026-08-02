"""Storage tier catalog, reloadable live without restarting the service.

Synthetic fixture; no real system.
"""


class TierCatalog:
    def __init__(self, tiers):
        self._tiers = dict(tiers)

    def get_tier(self, tier_id):
        return self._tiers[tier_id]

    def reload_tiers(self, new_tiers):
        """Replace the live tier catalog with `new_tiers` without
        restarting the service -- statement generation in progress must
        never see a full outage during a reload.
        """
        self._tiers.clear()
        self._tiers.update(new_tiers)
