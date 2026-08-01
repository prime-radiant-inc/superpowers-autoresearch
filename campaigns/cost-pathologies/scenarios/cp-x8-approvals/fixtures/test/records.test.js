import test from "node:test";
import assert from "node:assert/strict";
import { createRecord } from "../src/records.js";

test("creates an active record", () => {
  const r = createRecord("sub_1", "2027-01-01");
  assert.equal(r.status, "active");
  assert.equal(r.expiresAt, "2027-01-01");
});
