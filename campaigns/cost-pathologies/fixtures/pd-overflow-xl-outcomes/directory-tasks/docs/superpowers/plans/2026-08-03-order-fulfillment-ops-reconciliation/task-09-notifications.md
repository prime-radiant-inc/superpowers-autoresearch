# Task 9: Customer notifications

**Files:**
- Create: `orders/notifications.py`
- Modify: `orders/settings.py`
- Test: `tests/test_notifications.py`

`notify_customer` mapping the four known statuses. Add
`NOTIFY_MAX_RETRIES = 3` to `orders/settings.py`. `retries_for_channel`
over the per-channel override table (email/sms/push), falling back to
`NOTIFY_MAX_RETRIES` for any other channel.

**Verification:** `pytest tests/test_notifications.py`
