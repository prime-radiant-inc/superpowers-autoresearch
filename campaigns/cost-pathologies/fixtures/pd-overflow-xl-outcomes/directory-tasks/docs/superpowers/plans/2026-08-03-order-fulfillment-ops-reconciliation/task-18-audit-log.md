# Task 18: Audit log

**Files:**
- Create: `orders/audit_log.py`
- Modify: `orders/settings.py`
- Test: `tests/test_audit_log.py`

`AUDIT_EVENT_SEVERITY`, `classify_audit_event`. Add
`AUDIT_LOG_RETENTION_DAYS = 90` to `orders/settings.py`.
`is_within_retention`.

**Verification:** `pytest tests/test_audit_log.py`
