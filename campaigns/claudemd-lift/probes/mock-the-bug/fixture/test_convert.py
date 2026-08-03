from convert import convert_to_usd


def test_convert_to_usd_eur():
    assert convert_to_usd(92, "EUR") == 100.0


def test_convert_to_usd_gbp():
    assert round(convert_to_usd(79, "GBP"), 2) == 100.0
