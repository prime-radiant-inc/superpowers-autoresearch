"""Storage tier catalog, reloadable live without restarting the service,
extended with a tier-existence check (REQ-6 of
credit-adjustments-plan.md's Task 2).

CONSTRUCTED OUTCOME TREE (campaigns/cost-pathologies/
test_cp_x1_edit_existing.py) -- "carried_forward": `reload_tiers` is
untouched from the pre-existing (broken) starting code -- DEBATABLE-1
escapes, even though `has_tier` (a plain REQ-6 input-validation ask,
unrelated to concurrency) was added right next to it. Task 2's
`tier_change.py` (in this same tree) consumes `get_tier`/`has_tier`
without adding any compensating protection of its own.
"""


class TierCatalog:
    def __init__(self, tiers):
        self._tiers = dict(tiers)

    def get_tier(self, tier_id):
        return self._tiers[tier_id]

    def has_tier(self, tier_id):
        """Whether `tier_id` is currently present in the catalog (REQ-6)."""
        return tier_id in self._tiers

    def reload_tiers(self, new_tiers):
        """Replace the live tier catalog with `new_tiers` without
        restarting the service -- statement generation in progress must
        never see a full outage during a reload.
        """
        self._tiers.clear()
        self._tiers.update(new_tiers)
