import pytest

from orders.rate_limits import is_rate_limited, rate_limit_for_client


def test_rate_limit_for_known_client_types():
    assert rate_limit_for_client("internal") == 600
    assert rate_limit_for_client("partner") == 120
    assert rate_limit_for_client("public") == 30


def test_unknown_client_type_raises():
    with pytest.raises(ValueError, match="unknown client type: 'bot'"):
        rate_limit_for_client("bot")


def test_is_rate_limited():
    assert is_rate_limited("public", 31) is True
    assert is_rate_limited("public", 30) is False
