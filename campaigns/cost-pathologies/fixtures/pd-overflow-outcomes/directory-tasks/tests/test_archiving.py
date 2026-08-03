import datetime

from orders.archiving import should_archive, purge_eligible


def test_archivable_statuses():
    assert should_archive("shipped", 30) is True
    assert should_archive("cancelled", 30) is True
    assert should_archive("refunded", 30) is True
    assert should_archive("picking", 30) is False
    assert should_archive("shipped", 10) is False


def test_purge_eligible_after_grace_window():
    assert purge_eligible(datetime.date(2026, 1, 1), datetime.date(2026, 1, 8)) is True


def test_purge_not_eligible_before_grace_window():
    assert purge_eligible(datetime.date(2026, 1, 1), datetime.date(2026, 1, 4)) is False
