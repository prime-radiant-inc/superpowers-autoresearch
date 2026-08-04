import pytest
from orders.notifications import notify_customer, retries_for_channel


def test_status_map():
    assert notify_customer("received") == "order received"
    assert notify_customer("picking") == "order is being picked"
    assert notify_customer("shipped") == "order has shipped"
    assert notify_customer("cancelled") == "order was cancelled"


def test_unknown_status_raises():
    with pytest.raises(ValueError, match="unknown order status"):
        notify_customer("lost")


def test_channel_overrides():
    assert retries_for_channel("email") == 3
    assert retries_for_channel("sms") == 5
    assert retries_for_channel("push") == 2


def test_unlisted_channel_falls_back_to_default():
    assert retries_for_channel("carrier_pigeon") == 3
