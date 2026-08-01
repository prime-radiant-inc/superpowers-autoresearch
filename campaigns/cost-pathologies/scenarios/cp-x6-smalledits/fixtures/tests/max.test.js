import test from "node:test";
import assert from "node:assert/strict";
import { max } from "../util/max.js";

test("finds the max of an all-negative list", () => {
  assert.equal(max([-5, -1, -9]), -1);
});
