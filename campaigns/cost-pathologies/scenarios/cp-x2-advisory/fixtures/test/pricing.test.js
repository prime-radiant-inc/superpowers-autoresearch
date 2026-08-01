import test from "node:test";
import assert from "node:assert/strict";
import { computeTotal } from "../src/pricing.js";

test("sums item prices by quantity", () => {
  const total = computeTotal([
    { priceCents: 500, qty: 2 },
    { priceCents: 150, qty: 1 },
  ]);
  assert.equal(total, 1150);
});
