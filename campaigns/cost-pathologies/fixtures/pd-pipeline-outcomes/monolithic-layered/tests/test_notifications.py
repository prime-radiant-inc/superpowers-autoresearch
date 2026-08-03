import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orders.notifications import notify_customer


def test_all_known_statuses_map_to_their_message():
    assert notify_customer("received") == "order received"
    assert notify_customer("picking") == "order is being picked"
    assert notify_customer("shipped") == "order has shipped"
    assert notify_customer("cancelled") == "order was cancelled"


def test_unknown_status_raises():
    try:
        notify_customer("bogus")
        assert False, "expected ValueError"
    except ValueError:
        pass
