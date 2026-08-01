import test from "node:test";
import assert from "node:assert/strict";
import { isEven } from "../util/isEven.js";

test("recognizes an even number", () => {
  assert.equal(isEven(4), true);
});

test("recognizes an odd number", () => {
  assert.equal(isEven(3), false);
});
