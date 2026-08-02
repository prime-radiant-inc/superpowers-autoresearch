import test from "node:test";
import assert from "node:assert/strict";
import { sum } from "../util/sum.js";

test("sums an empty array to 0", () => {
  assert.equal(sum([]), 0);
});

test("sums a list of numbers", () => {
  assert.equal(sum([1, 2, 3]), 6);
});
