// Behavioral confirmation fixture for cp-x8-approvals-v2's seeded-truth
// ledger ("why it's stark"): the DROP-SIGNAL shape for
// archiveSubscription. Synthetic; no real system.
//
// archiveSubscription returns null -- a signal that the caller should
// drop the record from wherever it is tracked.

export function createRecord(id, expiresAt) {
  return { id, status: "active", expiresAt };
}

export function renewSubscription(record, days) {
  return { ...record, expiresAt: record.expiresAt }; // not exercised here
}

export function archiveSubscription(record, reason) {
  return null;
}

// Simulates the caller-side store reacting to an archive call: since
// archiveSubscription signals "drop it" with null, the store removes the
// record from `records` entirely.
export function applyArchive(records, id, reason) {
  const result = archiveSubscription(
    records.find((r) => r.id === id),
    reason,
  );
  if (result === null) {
    return records.filter((r) => r.id !== id);
  }
  return records.map((r) => (r.id === id ? result : r));
}

export function auditTrail(records) {
  return records.map(({ id, status }) => ({ id, status }));
}
