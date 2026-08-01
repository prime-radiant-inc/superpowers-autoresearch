import test from "node:test";
import assert from "node:assert/strict";
import { formatPrice } from "../src/format.js";

test("formats whole dollars", () => {
  assert.equal(formatPrice(1200), "$12.00");
});

test("pads single-digit cents", () => {
  assert.equal(formatPrice(105), "$1.05");
});
