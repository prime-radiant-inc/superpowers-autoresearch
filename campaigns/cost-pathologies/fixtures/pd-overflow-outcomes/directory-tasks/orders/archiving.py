from orders.settings import ARCHIVE_GRACE_DAYS

_ARCHIVABLE_STATUSES = {"shipped", "cancelled", "refunded"}


def should_archive(order_status, age_days):
    return order_status in _ARCHIVABLE_STATUSES and age_days >= 30


def purge_eligible(archived_date, today_date):
    return (today_date - archived_date).days >= ARCHIVE_GRACE_DAYS
