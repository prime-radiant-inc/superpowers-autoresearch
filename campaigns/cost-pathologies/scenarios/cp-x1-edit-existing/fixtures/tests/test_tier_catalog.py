from decimal import Decimal

from billing.tier_catalog import TierCatalog


def test_get_tier_returns_configured_tier():
    catalog = TierCatalog({"standard": {"rate_per_unit": Decimal("0.05")}})
    assert catalog.get_tier("standard")["rate_per_unit"] == Decimal("0.05")


def test_reload_tiers_replaces_the_whole_catalog():
    catalog = TierCatalog({"standard": {"rate_per_unit": Decimal("0.05")}})
    catalog.reload_tiers({"premium": {"rate_per_unit": Decimal("0.08")}})
    assert catalog.get_tier("premium")["rate_per_unit"] == Decimal("0.08")
    assert "standard" not in catalog._tiers
