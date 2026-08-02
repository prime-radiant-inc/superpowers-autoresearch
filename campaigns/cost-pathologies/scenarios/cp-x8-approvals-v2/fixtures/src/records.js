// Subscription record helpers. Synthetic fixture.
export function createRecord(id, expiresAt) {
  return { id, status: "active", expiresAt };
}
