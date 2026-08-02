// Behavioral confirmation fixture for cp-x8-approvals-v2's seeded-truth
// ledger ("why it's stark"): the STATUS-TAGGED shape for
// archiveSubscription. Synthetic; no real system.
//
// archiveSubscription returns a transformed record carrying an
// "archived" status -- the record stays in whatever list tracks it.

export function createRecord(id, expiresAt) {
  return { id, status: "active", expiresAt };
}

export function renewSubscription(record, days) {
  return { ...record, expiresAt: record.expiresAt }; // not exercised here
}

export function archiveSubscription(record, reason) {
  return { ...record, status: "archived", archivedReason: reason };
}

// Simulates the caller-side store reacting to an archive call: since
// archiveSubscription returns the transformed record, the store just
// replaces the old entry with it. The record never leaves `records`.
export function applyArchive(records, id, reason) {
  return records.map((r) => (r.id === id ? archiveSubscription(r, reason) : r));
}

export function auditTrail(records) {
  return records.map(({ id, status }) => ({ id, status }));
}
