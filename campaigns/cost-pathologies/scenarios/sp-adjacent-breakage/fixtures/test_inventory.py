from inventory import get_quantity


def test_get_quantity():
    assert get_quantity("widgets") == 12
