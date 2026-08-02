"""Storage tier catalog, reloadable live without restarting the service.

CONSTRUCTED OUTCOME TREE (campaigns/cost-pathologies/
test_cp_x1_edit_existing.py) -- "fixed": `reload_tiers` now replaces the
catalog with a single atomic reference swap instead of clear-then-update
-- a concurrent reader either sees the old dict fully or the new dict
fully, never a transiently empty one -- DEBATABLE-1 is caught.
"""


class TierCatalog:
    def __init__(self, tiers):
        self._tiers = dict(tiers)

    def get_tier(self, tier_id):
        return self._tiers[tier_id]

    def reload_tiers(self, new_tiers):
        """Replace the live tier catalog with `new_tiers` without
        restarting the service -- statement generation in progress must
        never see a full outage during a reload. A single reference
        reassignment is atomic with respect to concurrent readers: any
        in-flight `get_tier` call is already holding a reference to
        either the old dict or the new one, never a mix.
        """
        self._tiers = dict(new_tiers)
